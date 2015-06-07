import mock

from seedbox import cli
from seedbox import db
from seedbox.tests import test


class CliTestCase(test.ConfiguredBaseTestCase):

    @mock.patch.object(db, '_DBAPI')
    @mock.patch.object(cli.service, 'prepare_service')
    def test_cli(self, mock_db, mock_service):
        self.assertIsNone(cli.main())
