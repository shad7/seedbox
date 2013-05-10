#!/usr/bin/env python

import os, re, sys

# make sure setuptools are available
from ez_setup import use_setuptools
use_setuptools()

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        # because we are using sys.argv for testing our options
        # module, and by passing in 'test' or other inputs; we need
        # to reduce to what we are able to process so pop!
        sys.argv.pop()
        errno = pytest.main(self.test_args)
        sys.exit(errno)

PKG_DIR='src'

# handle dynamically getting the version
# for our application
VERFILE = os.path.join(PKG_DIR, 'seedbox', '_version.py')
verstr = 'unknown'
try:
    verstrline = open(VERFILE, 'rt').read()
except EnvironmentError as err:
    pass    # file is missing
else:
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        raise RuntimeError('if {0} exists, it is required to be well-formed'.format(VERFILE))

# generate a list of required components
required = []
required.append('SQLObject >= 1.3.2')
required.append('xworkflows')
required.append('rarfile >= 2.6')

data_files = ['LICENSE', 'README', 'README.md']

setup(
      name='SeedboxManager',
      version=verstr,
      description='Provides framework for performing tasks on a seedbox',
      author='shad7',
      author_email='kenny.shad7@gmail.com',
      url='TBD',
      license='MIT',
      packages=find_packages(PKG_DIR),
      package_dir={'': PKG_DIR},
      data_files=data_files,
      install_requires=required,
      entry_points={ 'console_scripts': ['seedmgr = seedbox.manager:main'] },
      zip_safe=False,
      tests_require=['pytest'],
      cmdclass = {'test': PyTest},
)

