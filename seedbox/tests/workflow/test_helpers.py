from __future__ import absolute_import
import tempfile
import testtools

import seedbox.db.schema as schema
import seedbox.db.api as dbapi
from seedbox.tests import test
from seedbox.workflow import helpers


class HelpersTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(HelpersTest, self).setUp()

        # initialize the database and schema details.
        schema.init()

    def test_set_failed(self):

        torrent = dbapi.add_torrent('hhhhhh.torrent')
        self.assertFalse(torrent.failed)
        self.assertIsNone(torrent.error_msg)

        helpers.set_torrent_failed(torrent, 'test error')
        self.assertTrue(torrent.failed)
        self.assertEqual(torrent.error_msg, 'test error')

        helpers.set_torrent_failed(torrent, 'another error')
        self.assertTrue(torrent.failed)
        self.assertEqual(torrent.error_msg, 'test error+&+another error')

    def test_synced_media_file(self):

        torrent = dbapi.add_torrent('help-funnny.torrent')

        mediafiles = [{'filename': 'vid11',
                       'file_ext': '.rar',
                       'file_path': '/etc/torrents/',
                       'compressed': 1,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid2',
                       'file_ext': '.mxx',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid3',
                       'file_ext': '.mp4',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid5',
                       'file_ext': '.mp4',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      ]

        dbapi.add_files_to_torrent(torrent, mediafiles)

        files = dbapi.get_files_by_torrent(torrent)
        for file in files:
            self.assertFalse(file.synced)
            helpers.synced_media_file(file)
            self.assertTrue(file.synced)

        with testtools.ExpectedException(ValueError):
            helpers.synced_media_file(None)

    def test_media_files_path(self):

        torrent = dbapi.add_torrent('xxxx.torrent')

        mediafiles = ['vid11.mp4', 'vid2.mp4', 'vid3.mp4',
                      'vid4.mp4', 'vid5.avi']

        media_list = []
        # now create the media files
        for media in mediafiles:
            (name, ext) = media.split('.')

            media_list.append({'filename': name,
                               'file_ext': '.'+ext})

        dbapi.add_files_to_torrent(torrent, media_list)
        all_media = dbapi.get_files_by_torrent(torrent)

        helpers.set_media_files_path(self.base_dir, all_media)
        for am in all_media:
            self.assertEqual(am.file_path, self.base_dir)

        with testtools.ExpectedException(ValueError):
            helpers.set_media_files_path(None, all_media)

        with testtools.ExpectedException(ValueError):
            helpers.set_media_files_path('/does/not/exist/path', all_media)

        with testtools.ExpectedException(ValueError):
            helpers.set_media_files_path(self.CONF.config_file, all_media)

        with testtools.ExpectedException(TypeError):
            helpers.set_media_files_path(self.base_dir, 'all_media')

    def test_torrent_processed(self):

        torrent = dbapi.add_torrent('funnny.torrent')

        mediafiles = [{'filename': 'vid11',
                       'file_ext': '.rar',
                       'file_path': '/etc/torrents/',
                       'compressed': 1,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid2',
                       'file_ext': '.mxx',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 1,
                       },
                      {'filename': 'vid3',
                       'file_ext': '.mp4',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 1,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid4',
                       'file_ext': '.mp4',
                       'file_path': None,
                       'compressed': 0,
                       'synced': 0,
                       'missing': 1,
                       'skipped': 0,
                       },
                      {'filename': 'vid5',
                       'file_ext': '.mp4',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 1,
                       'missing': 0,
                       'skipped': 0,
                       },
                      ]

        dbapi.add_files_to_torrent(torrent, mediafiles)
        all_media = dbapi.get_files_by_torrent(torrent)

        self.assertFalse(helpers.is_torrent_processed(torrent))

        for am in all_media:
            if am.synced or am.missing or am.skipped:
                continue
            else:
                am.synced = True

        self.assertTrue(helpers.is_torrent_processed(torrent))

        with testtools.ExpectedException(ValueError):
            helpers.is_torrent_processed(None)

    def test_add_mediafiles_to_torrent(self):

        torrent = dbapi.add_torrent('add_funnny.torrent')

        media1 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.base_dir)
        media2 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.base_dir)

        media_files = [media1.name,
                       media2.name,
                       ]

        helpers.add_mediafiles_to_torrent(torrent,
                                          self.base_dir,
                                          [])
        self.assertEqual(len(dbapi.get_files_by_torrent(torrent)), 0)

        helpers.add_mediafiles_to_torrent(torrent,
                                          self.base_dir,
                                          media_files)
        self.assertEqual(len(dbapi.get_files_by_torrent(torrent)), 2)

        with testtools.ExpectedException(ValueError):
            helpers.add_mediafiles_to_torrent(None,
                                              self.base_dir,
                                              media_files)

        with testtools.ExpectedException(ValueError):
            helpers.add_mediafiles_to_torrent(torrent,
                                              None,
                                              media_files)

        with testtools.ExpectedException(ValueError):
            helpers.add_mediafiles_to_torrent(torrent,
                                              '/does/not/exist/path',
                                              media_files)

        with testtools.ExpectedException(ValueError):
            helpers.add_mediafiles_to_torrent(torrent,
                                              self.CONF.config_file,
                                              media_files)

        with testtools.ExpectedException(TypeError):
            helpers.add_mediafiles_to_torrent(torrent,
                                              self.base_dir,
                                              'media_files')

    def test_get_media_files(self):

        torrent = dbapi.add_torrent('funnny.torrent')

        mediafiles = [{'filename': 'vid11',
                       'file_ext': '.rar',
                       'file_path': '/etc/torrents/',
                       'compressed': 1,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid2',
                       'file_ext': '.mxx',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 1,
                       },
                      {'filename': 'vid3',
                       'file_ext': '.mp4',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 1,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid4',
                       'file_ext': '.mp4',
                       'file_path': None,
                       'compressed': 0,
                       'synced': 0,
                       'missing': 1,
                       'skipped': 0,
                       },
                      {'filename': 'vid5',
                       'file_ext': '.avi',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 1,
                       'missing': 0,
                       'skipped': 0,
                       },
                      ]

        dbapi.add_files_to_torrent(torrent, mediafiles)

        # by path
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path='/etc/torrents/',
                                                 compressed=None,
                                                 synced=None,
                                                 missing=None,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 4)

        # by compressed (yes)
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=1,
                                                 synced=None,
                                                 missing=None,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 1)

        # by compressed (no)
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=0,
                                                 synced=None,
                                                 missing=None,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 4)

        # by synced (yes)
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=None,
                                                 synced=1,
                                                 missing=None,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 2)

        # by synced (no)
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=None,
                                                 synced=0,
                                                 missing=None,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 3)

        # by missing (yes)
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=None,
                                                 synced=None,
                                                 missing=1,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 1)

        # by missing (no)
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=None,
                                                 synced=None,
                                                 missing=0,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 4)

        # by skipped (yes)
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=None,
                                                 synced=None,
                                                 missing=None,
                                                 skipped=1)
        self.assertEqual(len(found_torrents), 1)

        # by skipped (no)
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=None,
                                                 synced=None,
                                                 missing=None,
                                                 skipped=0)
        self.assertEqual(len(found_torrents), 4)

        # by mutli options 1
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path='/etc/torrents/',
                                                 compressed=0,
                                                 synced=1,
                                                 missing=None,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 2)

        # by mutli options 1
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=None,
                                                 synced=None,
                                                 missing=1,
                                                 skipped=0)
        self.assertEqual(len(found_torrents), 1)

        # no matches
        found_torrents = helpers.get_media_files(torrent,
                                                 file_path=None,
                                                 compressed=1,
                                                 synced=1,
                                                 missing=1,
                                                 skipped=1)
        self.assertEqual(len(found_torrents), 0)

        # filter by file ext
        found_torrents = helpers.get_media_files(torrent,
                                                 file_exts='.avi',
                                                 compressed=None,
                                                 synced=1,
                                                 missing=None,
                                                 skipped=None)
        self.assertEqual(len(found_torrents), 1)

        with testtools.ExpectedException(ValueError):
            helpers.get_media_files(None,
                                    file_path=None,
                                    compressed=None,
                                    synced=None,
                                    missing=None,
                                    skipped=0)
