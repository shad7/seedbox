import mock

from seedbox import cli
from seedbox import db
from seedbox.tests import test


class CliTestCase(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(CliTestCase, self).setUp()

        self.patch(db, '_DBAPI', {})

    @mock.patch('seedbox.service.prepare_service')
    def test_cli(self, mock_service):
        self.assertIsNone(cli.main())
