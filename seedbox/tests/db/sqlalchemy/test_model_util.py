from seedbox.db import models as api_model
from seedbox.db.sqlalchemy import models as db_model
from seedbox.db.sqlalchemy import model_util
from seedbox.db.sqlalchemy import session
from seedbox.tests import test


class ModelUtilTestCase(test.BaseTestCase):

    def setUp(self):
        super(ModelUtilTestCase, self).setUp()

        self.facade = session.EngineFacade('sqlite:///:memory:')
        db_model.verify_tables(self.facade.engine)

    def tearDown(self):
        db_model.purge_all_tables(self.facade.engine)
        super(ModelUtilTestCase, self).tearDown()

    def test_from_db(self):
        self.assertIsNone(model_util.from_db(None))

        _tor = db_model.Torrent()
        _tor['name'] = 'fake.torrent'

        _pub_tor = model_util.from_db(_tor)
        self.assertIsInstance(_pub_tor, api_model.Torrent)

        _mf = db_model.MediaFile()
        _mf['filename'] = 'media.mp4'
        _mf['file_ext'] = '.mp4'
        _mf['torrent_id'] = _tor.id

        _pub_mf = model_util.from_db(_mf)
        self.assertIsInstance(_pub_mf, api_model.MediaFile)

    def test_to_db(self):
        self.assertIsNone(model_util.to_db(None))

        _tor = api_model.Torrent.make_empty()
        _tor.torrent_id = 1
        _tor.name = 'fake.torrent'

        _db_tor = model_util.to_db(_tor)
        self.assertIsInstance(_db_tor, db_model.Torrent)

        _mf = api_model.MediaFile.make_empty()
        _mf.media_id = 1
        _mf.filename = 'media.mp4'
        _mf.file_ext = '.mp4'
        _mf.torrent_id = _tor.torrent_id

        _tor.media_files = [_mf]

        _db_tor = model_util.to_db(_tor)
        self.assertIsInstance(_db_tor, db_model.Torrent)
