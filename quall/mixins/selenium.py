# -*- coding: utf-8 -*-
"""
    quall.mixins.selenium
    ~~~~~~~~~~~~~~~~~~~~~

    Provides Selenium client functionality.

    Example::
      self.ssh_command("some.domain.tld", "ls -lah")
      self.forward_port_to_local("some.domain.tld", 80)
      self.send_local_file("some.domain.tld", "./hosts", "/etc/hosts")
"""