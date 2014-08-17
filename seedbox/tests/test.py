# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
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

"""Common utilities used in testing"""

import os
import shutil
import tempfile

from oslo.config import fixture as config
from oslotest import base


# to avoid having to change all test code that references the base directly
# just reference the oslotest version here.
BaseTestCase = base.BaseTestCase


class ConfiguredBaseTestCase(BaseTestCase):

    def setUp(self):
        super(ConfiguredBaseTestCase, self).setUp()

        self.CONF = self.useFixture(config.Config()).conf
        self.CONF.import_group('torrent', 'seedbox.torrent')
        self.base_dir = tempfile.gettempdir()
        self.set_required_options()
        self.CONF([], project='seedbox')
        self.CONF.set_override('config_dir', self.base_dir)
        if self.base_dir != self.CONF.config_dir:
            self.CONF.set_default('config_dir', self.base_dir)

    def tearDown(self):
        shutil.rmtree(self.base_dir, ignore_errors=True)
        self.CONF.reset()
        super(ConfiguredBaseTestCase, self).tearDown()

    def _make_dir(self, dirname):
        dirpath = os.path.join(self.base_dir, dirname)
        os.mkdir(dirpath)
        return dirpath

    def set_required_options(self):

        # provide values for the required configs
        self.CONF.set_override('torrent_path',
                               self._make_dir('torrent'),
                               group='torrent')
        self.CONF.set_override('media_paths',
                               [self._make_dir('complete'),
                                self._make_dir('seedLT')],
                               group='torrent')
        self.CONF.set_override('incomplete_path',
                               self._make_dir('inprogress'),
                               group='torrent')
