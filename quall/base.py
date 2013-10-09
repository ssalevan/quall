# -*- coding: utf-8 -*-
"""
    quall.base
    ~~~~~~~~~~

    Contains the base class for all derived test frameworks.
"""


import logging
import optparse
import os
import proboscis
import socket
import subprocess
import sys
import time
import traceback
import yaml

try:
  from yaml import CLoader as Loader
except ImportError:
  from yaml import Loader


LOG_FORMAT = "%(asctime)s|%(name)s|%(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

class QuallBase(object):

  CONFIG_FILE = "%s/config/base_config.yml" % os.getcwd()

  def __init__(self):

    #super(QuallBase, self).__init__()
    self.log = logging.getLogger("quall.base")
    pass

  def cfg(self, section, var):
    return self.config[section][var]

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
      print "Loading harness config at %s" % self.options.config_file
      cfg_file = open(self.options.config_file, 'r')
      self.config = yaml.load(cfg_file,
                    Loader = Loader)[self.options.environment]
    except Exception:
      sys.stderr.write(
          "FATAL: Unable to read config file: %s\n" % self.options.config_file)
      sys.stderr.write("%s\n" % traceback.format_exc())
      sys.stderr.flush()
      sys.exit(-1)

  def run_command(self, command, background = False, shell = True):
    self.log.info("Running local command: %s" % command)
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = shell)
    if background:
      return process
    (stdout, stderr) = process.communicate()
    self.log.info("Return code: %s" % process.returncode)
    self.log.info("Stdout: %s" % stdout)
    self.log.info("Stderr: %s" % stderr)
    return (process.returncode, stdout, stderr)

  def sleep(self, seconds):
    self.log.info("Sleeping for %s seconds..." % seconds)
    time.sleep(seconds)

  def launch(self):
    # Parses command-line options.
    parser = optparse.OptionParser()
    parser.add_option("-e", "--env", dest = "environment",
        help = "harness config environment to test with", metavar = "ENV",
        default = "default")
    parser.add_option("-c", "--config", dest = "config_file",
        help = "path to a configuration YAML file", metavar = "CFG_FILE",
        default = self.CONFIG_FILE)
    parser.add_option("-g", "--group", dest = "groups",
        help = "a comma-separated list of Proboscis test groups to run",
        metavar = "PROBOSCIS_GROUPS", default = "all")
    (self.options, args) = parser.parse_args()
    print self.options
    # Loads environment-wise harness configuration from configuration file.
    self.load_config()
    # Runs all configured tests.
    #proboscis.TestProgram(
    #  groups = self.options.groups.strip().split(","),
    #  argv = []
    #).run_and_exit()
