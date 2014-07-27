from __future__ import print_function
from seedbox.db import models as api_model
from seedbox.db.sqlalchemy import models as db_model
from seedbox.db.sqlalchemy import api
from seedbox.tests import test


class SAApiTestCase(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(SAApiTestCase, self).setUp()

        self.dbconn = api.Connection(self.CONF)

    def _print_tables(self, msg_key):

        for t, tab in db_model.Base.metadata.tables.items():
            print(msg_key, 'table =>', t, tab.c)

    def test_upgrade(self):
        try:
            self.dbconn.upgrade()
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_clear(self):
        self.dbconn.clear()
        self.assertTrue(True)

    def test_backup(self):
        self.dbconn.backup()
        self.assertTrue(True)

    def test_shrink_db(self):
        self.dbconn.shrink_db()
        self.assertTrue(True)

    def test_save(self):

        torrent = api_model.Torrent(torrent_id=None, name='fake1.torrent')
        self.assertIsInstance(torrent, api_model.Torrent)

        _saved_torrent = self.dbconn.save(torrent)
        self.assertIsInstance(_saved_torrent, api_model.Torrent)

        self.assertIsNone(torrent.created_at)
        self.assertIsNotNone(_saved_torrent.created_at)

        _saved_torrent.state = 'active'
        torrent = self.dbconn.save(_saved_torrent)
        # self.assertIsNotNone(torrent.updated_at)
        self.assertIsNone(_saved_torrent.updated_at)

    def test_bulk_create(self):

        torrent = api_model.Torrent(torrent_id=None, name='fake2.torrent')
        torrent = self.dbconn.save(torrent)

        _medias = []
        for i in range(1, 11):
            media = api_model.MediaFile.make_empty()
            media.filename = 'movie-{0}.mp4'.format(i)
            media.file_ext = '.mp4'
            media.file_path = '/tmp/media'
            media.torrent_id = torrent.torrent_id
            _medias.append(media)
        _results = self.dbconn.bulk_create(_medias)
        self.assertEqual(len(list(_results)), 10)

    def test_bulk_update(self):

        torrent = api_model.Torrent(torrent_id=None, name='fake3.torrent')
        torrent = self.dbconn.save(torrent)

        _medias = []
        for i in range(1, 11):
            media = api_model.MediaFile.make_empty()
            media.filename = 'movie-{0}.mp4'.format(i)
            media.file_ext = '.mp4'
            media.file_path = '/tmp/media'
            media.torrent_id = torrent.torrent_id
            _medias.append(media)
        self.dbconn.bulk_create(_medias)

        value_map = dict(synced=True)
        qfilter = {'=': {'torrent_id': torrent.torrent_id}}
        self.dbconn.bulk_update(value_map, api_model.MediaFile, qfilter)

    def test_delete_by(self):

        torrent = api_model.Torrent(torrent_id=None, name='fake4.torrent')
        torrent = self.dbconn.save(torrent)

        _medias = []
        for i in range(1, 11):
            media = api_model.MediaFile.make_empty()
            media.filename = 'movie-{0}.mp4'.format(i)
            media.file_ext = '.mp4'
            media.file_path = '/tmp/media'
            media.torrent_id = torrent.torrent_id
            _medias.append(media)
        self.dbconn.bulk_create(_medias)

        qfilter = {'=': {'file_ext': '.mp4'}}
        self.dbconn.delete_by(api_model.MediaFile, qfilter)

    def test_delete(self):

        torrent = api_model.Torrent(torrent_id=None, name='fake5.torrent')
        torrent = self.dbconn.save(torrent)

        self.dbconn.delete(torrent)
        self.assertIsNone(
            self.dbconn.fetch(api_model.Torrent, torrent.torrent_id))

        self.dbconn.delete(
            api_model.Torrent(torrent_id=1000, name='fakeX.torrent'))

    def test_fetch_by(self):

        torrent = api_model.Torrent(torrent_id=None, name='fake6.torrent')
        torrent = self.dbconn.save(torrent)

        qfilter = {'=': {'name': 'fake6.torrent'}}
        _torrent = self.dbconn.fetch_by(api_model.Torrent, qfilter)
        self.assertEqual(torrent, list(_torrent)[0])
