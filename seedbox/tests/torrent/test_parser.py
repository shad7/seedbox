from __future__ import absolute_import
import os
import glob

import testtools

from seedbox.tests import test
from seedbox.torrent import parser

torrent_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'testdata')


class TorrentParserTest(test.BaseTestCase):

    def test_parse(self):

        tfiles = glob.glob(os.path.join(torrent_path, 'other-*.torrent'))

        for tfile in tfiles:
            torrent = parser.TorrentParser(tfile)
            self.assertIsNotNone(torrent)
            self.assertIsNotNone(torrent.get_tracker_url())
            self.assertIsNotNone(torrent.get_creation_date())
            self.assertIsNotNone(torrent.get_creation_date(str()))
            self.assertTrue(len(torrent.get_files_details()) > 0)

    def test_custom_parser1(self):
        tfile = os.path.join(torrent_path, 'bencode-bad-1.torrent')
        torrent = parser.TorrentParser(tfile)
        self.assertIsNotNone(torrent)

    def test_custom_parser2(self):
        tfile = os.path.join(torrent_path, 'bencode-bad-2.torrent')
        torrent = parser.TorrentParser(tfile)
        self.assertIsNotNone(torrent)

    def test_custom_parser3(self):
        tfile = os.path.join(torrent_path, 'bencode-bad-3.torrent')
        torrent = parser.TorrentParser(tfile)
        self.assertIsNotNone(torrent)

    def test_tiny_torrent(self):
        tfile = os.path.join(torrent_path, 'tiny-torrent.torrent')
        torrent = parser.TorrentParser(tfile)
        self.assertIsNotNone(torrent)

    def test_medium_torrent(self):
        tfile = os.path.join(torrent_path, 'medium-torrent.torrent')
        torrent = parser.TorrentParser(tfile)
        self.assertIsNotNone(torrent)

    def test_large_torrent(self):
        tfile = os.path.join(torrent_path, 'large-torrent.torrent')
        torrent = parser.TorrentParser(tfile)
        self.assertIsNotNone(torrent)

    def test_client_name(self):
        tfile = os.path.join(torrent_path, 'other-5.torrent')
        torrent = parser.TorrentParser(tfile)
        self.assertIsNotNone(torrent.get_client_name())

        tfile = os.path.join(torrent_path, 'other-9.torrent')
        torrent = parser.TorrentParser(tfile)
        self.assertIsNone(torrent.get_client_name())

    def test_missing_file(self):

        with testtools.ExpectedException(ValueError):
            parser.TorrentParser(str())

        with testtools.ExpectedException(IOError):
            parser.TorrentParser('dummy/file/does/not/exist')
