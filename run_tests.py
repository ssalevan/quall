from quall.base import QuallBase

class MainClass(QuallBase):

    def run_tests(self):
        from proboscis import TestProgram
        from tests import *

        TestProgram().run_and_exit()


if __name__ == '__main__':
    m = MainClass()
    m.run_tests()
