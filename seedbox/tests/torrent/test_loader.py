from __future__ import absolute_import
import os
import glob
import tempfile

import mock

from seedbox.db import schema
from seedbox.tests import test
from seedbox import torrent as torrent_loader
from seedbox.torrent import loader

torrent_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'testdata')


class TorrentLoaderTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(TorrentLoaderTest, self).setUp()

        self.CONF.set_override('torrent_path',
                               torrent_path,
                               group='torrent')

        self.CONF.set_override('media_paths',
                               [torrent_path],
                               group='torrent')

        self.CONF.set_override('incomplete_path',
                               torrent_path,
                               group='torrent')

        # initialize the database and schema details.
        schema.init()

    def test_pub_loader(self):
        torrent_loader.load()

    @mock.patch('seedbox.torrent.loader')
    def test_load_torrents(self, mock_loader):
        mock_loader._is_torrent_downloading.return_value = True
        loader.load_torrents()

    def test_load_torrents_no_parse(self):

        for tor in glob.glob(os.path.join(torrent_path, '*.torrent')):
            schema.Torrent(name=os.path.basename(tor), invalid=True)

        loader.load_torrents()

    def test_parsing_required(self):
        torrent = schema.Torrent(name='preq-check')
        result = loader._is_parsing_required(torrent)
        self.assertTrue(result)

        torrent.invalid = True
        result = loader._is_parsing_required(torrent)
        self.assertFalse(result)

        torrent.invalid = False
        torrent.purged = True
        result = loader._is_parsing_required(torrent)
        self.assertFalse(result)

        torrent.purged = False
        schema.MediaFile(filename='media',
                         file_ext='.mp4',
                         torrent=torrent)
        result = loader._is_parsing_required(torrent)
        self.assertFalse(result)

    def test_torrent_downloading(self):

        mediafiles = [('fake1.mp4', 150000), ('fake2.mp4', 150000)]

        self.CONF.set_override('incomplete_path',
                               self.base_dir,
                               group='torrent')

        result = loader._is_torrent_downloading(mediafiles)
        self.assertFalse(result)

        media1 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.base_dir)
        media2 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.base_dir)
        mediafiles = [(media1.name, 150000), (media2.name, 150000)]

        result = loader._is_torrent_downloading(mediafiles)
        self.assertTrue(result)

    def test_get_file_path(self):

        self.CONF.set_override('media_paths',
                               [self.base_dir],
                               group='torrent')

        location = loader._get_file_path('fake-name.mp4')
        self.assertIsNone(location)

        media1 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.base_dir)

        location = loader._get_file_path(media1.name)
        self.assertIsNotNone(location)
