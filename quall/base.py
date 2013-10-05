#!/usr/bin/python
# Contains base

import os
import socket
import sys
import traceback
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import quall.mixins.ssh


class QuallBase(quall.mixins.ssh.SSHMixin):

  CONFIG_FILE = "%s/config/base_config.yml" % os.getcwd()

  def __init__(self):
    self.load_config()

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
      self.config = yaml.load(cfg_file, Loader=Loader)
    except Exception:
      sys.stderr.write(
          "FATAL: Unable to read config file: %s\n" % self.CONFIG_FILE)
      sys.stderr.write("%s\n" % traceback.format_exc())
      sys.stderr.flush()
      sys.exit(-1)
