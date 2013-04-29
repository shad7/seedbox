#!/usr/bin/env python

from distutils.core import setup

setup(name='SeedboxManager',
      version='0.1',
      description='Provides framework for performing tasks on a seedbox',
      author='shad7',
      author_email='kenny.shad7@gmail.com',
      url='TBD',
      packages=['seedbox', 'seedbox.model', 'seedbox.tasks'],
      package_dir={'seedbox': 'src/seedbox'},
      requires=['sqlobject (>=1.3.2)',
                'xworkflows (>=0.4.1)',
                'rarfile (>=2.6)',
                'sqlite3'],
    )
