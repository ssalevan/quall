import sys
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(name = "quall",
      version = "0.1",
      description = "Functional test framework builder",
      author = "James Molet",
      author_email = "jmolet@redhat.com",
      url = "https://github.com/Lorquas/quall/",
      packages = [ 'quall' ],
      license = 'LGPL',
      platforms = 'Posix; MacOS X; Windows',
      classifiers = [ 'Development Status :: 1 - Planning',
                      'Intended Audience :: Developers',
                      'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                      'Operating System :: OS Independent' ],
      long_description = "Provides rudiments for building a functional test framework"
      )