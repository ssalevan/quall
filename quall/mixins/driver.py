# -*- coding: utf-8 -*-
"""
    quall.mixins.selenium
    ~~~~~~~~~~~~~~~~~~~~~

    Provides Selenium client functionality.

    Example::
      
"""


import selenium

from selenium import webdriver


class SeleniumMixin(object):

  DEFAULT_DRIVER = "Chrome"
  DEFAULT_DESIRED_CAPABILITIES = "CHROME"
  DEFAULT_COMMAND_EXECUTOR = "http://localhost"

  config = {'selenium':{}}

  def with_driver(fn):
    def new_fn():
      if self.driver == None:
        self.start_driver()
      fn()
    return new_fn

  def start_driver(self):
    driver_class = getattr(selenium.webdriver,
        self.config["selenium"].get("driver", self.DEFAULT_DRIVER))
    desired_capabilities = getattr(
        selenium.webdriver.common.desired_capabilities.DesiredCapabilities,
        self.config["selenium"].get("desired_capabilities_base",
            self.DEFAULT_DESIRED_CAPABILITIES))
    command_executor = self.config["selenium"].get("command_executor",
        self.DEFAULT_COMMAND_EXECUTOR)
    self.log.info(
        "Starting WebDriver with capabilities: %s" % desired_capabilities_base)
    if self.config["selenium"].has_key("desired_capabilities"):
      for key in self.config["selenium"]["desired_capabilities"].keys():
        capability = self.config["selenium"]["desired_capabilities"][key]
        desired_capabilities[key] = capability
    self.driver = driver_class(
        desired_capabilities = desired_capabilities,
        command_executor = command_executor)
    self.driver.implicitly_wait(30)
    self.log.info("WebDriver successfully started.")

  @with_driver
  def go(self, url):
    self.log.info("Opening URL: %s" % url)
    self.driver.get(url)
