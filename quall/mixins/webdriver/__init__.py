# -*- coding: utf-8 -*-
"""
    quall.mixins.webdriver
    ~~~~~~~~~~~~~~~~~~~~~~

    Provides WebDriver client functionality.

    Example::
      
"""


import shutil
import tempfile
import traceback
import urllib2

import selenium

import quall.exceptions


class SeleniumException(quall.exceptions.QuallException):
  pass


class SeleniumDownloadException(SeleniumException):
  pass


class WebDriverMixin(WebDriverAbstractions):

  DEFAULT_COMMAND_EXECUTOR = "http://localhost"
  DEFAULT_DESIRED_CAPABILITIES = "CHROME"
  DEFAULT_DRIVER = "Chrome"
  DEFAULT_SELENIUM_URL = "http://selenium.googlecode.com/files/selenium-server-standalone-2.28.0.jar"

  def with_driver(fn):
    def new_fn():
      if self.driver == None:
        self.start_driver()
      fn()
    return new_fn

  def download_selenium(self):
    self.temp_dir = tempfile.mkdtemp()
    self.selenium_location = "%s/selenium.jar" % self.temp_dir
    selenium_file = None
    selenium_to_retrieve = None
    try:
      selenium_file = open(self.selenium_location, "wb")
      selenium_url = self.config["webdriver"].get("selenium_url",
          DEFAULT_SELENIUM_URL)
      self.log.info("Retrieving Selenium from %s" % selenium_url)
      selenium_to_retrieve = urllib2.urlopen(selenium_url)
      cur_chunk = selenium_to_retrieve.read(1024)
      while cur_chunk != "":
        selenium_file.write(cur_chunk)
        cur_chunk = selenium_to_retrieve.read(1024)
    except Exception:
      raise SeleniumDownloadException(
          "Failed to download Selenium:\n%s" % traceback.format_exc())
    finally:
      if selenium_file is not None:
        selenium_file.close()
      if selenium_to_retrieve is not None:
        selenium_to_retrieve.close()

  def start_selenium(self):
    selenium_args = self.config["webdriver"].get("selenium_args", "")
    self.selenium_port = int(self.config["webdriver"].get("selenium_port",
        self.get_free_port()))
    self.selenium_process = self.run_command(
        "%s %s -port %s" % (self.selenium_process, selenium_args,
            self.selenium_port), background = True)

  def start_driver(self):
    # Downloads Selenium if configured to do so.
    if self.config["webdriver"].get("download_selenium", False):
      self.download_selenium()
    else:
      self.selenium_location = self.config["webdriver"]["selenium_location"]
    # Starts Selenium if configured to do so.
    if self.config["webdriver"].get("start_selenium", False):
      self.start_selenium()
    else:
      self.selenium_process = None
    # Obtains the requested driver and base desired driver capabilities.
    driver_class = getattr(selenium.webdriver,
        self.config["webdriver"].get("driver", self.DEFAULT_DRIVER))
    desired_capabilities = getattr(
        selenium.webdriver.common.desired_capabilities.DesiredCapabilities,
        self.config["webdriver"].get("desired_capabilities_base",
            self.DEFAULT_DESIRED_CAPABILITIES))
    command_executor = self.config["webdriver"].get("command_executor",
        self.DEFAULT_COMMAND_EXECUTOR)
    self.log.info(
        "Starting WebDriver with capabilities: %s" % desired_capabilities_base)
    # Overrides base driver capabilities with those specified in configuration.
    if self.config["webdriver"].has_key("desired_capabilities"):
      for key in self.config["webdriver"]["desired_capabilities"].keys():
        capability = self.config["webdriver"]["desired_capabilities"][key]
        desired_capabilities[key] = capability
    # Instantiates WebDriver client connection.
    self.driver = driver_class(
        desired_capabilities = desired_capabilities,
        command_executor = command_executor)
    self.driver.implicitly_wait(30)
    self.log.info("WebDriver successfully started.")

  def stop_driver(self):
    # Ends the WebDriver session.
    if "driver" in dir(self):
      if self.driver is not None:
        self.log.info("Ending WebDriver session...")
        driver.quit()
    # If Selenium process is active, terminates it.
    if "selenium_process" in dir(self):
      if self.selenium_process is not None:
        self.log.info("Terminating Selenium process...")
        self.selenium_process.terminate()
        self.sleep(30)
        if not self.selenium_process.poll():
          self.log.info("Killing Selenium process...")
          self.selenium_process.kill()

  def webdriver_cleanup(self):
    self.stop_driver()
    if "temp_dir" in dir(self):
      self.log.debug("Removing temp dir: %s" % self.temp_dir)
      shutil.rmtree(self.temp_dir)

  @with_driver
  def go(self, url):
    self.log.info("Opening URL: %s" % url)
    self.driver.get(url)
