from __future__ import print_function
import datetime
import os

from seedbox import db
from seedbox.db import models as api_model
from seedbox.tests import test


class ApiDBTestCase(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(ApiDBTestCase, self).setUp()

        self.patch(db, '_DBAPI', None)
        self.dbapi = db.dbapi(self.CONF)

    def test_clear(self):
        self.dbapi.clear()
        self.assertTrue(True)

    def test_backup(self):
        self.dbapi.backup()
        self.assertTrue(True)

    def test_shrink_db(self):
        self.dbapi.shrink_db()
        self.assertTrue(True)

    def test_save_torrent(self):

        torrent = api_model.Torrent(torrent_id=None, name='fake.torrent')
        _torrent = self.dbapi.save_torrent(torrent)
        self.assertIsNotNone(_torrent.torrent_id)

    def test_delete_torrent(self):

        torrent = api_model.Torrent(torrent_id=None, name='fake.torrent')
        _torrent = self.dbapi.save_torrent(torrent)

        self.dbapi.delete_torrent(_torrent)
        torrent = self.dbapi.get_torrent(_torrent.torrent_id)
        self.assertIsNone(torrent)

    def test_delete_torrents(self):

        torrent1 = self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='active'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='active'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake3.torrent'))

        qfilter = {'=': {'state': 'active'}}
        self.dbapi.delete_torrents(qfilter)

        self.assertIsNone(self.dbapi.get_torrent(torrent1.torrent_id))

    def test_get_torrents(self):

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='active'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='active'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake3.torrent'))

        qfilter = {'=': {'state': 'active'}}
        self.assertEqual(len(list(self.dbapi.get_torrents(qfilter))), 2)

    def test_get_torrents_active(self):

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='active'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='active'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake3.torrent'))

        self.assertEqual(len(list(self.dbapi.get_torrents_active())), 3)

    def test_get_torrents_by_state(self):

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='active'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='active'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake3.torrent'))

        self.assertEqual(
            len(list(self.dbapi.get_torrents_by_state('active'))), 2)

    def test_torrents_eligible_for_purging(self):

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='done'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='done'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake3.torrent'))

        self.assertEqual(
            len(list(self.dbapi.get_torrents_eligible_for_purging())), 2)

    def test_torrents_eligible_for_removal(self):

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='done',
                              purged=True))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='done',
                              purged=True))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake3.torrent'))

        self.assertEqual(
            len(list(self.dbapi.get_torrents_eligible_for_removal())), 2)

    def test_fetch_or_create_torrent(self):

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='done',
                              purged=True))

        self.assertIsInstance(
            self.dbapi.fetch_or_create_torrent('fake1.torrent'),
            api_model.Torrent)

        self.assertIsInstance(
            self.dbapi.fetch_or_create_torrent('fake99.torrent'),
            api_model.Torrent)

    def test_save_media(self):
        media = api_model.MediaFile(media_id=None,
                                    torrent_id=None,
                                    filename='movie-1.mp4',
                                    file_ext='.mp4',
                                    file_path='/tmp/media')
        media = self.dbapi.save_media(media)

        self.assertIsNotNone(media.media_id)

    def test_bulk_create_medias(self):

        _medias = []
        for i in range(1, 11):
            _medias.append(api_model.MediaFile(media_id=None,
                                               torrent_id=None,
                                               filename='movie-1.mp4',
                                               file_ext='.mp4',
                                               file_path='/tmp/media'))
        medias = self.dbapi.bulk_create_medias(_medias)
        self.assertEqual(len(medias), 10)
        self.assertIsInstance(medias[0], api_model.MediaFile)

    def test_delete_media(self):

        media = api_model.MediaFile(media_id=None,
                                    torrent_id=None,
                                    filename='movie-1.mp4',
                                    file_ext='.mp4',
                                    file_path='/tmp/media')
        media = self.dbapi.save_media(media)

        self.dbapi.delete_media(media)
        self.assertIsNone(self.dbapi.get_media(media.media_id))

    def test_delete_medias(self):

        _medias = []
        for i in range(1, 11):
            _medias.append(api_model.MediaFile(media_id=None,
                                               torrent_id=None,
                                               filename='movie-1.mp4',
                                               file_ext='.mp4',
                                               file_path='/tmp/media',
                                               synced=True if i % 2 else False)
                           )
        self.dbapi.bulk_create_medias(_medias)

        qfilter = {'=': {'synced': True}}
        self.dbapi.delete_medias(qfilter)

        qfilter = {'=': {'synced': False}}
        self.assertEqual(len(list(self.dbapi.get_medias(qfilter))), 5)

    def test_get_medias_by_torrent(self):

        tor1 = self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='active'))

        tor2 = self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='active'))

        _medias = []
        for i in range(1, 11):
            _medias.append(api_model.MediaFile(
                media_id=None,
                torrent_id=tor1.torrent_id if i % 2 else tor2.torrent_id,
                filename='movie-1.mp4',
                file_ext='.mp4',
                file_path='/tmp/media'))
        self.dbapi.bulk_create_medias(_medias)

        self.assertEqual(
            len(list(self.dbapi.get_medias_by_torrent(tor1.torrent_id))), 5)

    def test_get_medias_by(self):

        tor1 = self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='active'))

        tor2 = self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='active'))

        _medias = []
        for i in range(1, 11):
            _medias.append(api_model.MediaFile(
                media_id=None,
                torrent_id=tor1.torrent_id if i % 2 else tor2.torrent_id,
                filename='movie-{0}.mp4'.format(i),
                file_ext='.mp4',
                file_path='/tmp/media/{0}'.format('a' if i % 2 else 'b'),
                compressed=False if i % 2 else True,
                synced=True if i % 2 else False,
                missing=False if i % 2 else True,
                skipped=True if i == 5 else False,
                ))
        self.dbapi.bulk_create_medias(_medias)

        self.assertEqual(
            len(list(self.dbapi.get_medias_by(tor1.torrent_id))), 5)

        self.assertEqual(
            len(list(self.dbapi.get_medias_by(tor1.torrent_id,
                                              file_path='/tmp/media/a'))), 5)

        self.assertEqual(
            len(list(self.dbapi.get_medias_by(tor1.torrent_id,
                                              compressed=False))), 5)

        self.assertEqual(
            len(list(self.dbapi.get_medias_by(tor1.torrent_id,
                                              synced=True))), 5)

        self.assertEqual(
            len(list(self.dbapi.get_medias_by(tor1.torrent_id,
                                              missing=False))), 5)

        self.assertEqual(
            len(list(self.dbapi.get_medias_by(tor1.torrent_id,
                                              skipped=False))), 4)

    def test_get_processed_medias(self):

        tor1 = self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='active'))

        tor2 = self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='active'))

        _medias = []
        for i in range(1, 11):
            _medias.append(api_model.MediaFile(
                media_id=None,
                torrent_id=tor1.torrent_id if i % 2 else tor2.torrent_id,
                filename='movie-{0}.mp4'.format(i),
                file_ext='.mp4',
                file_path='/tmp/media/{0}'.format('a' if i % 2 else 'b'),
                compressed=False if i % 2 else True,
                synced=True if i % 2 else False,
                missing=False if i % 2 else True,
                skipped=True if i == 5 else False,
                ))
        self.dbapi.bulk_create_medias(_medias)

        self.assertEqual(
            len(list(self.dbapi.get_processed_medias(tor1.torrent_id))), 5)

    def test_save_appstate(self):

        appstate = api_model.AppState(name='test', value='fake')
        appstate = self.dbapi.save_appstate(appstate)
        self.assertIsInstance(appstate, api_model.AppState)

    def test_delete_appstate(self):

        appstate = self.dbapi.save_appstate(
            api_model.AppState(name='test', value='fake'))

        self.dbapi.delete_appstate(appstate)
        self.assertIsNone(self.dbapi.get_appstate('test'))

    def test_clean_up(self):
        # initial call where there is no last_purge_date
        # appstate entry.
        self.dbapi.clean_up()

        # second call where a value exists for
        # last_purge_date
        self.dbapi.clean_up()

        # now with last_purge_date >= 1 week ago
        self.dbapi.save_appstate(
            api_model.AppState(
                name='last_purge_date',
                value=datetime.datetime.utcnow() - datetime.timedelta(weeks=1)
                ))

        self.dbapi.clean_up()

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake1.torrent',
                              state='done'))

        self.dbapi.save_torrent(
            api_model.Torrent(torrent_id=None,
                              name='fake2.torrent',
                              state='done'))

        self.assertEqual(
            len(list(self.dbapi.get_torrents_eligible_for_purging())), 2)

        open(os.path.join(self.CONF.torrent.torrent_path,
                          'fake2.torrent'), 'a').close()
        self.dbapi.clean_up()
