import os

from seedbox import cli
from seedbox import db
from seedbox.tests import test


class FakeOptions(object):

    @staticmethod
    def initialize(args):
        pass


class CliTestCase(test.ConfiguredBaseTestCase):

    def test_cli(self):
        self.patch(db, '_DBAPI', None)
        self.patch(cli, 'options', FakeOptions)
        cli.main()
        self.assertTrue(True)

    def test_cli_lock_timeout(self):
        self.patch(db, '_DBAPI', None)
        self.patch(cli, 'options', FakeOptions)
        with open(os.path.join(self.CONF.config_dir, 'seedmgr.lock'), 'w'):
            cli.main()

        self.assertTrue(True)
