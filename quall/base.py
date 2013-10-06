# -*- coding: utf-8 -*-
"""
    quall.base
    ~~~~~~~~~~

    Contains the base class for all derived test frameworks.
"""


import os
import socket
import subprocess
import sys
import traceback
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class QuallBase(object):

  CONFIG_FILE = "%s/config/base_config.yml" % os.getcwd()

  def __init__(self):
    self.load_config()
    #super()

  def get_free_port(self):
    sock = None
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.bind(("", 0))
      return sock.getsockname()[1]
    finally:
      if sock is not None:
        sock.close()

  def load_config(self):
    try:
      cfg_file = open(self.CONFIG_FILE, 'r')
      self.config = yaml.load(cfg_file, Loader=Loader)["default"]
    except Exception:
      sys.stderr.write(
          "FATAL: Unable to read config file: %s\n" % self.CONFIG_FILE)
      sys.stderr.write("%s\n" % traceback.format_exc())
      sys.stderr.flush()
      sys.exit(-1)

  def run_command(self, command, background = False, shell = True):
    self.log.info("Running local command: %s..." % command)
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = shell)
    if background:
      return process
    (stdout, stderr) = process.communicate()
    log.info("Return code: %s" % process.returncode)
    log.info("Stdout: %s" % stdout)
    log.info("Stderr: %s" % stderr)
    return (p.returncode, stdout, stderr)
