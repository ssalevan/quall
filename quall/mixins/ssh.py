# -*- coding: utf-8 -*-
"""
    quall.mixins.ssh
    ~~~~~~~~~~~~~~~~

    Provides SSH client functionality.

    Example::
      self.run_command("some.domain.tld", "ls -lah")
      self.forward_port_to_local("some.domain.tld", 80)
      self.send_local_file("some.domain.tld", "./hosts", "/etc/hosts")

"""


import base64
import binascii
import os
import socket
import traceback

import paramiko

import quall.exceptions


class SSHException(quall.exceptions.QuallException):
  pass


class SFTPException(SSHException):
  pass

class SSHAuthenticationException(SSHException):
  pass


class SSHTimeoutException(SSHException):
  pass


class SSHHostKeyException(SSHException):
  pass


class SSHHostKeyChangedException(SSHHostKeyException):
  pass


class SSHHostKeyUnknownException(SSHHostKeyException):
  pass


class SSHClientMixin(object):

  DEFAULT_KNOWN_HOSTS_PATH = os.path.join(
      os.environ["HOME"], ".ssh", "known_hosts")
  DEFAULT_PRIVATE_KEY_TYPE = "rsa"
  DEFAULT_RSA_KEY_PATH = os.path.join(os.environ['HOME'], ".ssh", "id_rsa")
  DEFAULT_DSA_KEY_PATH = os.path.join(os.environ['HOME'], ".ssh", "id_dsa")

  def _authenticate_ssh_transport(self, transport, username, password):
    # If configured to use the SSH agent, tries agent keys.
    if self._try_agent_authentication(transport, username):
      return
    # Next, attempts SSH key authentication.
    if self._try_key_authentication(transport, username, password):
      return
    # Finally, attempts password authentication.
    if self._try_password_authentication(transport, username, password):
      return
    raise SSHAuthenticationException(
        "Unable to authenticate to %s using any methods" % transport)

  def _check_host_keys(self, transport, hostname):
    known_hosts_path = self.config["ssh"].get(
        "known_hosts_path", DEFAULT_KNOWN_HOSTS_PATH)
    known_hosts_keys = paramiko.util.load_host_keys(
        os.path.expanduser(known_hosts_path))
    remote_key = transport.get_remote_server_key()
    if not known_hosts_keys.has_key(hostname):
      raise SSHHostKeyUnknownException(
          "Unknown host key %s for hostname %s" % (remote_key, hostname))
    if not known_hosts_keys[hostname].has_key(remote_key.get_name()):
      raise SSHHostKeyUnknownException(
          "Unknown host key %s for hostname %s" % (remote_key, hostname))
    if not known_hosts_keys[hostname][remote_key.get_name()] != remote_key:
      raise SSHHostKeyChangedException(
          "Host key has changed for hostname %s; expected %s, "
          "got %s" % (hostname, 
              known_hosts_keys[hostname][remote_key.get_name()], remote_key))

  def _try_agent_authentication(self, transport, username):
    if self.config["ssh"].get("use_ssh_agent", False):
      self.log.debug("Trying SSH agent auth to %s" % transport)
      agent = paramiko.Agent()
      agent_keys = agent.get_keys()
      for key in agent_keys:
        key_fingerprint = binascii.hexlify(key.get_fingerprint())
        try:
          self.log.debug(
              "Trying agent key: %s" % key_fingerprint)
          transport.auth_publickey(username, key)
          return True
        except paramiko.SSHException:
          self.log.debug(
              "Agent key %s failed to authenticate" % key_fingerprint)
      self.log.debug("Failed to authenticate with SSH agent")
    return False

  def _try_key_authentication(self, transport, username, password):
    private_key_type = self.config["ssh"].get("key_type",
        DEFAULT_PRIVATE_KEY_TYPE).lower()
    private_key_password = self.config["ssh"].get("key_password",
        password)
    key = None
    if "rsa" in private_key_type:
      rsa_key_path = self.config["ssh"].get("key_path", DEFAULT_RSA_KEY_PATH)
      rsa_key_path = os.path.expanduser(rsa_key_path)
      self.log.debug("Trying RSA key authentication from: %s" % rsa_key_path)
      try:
        key = paramiko.RSAKey.from_private_key_file(rsa_key_path)
      except paramiko.PasswordRequiredException:
        try:
          key = paramiko.RSAKey.from_private_key_file(rsa_key_path,
              private_key_password)
        except paramiko.SSHException:
          self.log.debug("Unable to decrypt RSA key: %s" % rsa_key_path)
    elif "dsa" in private_key_type:
      dsa_key_path = self.config["ssh"].get("key_path", DEFAULT_DSA_KEY_PATH)
      dsa_key_path = os.path.expanduser(dsa_key_path)
      self.log.debug("Trying DSA key authentication from %s" % dsa_key_path)
      try:
        key = paramiko.DSSKey.from_private_key_file(dsa_key_path)
      except paramiko.PasswordRequiredException:
        try:
          key = paramiko.DSSKey.from_private_key_file(dsa_key_path,
              private_key_password)
        except paramiko.SSHException:
          self.log.debug("Unable to decrypt DSA key: %s" % dsa_key_path)
    if key is not None:
      try:
        transport.auth_publickey(username, key)
        return True
      except paramiko.AuthenticationException:
        self.log.debug(
            "Failed to authenticate with key:\n%s" % traceback.format_exc())
    return False

  def _try_password_authentication(self, transport, username, password):
    try:
      transport.auth_password(username, password)
      return True
    except paramiko.AuthenticationException:
      self.log.debug(
          "Failed to authenticate with password:\n%s" % traceback.format_exc())
    return False

  def get_sftp_client(self, hostname, username = "root", password = None,
      ssh_port = 22):
    return paramiko.SFTPClient.from_transport(
        get_ssh_transport(hostname, username, password, port))

  def get_ssh_transport(self, hostname, username = "root", password = None,
      ssh_port = 22):
    self.log.debug("Opening SSH connection to %s@%s" % (username, hostname))
    # Opens a socket to the remote host's SSH port.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, ssh_port))
    # Opens an SSH session against the SSH socket.
    transport = paramiko.Transport(sock)
    transport.start_client()
    # Checks known hosts if requested to do so.
    if (self.config["ssh"].get("check_host_keys", False)):
      self._check_host_keys(transport, hostname)
    # Authenticates SSH connection.
    self._authenticate_ssh_transport(transport, username, password)
    self.log.debug(
        "Successfully authenticated to %s@%s" % (username, hostname))
    return transport

  def run_command(self, hostname, command, username = "root", password = None,
      ssh_port = 22, shell = False, get_pty = False, combine_stderr = False,
      timeout = None):
    channel = None
    transport = None
    try:
      self.log.info(
          "Executing SSH command against %s@%s: %s" % (username, hostname,
              command))
      transport = get_ssh_transport(hostname, username, password)
      channel = transport.open_session()
      # Starts a pseudo-terminal on the remote host if desired.
      if get_pty:
        channel.get_pty()
      # Invokes a shell on the remote host if desired.
      if shell:
        channel.invoke_shell()
      # Combines stderr into stdout stream if desired.
      if combine_stderr:
        channel.set_combine_stderr(combine_stderr)
      # Sets a timeout on blocking operations if desired.
      if timeout is not None:
        channel.settimeout(float(timeout))
      # Finally, executes the command.
      if type(command) is list:
        channel.exec_command(" ".join(command))
      else:
        channel.exec_command(command)
      # Blocks until the remote command completes.
      stdout = channel.makefile("rb", -1)
      stderr = channel.makefile_stderr("rb", -1)
      exit_code = channel.recv_exit_status()
      # Consumes stdout/stderr streams.
      stdout_text = stdout.read()
      stderr_text = stderr.read()
      # Logs command output.
      self.log.info("Exit code: %s" % exit_code)
      self.log.info("Stdout:\n%s" % stdout_text)
      self.log.info("Stderr:\n%s" % stderr_text)
      return (exit code, stdout_text, stderr_text)
    except socket.timeout:
      raise SSHTimeoutException(
          "Reached timeout of %s seconds while executing SSH command against "
          "%s@%s: %s" % (timeout, username, hostname, command))
    except Exception:
      raise SSHException(
          "Failed to execute SSH command against %s@%s: %s\n%s" % (username,
              hostname, command, traceback.format_exc()))
    finally:
      if channel is not None:
        channel.close()
      if transport is not None:
        transport.close()

  def send_local_file(self, hostname, local_path, remote_path,
      username = "root", password = None, ssh_port = 22):
    try:
      sftp = get_sftp_client(hostname, username, password, port)
      sftp.put(local_path, remote_path)
    except paramiko.SFTPError:
      raise SFTPException(
          "Failed to send %s to %s@%s:%s\n%s" % (local_path,
              username, hostname, remote_path, traceback.format_exc()))

  def get_remote_file(self, hostname, remote_path, local_path,
      username = "root", password = None, ssh_port = 22):
    try:
      sftp = get_sftp_client(hostname, username, password, port)
      sftp.get(remote_path, local_path)
    except paramiko.SFTPError:
      raise SFTPException(
          "Failed to get %s from %s@%s:%s\n%s" % (local_path,
              username, hostname, remote_path, traceback.format_exc()))

  def get_remote_file_contents(self, hostname, remote_path,
      username = "root", password = None, ssh_port = 22):
    try:
      sftp = get_sftp_client(hostname, username, password, port)
      return sftp.open(remote_path).read()
    except paramiko.SFTPError:
      raise SFTPException(
          "Failed to get %s from %s@%s:%s\n%s" % (local_path,
              username, hostname, remote_path, traceback.format_exc()))
