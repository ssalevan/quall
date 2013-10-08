from proboscis.asserts import *
from proboscis import after_class
from proboscis import before_class
from proboscis import SkipTest
from proboscis import test


@test(groups=['example'])
class ExampleTests():
  @before_class
  def something_before(self):
    """Before class that would set up the tests in this class."""
    print "ow my balls"

  @after_class
  def something_after(self):
    """This one does cleanup."""
    print "butts"

  @test(groups=['example', 'string'])
  def check_reversed(self):
    "Checks if strings are reversed."
    orig = "hello"
    expected = "olleh"
    actual = orig[::-1]
    assert_equal(expected, actual)

  @test
  def skip_this_test(self):
    """This test skips"""
    raise SkipTest("Skipping this test!")

  @test(depends_on=[skip_this_test])
  def depend_test(self):
    """this test will skip as the test it depdns on skipped"""
    print "skipped!"
