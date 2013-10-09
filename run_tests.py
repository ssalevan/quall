from quall.base import QuallBase
from quall.mixins.ssh import SSHClientMixin
from tests import *

from proboscis import SkipTest
from proboscis import test

class MainClass(QuallBase, SSHClientMixin):
  
  def __init__(self): 
    super(MainClass, self).__init__()

  #@test(groups=['ssh'])
  def testssh(self):
    self.ssh_command("ec2-54-224-175-121.compute-1.amazonaws.com", "ls /etc", username="ec2-user")
    print self.get_remote_file_contents("ec2-54-224-175-121.compute-1.amazonaws.com", "/etc/hosts")

  def butt(self):
    pass


if __name__ == '__main__':
#  MixIn(MainClass, ssh.SSHClientMixin)
  m = MainClass()
  m.launch()
  m.testssh()
  #m.run_tests()