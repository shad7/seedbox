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

import fixtures
import testtools
import tempfile

from seedbox import options  # noqa
from seedbox import logext as logmgr  # noqa
from seedbox.fixture import config

_TRUE_VALUES = ('True', 'true', '1', 'yes')


class BaseTestCase(testtools.TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self._set_timeout()
        self._fake_output()
        self.useFixture(fixtures.FakeLogger('seedbox'))
        self.useFixture(fixtures.NestedTempfile())
        self.useFixture(fixtures.TempHomeDir())

        self.CONF = self.useFixture(config.Config()).conf
        base_dir = tempfile.gettempdir()
        self.set_required_options(base_dir)
        self.CONF([], project='seedbox')
        self.CONF.set_override('config_dir', base_dir)

    def set_required_options(self, base_dir=None):

        start_dir = base_dir
        if not start_dir:
            start_dir = tempfile.gettempdir()

        # provide values for the required configs
        self.CONF.set_override('torrent_path',
                               os.mkdir(os.path.join(start_dir, 'torrent')))
        self.CONF.set_override('media_paths',
                               [os.mkdir(os.path.join(start_dir, 'complete')),
                                os.mkdir(os.path.join(start_dir, 'seedLT'))])
        self.CONF.set_override('incomplete_path',
                               os.mkdir(os.path.join(start_dir, 'inprogress')))
        self.CONF.set_override('sync_path',
                               os.mkdir(os.path.join(start_dir, 'toSync')))

    def _set_timeout(self):
        test_timeout = os.environ.get('OS_TEST_TIMEOUT', 0)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            # If timeout value is invalid do not set a timeout.
            test_timeout = 0
        if test_timeout > 0:
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))

    def _fake_output(self):
        if os.environ.get('OS_STDOUT_CAPTURE') in _TRUE_VALUES:
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if os.environ.get('OS_STDERR_CAPTURE') in _TRUE_VALUES:
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
