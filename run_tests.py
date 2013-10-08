from quall.base import QuallBase
from tests import *

class MainClass(QuallBase):

  def run_tests(self):
    from proboscis import TestProgram        
    TestProgram().run_and_exit()


if __name__ == '__main__':
  m = MainClass()
  m.launch()
  #m.run_tests()
