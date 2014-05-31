import uuid

import sqlalchemy as sa
import testtools

from seedbox.db import exception
from seedbox.db.sqlalchemy import migration
from seedbox.db.sqlalchemy import session
from seedbox.tests import test


class DBMigrationTestCase(test.BaseTestCase):

    def setUp(self):
        super(DBMigrationTestCase, self).setUp()

    def test_db_version(self):
        dbname = 'sqlite:////tmp/' + str(uuid.uuid4()) + '.db'
        self.facade = session.EngineFacade(dbname)

        ver = migration.db_version(self.facade.engine)
        self.assertEqual(ver, 0)

    def test_db_sync(self):
        dbname = 'sqlite:////tmp/' + str(uuid.uuid4()) + '.db'
        self.facade = session.EngineFacade(dbname)

        migration.db_sync(self.facade.engine)
        ver = migration.db_version(self.facade.engine)
        self.assertEqual(ver, 3)

    def test_db_sync_bad_version(self):
        dbname = 'sqlite:////tmp/' + str(uuid.uuid4()) + '.db'
        self.facade = session.EngineFacade(dbname)

        with testtools.ExpectedException(exception.DbMigrationError):
            migration.db_sync(self.facade.engine, 'x')

    def test_db_sync_downgrade(self):
        dbname = 'sqlite:////tmp/' + str(uuid.uuid4()) + '.db'
        self.facade = session.EngineFacade(dbname)

        migration.db_sync(self.facade.engine)
        migration.db_sync(self.facade.engine, 2)
        ver = migration.db_version(self.facade.engine)
        self.assertEqual(ver, 2)
        migration.db_sync(self.facade.engine, 1)
        ver = migration.db_version(self.facade.engine)
        self.assertEqual(ver, 1)

        with testtools.ExpectedException(NotImplementedError):
            migration.db_sync(self.facade.engine, 0)

    def test_db_sync_v1_to_v2(self):
        dbname = 'sqlite:////tmp/' + str(uuid.uuid4()) + '.db'
        self.facade = session.EngineFacade(dbname)

        migration.db_sync(self.facade.engine, 1)

        meta = sa.MetaData(bind=self.facade.engine)

        v1_appstate = sa.Table('app_state', meta, autoload=True)
        data = {
            'name': 'test',
            'val_str': 'sample'
            }
        v1_appstate.insert().values(**data).execute()

        v1_torrent = sa.Table('torrent', meta, autoload=True)
        data = {
            'name': 'test_torrent.torrent'
            }
        v1_torrent.insert().values(**data).execute()

        v1_media = sa.Table('media_file', meta, autoload=True)
        data = {
            'filename': 'sample.mp4',
            'file_ext': '.mp4',
            'file_path': '/tmp',
            }
        v1_media.insert().values(**data).execute()

        migration.db_sync(self.facade.engine, 2)
        ver = migration.db_version(self.facade.engine)
        self.assertEqual(ver, 2)
