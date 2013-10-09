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
    host = "ec2-54-224-175-121.compute-1.amazonaws.com"
    self.ssh_command(host, "cat /etc/anus", username="ec2-user")
    self.ssh_command(host, "wall 'i farted'", username="ec2-user")
    self.get_remote_file(host, "/etc/hosts", "/tmp/fuck", username = "ec2-user")
    self.put_remote_file(host, "/tmp/fuck", "/home/ec2-user/fuck", username = "ec2-user")
    print self.get_remote_file_contents("ec2-54-224-175-121.compute-1.amazonaws.com", "/etc/hosts", username="ec2-user")

  def butt(self):
    pass


if __name__ == '__main__':
#  MixIn(MainClass, ssh.SSHClientMixin)
  m = MainClass()
  m.launch()
  m.testssh()
  #m.run_tests()