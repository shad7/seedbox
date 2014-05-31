# -*- encoding: utf-8 -*-
#
# Copyright © 2013 Intel Corp.
#
# Author: Lianhao Lu <lianhao.lu@intel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import fixtures
import sys

from seedbox.configs import generator
from seedbox.fixture import mockpatch
from seedbox.tests import test


class GeneratorTestcase(test.BaseTestCase):
    conffiles = ['seedbox/tests/testmods/baar_baa_opt.py',
                 'seedbox/tests/testmods/bar_foo_opt.py',
                 ]

    def test_generate(self):
        stdout = self.useFixture(fixtures.StringStream('confstdout')).stream
        self.useFixture(mockpatch.Patch('sys.stdout', new=stdout))
        generator.generate(self.conffiles)
        stdout.flush()
        stdout.seek(0)
        lines = stdout.readlines()
        # Test we have group in the output
        self.assertIn('[DEFAULT]\n', lines)
        self.assertIn('[baar]\n', lines)
        self.assertIn('[bar]\n', lines)
        # Test we have opt in the output
        self.assertIn('#fooey=false\n', lines)
        self.assertIn('# **REQUIRED** number of bad items (integer value)\n',
                      lines)
        self.assertIn('#baaad=7\n', lines)
        self.assertIn('#zooey=dewey\n', lines)
        self.assertIn('#baa=<None>\n', lines)
        self.assertIn('#foo=<None>\n', lines)
        self.assertIn('#weight=1.1\n', lines)
        self.assertIn('#crazy=sample,people\n', lines)
        self.assertIn('#numbers=one.two.three.four.five.six\n', lines)
        self.assertIn('#strings=\n', lines)

    def test_main(self):
        self.patch(sys, 'argv', ['test',
                                 'seedbox/tests/testmods/baar_baa_opt.py'])
        generator.main()
        self.assertTrue(True)

    def test_import_module(self):
        mod = generator._import_module('seedbox.tests.testmods.baar_baa_opt')
        self.assertIsNotNone(mod)

        mod = generator._import_module('seedbox.tests.bar_foo_opt')
        self.assertIsNone(mod)

    def test_list_opts(self):
        mod = generator._import_module('seedbox.tests.testmods.baar_baa_opt')
        opts = generator._list_opts(mod)
        self.assertIsNotNone(opts)

    def test_gen_opts_by_group(self):
        self.assertRaises(RuntimeError, generator._gen_opts_by_group,
                          ['seedbox.tests.bar_foo_opt'], {'DEFAULT': []})
