import glob
import os

import six.moves.urllib.parse as urlparse

from seedbox import db
from seedbox.db import maintenance
from seedbox.tests import test


class DbMaintenanceTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(DbMaintenanceTest, self).setUp()

        # initialize the database and schema details.
        db.dbapi(self.CONF)

    def test_backup_database(self):

        db_name = urlparse.urlparse(
            self.CONF.database.connection).path.replace('//', '/')

        for cnt in range(0, 15):
            if cnt == 0:
                self.assertEqual(len(glob.glob(db_name+'*')), 1)
            elif 1 <= cnt <= 8:
                self.assertEqual(len(glob.glob(db_name+'*')), 1+cnt)
            else:
                self.assertEqual(len(glob.glob(db_name+'*')), 9)

            # perform backup
            maintenance.backup(self.CONF)

        if os.path.exists(db_name):
            os.remove(db_name)
        # perform backup
        maintenance.backup(self.CONF)
