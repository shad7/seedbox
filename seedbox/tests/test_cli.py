import os

from seedbox import cli
from seedbox import db
from seedbox.tests import test


class fake_options(object):

    @staticmethod
    def initialize(args):
        pass


class fake_process(object):

    @staticmethod
    def start():
        pass


class CliTestCase(test.ConfiguredBaseTestCase):

    def test_cli(self):
        self.patch(db, '_DBAPI', None)
        self.patch(cli, 'options', fake_options)
        cli.main()
        self.assertTrue(True)

    def test_cli_lock_timeout(self):
        self.patch(db, '_DBAPI', None)
        self.patch(cli, 'options', fake_options)
        with open(os.path.join(self.CONF.config_dir, 'seedmgr.lock'), 'w'):
            cli.main()

        self.assertTrue(True)
