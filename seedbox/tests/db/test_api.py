from __future__ import absolute_import
import datetime
import os

import six

from seedbox.tests import test
import seedbox.db.schema as schema

# now include what we need to test
import seedbox.db.api as dbapi


class ApiDBTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(ApiDBTest, self).setUp()
        # initialize the database and schema details.
        schema.init()

    def test_initialize(self):

        self.CONF.set_override('purge', True, group='db')
        dbapi.initialize()

        self.CONF.set_override('purge', False, group='db')

        search = schema.AppState.selectBy(name='last_purge_date')
        last_purge_date = search.getOne(None)
        if last_purge_date is not None:
            schema.AppState.deleteBy(name='last_purge_date')

        # no existing last_purge_date
        dbapi.initialize()

        # now with existing last_purge_date
        dbapi.initialize()

        # now with last_purge_date >= 1 week ago
        dbapi.set_date('last_purge_date',
                       datetime.datetime.utcnow() -
                       datetime.timedelta(weeks=1))
        dbapi.initialize()

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent',
                    'test-a.torrent', 'myt.torrent', 'ant.torrent',
                    'the-perfect-t.torrent']

        states = [schema.DONE,
                  schema.CANCELLED,
                  ]
        # loop through and create the torrents
        for i, name in enumerate(tornames):
            torrent = dbapi.add_torrent(name=name)
            torrent.state = states[i % 2]

        torpath = os.path.join(self.base_dir, 'torrent')
        if not os.path.exists(torpath):
            os.mkdir(torpath)
        self.CONF.set_override('torrent_path',
                               torpath,
                               group='torrent')

        dbapi.initialize()

    def test_add_torrent(self):

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent']

        counter = 0
        # loop through and create the torrents
        for name in tornames:
            counter += 1
            torrent = dbapi.add_torrent(name=name)
            # verify we have an instance
            self.assertIsInstance(torrent, schema.Torrent)
            # verify the defaults are set correctly
            self.assertEqual(torrent.name, name)
            self.assertIsNotNone(torrent.create_date)
            self.assertEqual(torrent.state, schema.INIT)
            self.assertEqual(torrent.retry_count, 0)
            self.assertFalse(torrent.failed)
            self.assertIsNone(torrent.error_msg)
            self.assertFalse(torrent.invalid)
            self.assertFalse(torrent.purged)
            self.assertEqual(len(list(torrent.media_files)), 0)

        # make sure the total list size is the total number we processed
        self.assertEqual(len(tornames), counter)

    def test_update_state(self):

        torrent = dbapi.add_torrent('xxxx.torrent')
        self.assertEqual(torrent.state, schema.INIT)

        dbapi.update_state([torrent], schema.READY)
        self.assertEqual(torrent.state, schema.READY)
        dbapi.update_state([torrent], schema.ACTIVE)
        self.assertEqual(torrent.state, schema.ACTIVE)
        torrent.failed = True
        dbapi.update_state([torrent], schema.DONE)
        self.assertEqual(torrent.state, schema.ACTIVE)
        torrent.failed = False
        dbapi.update_state([torrent], schema.DONE)
        self.assertEqual(torrent.state, schema.DONE)
        dbapi.update_state([torrent], schema.CANCELLED)
        self.assertEqual(torrent.state, schema.CANCELLED)

    def test_set_failed(self):

        torrent = dbapi.add_torrent('xxxx.torrent')
        self.assertFalse(torrent.failed)
        self.assertIsNone(torrent.error_msg)

        dbapi.set_failed(torrent, 'torrent failed to parse')
        self.assertTrue(torrent.failed)
        self.assertEqual(torrent.error_msg, 'torrent failed to parse')

    def test_set_invalid(self):

        torrent = dbapi.add_torrent('xxxx.torrent')
        self.assertFalse(torrent.invalid)
        self.assertEqual(torrent.state, schema.INIT)

        dbapi.set_invalid(torrent)
        self.assertTrue(torrent.invalid)
        self.assertEqual(torrent.state, schema.CANCELLED)

    def test_set_done(self):

        torrent = dbapi.add_torrent('xxxx.torrent')
        self.assertEqual(torrent.state, schema.INIT)

        dbapi.set_done(torrent)
        self.assertEqual(torrent.state, schema.DONE)

    def test_reset_failed(self):

        torrent = dbapi.add_torrent('xxxx.torrent')
        dbapi.set_failed(torrent, 'torrent failed to parse')
        self.assertTrue(torrent.failed)
        self.assertEqual(torrent.error_msg, 'torrent failed to parse')

        dbapi.reset_failed(torrent)
        self.assertFalse(torrent.failed)
        self.assertIsNone(torrent.error_msg)

    def test_fetch_torrent_by_name(self):

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent']

        created_torrents = []
        # loop through and create the torrents
        for name in tornames:
            torrent = dbapi.add_torrent(name=name)
            created_torrents.append(torrent)

        for name in tornames:
            torrent = dbapi.fetch_torrent_by_name(name=name)
            self.assertTrue(torrent in created_torrents)

    def test_fetch_or_create_torrent(self):

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent']

        # loop through and create the torrents
        for name in tornames:
            torrent = dbapi.fetch_or_create_torrent(name=name)
            self.assertIsNotNone(torrent)
            other_torrent = dbapi.fetch_or_create_torrent(name=name)
            self.assertIs(torrent, other_torrent)

    def test_add_files_to_torrent(self):

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

        self.assertEqual(len(list(torrent.media_files)), len(mediafiles))

    def test_get_files_by_torrent(self):

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

        self.assertEqual(len(dbapi.get_files_by_torrent(torrent)),
                         len(mediafiles))

    def test_get_torrents_by_state(self):

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent']

        states = [(schema.INIT, False),
                  (schema.READY, True),
                  (schema.ACTIVE, False),
                  (schema.INIT, False),
                  (schema.READY, True),
                  (schema.ACTIVE, False),
                  ]

        # loop through and create the torrents
        for i, name in enumerate(tornames):
            torrent = dbapi.add_torrent(name=name)
            torrent.state = states[i][0]
            torrent.failed = states[i][1]

        torrents = dbapi.get_torrents_by_state(schema.INIT, False)
        self.assertEqual(len(torrents), 2)

        torrents = dbapi.get_torrents_by_state(schema.READY, True)
        self.assertEqual(len(torrents), 2)

        torrents = dbapi.get_torrents_by_state(schema.ACTIVE, False)
        self.assertEqual(len(torrents), 2)

    def test_delete_torrents(self):

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent']

        created_torrents = []
        # loop through and create the torrents
        for name in tornames:
            torrent = dbapi.add_torrent(name=name)
            created_torrents.append(torrent)

        dbapi.delete_torrents(created_torrents)

        found = []
        for name in tornames:
            torrent = dbapi.fetch_torrent_by_name(name=name)
            if torrent:
                found.append(torrent)

        self.assertNotEqual(len(created_torrents), len(found))
        self.assertEqual(len(found), 0)

    def test_eligible_for_purging(self):

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent',
                    'test-a.torrent', 'myt.torrent', 'ant.torrent',
                    'the-perfect-t.torrent']

        states = [schema.DONE,
                  schema.CANCELLED,
                  ]
        # loop through and create the torrents
        for i, name in enumerate(tornames):
            torrent = dbapi.add_torrent(name=name)
            torrent.state = states[i % 2]

        torrent = dbapi.add_torrent('funnny.torrent')

        purgable = dbapi.get_eligible_for_purging()
        self.assertEqual(len(purgable), 10)

        torrent.state = schema.DONE
        purgable = dbapi.get_eligible_for_purging()
        self.assertEqual(len(purgable), 11)

    def test_eligible_for_removal(self):

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent',
                    'test-a.torrent', 'myt.torrent', 'ant.torrent',
                    'the-perfect-t.torrent']

        states = [schema.DONE,
                  schema.CANCELLED,
                  ]
        # loop through and create the torrents
        for i, name in enumerate(tornames):
            torrent = dbapi.add_torrent(name=name)
            torrent.state = states[i % 2]
            torrent.purged = True

        torrent = dbapi.add_torrent('funnny.torrent')

        removeable = dbapi.get_eligible_for_removal()
        self.assertEqual(len(removeable), 10)

        torrent.state = schema.DONE
        torrent.purged = True
        removeable = dbapi.get_eligible_for_removal()
        self.assertEqual(len(removeable), 11)

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
                       'file_ext': '.mp4',
                       'file_path': '/etc/torrents/',
                       'compressed': 0,
                       'synced': 1,
                       'missing': 0,
                       'skipped': 0,
                       },
                      ]

        dbapi.add_files_to_torrent(torrent, mediafiles)

        # by path
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path='/etc/torrents/',
                                               compressed=None,
                                               synced=None,
                                               missing=None,
                                               skipped=None)
        self.assertEqual(len(found_torrents), 4)

        # by compressed (yes)
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=1,
                                               synced=None,
                                               missing=None,
                                               skipped=None)
        self.assertEqual(len(found_torrents), 1)

        # by compressed (no)
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=0,
                                               synced=None,
                                               missing=None,
                                               skipped=None)
        self.assertEqual(len(found_torrents), 4)

        # by synced (yes)
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=None,
                                               synced=1,
                                               missing=None,
                                               skipped=None)
        self.assertEqual(len(found_torrents), 2)

        # by synced (no)
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=None,
                                               synced=0,
                                               missing=None,
                                               skipped=None)
        self.assertEqual(len(found_torrents), 3)

        # by missing (yes)
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=None,
                                               synced=None,
                                               missing=1,
                                               skipped=None)
        self.assertEqual(len(found_torrents), 1)

        # by missing (no)
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=None,
                                               synced=None,
                                               missing=0,
                                               skipped=None)
        self.assertEqual(len(found_torrents), 4)

        # by skipped (yes)
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=None,
                                               synced=None,
                                               missing=None,
                                               skipped=1)
        self.assertEqual(len(found_torrents), 1)

        # by skipped (no)
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=None,
                                               synced=None,
                                               missing=None,
                                               skipped=0)
        self.assertEqual(len(found_torrents), 4)

        # by mutli options 1
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path='/etc/torrents/',
                                               compressed=0,
                                               synced=1,
                                               missing=None,
                                               skipped=None)
        self.assertEqual(len(found_torrents), 2)

        # by mutli options 1
        found_torrents = dbapi.get_media_files(torrent,
                                               file_path=None,
                                               compressed=None,
                                               synced=None,
                                               missing=1,
                                               skipped=0)
        self.assertEqual(len(found_torrents), 1)

    def test_processed_media_files(self):

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

        processed = dbapi.get_processed_media_files(torrent)
        self.assertEqual(len(processed), 4)

        torrent.invalid = 1
        processed = dbapi.get_processed_media_files(torrent)
        self.assertEqual(len(processed), 0)

    def test_purge_media(self):

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

        tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent',
                    'x1.torrent', 'XXXX10.torrent', 'test2.torrent',
                    'test-a.torrent', 'myt.torrent', 'ant.torrent',
                    'the-perfect-t.torrent']

        states = [schema.DONE,
                  schema.CANCELLED,
                  ]

        torrents = []
        # loop through and create the torrents
        for i, name in enumerate(tornames):
            torrent = dbapi.add_torrent(name=name)
            torrents.append(torrent)
            torrent.state = states[i % 2]

            dbapi.add_files_to_torrent(torrent, mediafiles)

        for torrent in torrents:
            self.assertEqual(len(list(torrent.media_files)), 5)
            dbapi.purge_media(torrent)
            self.assertEqual(len(list(torrent.media_files)), 0)

    def test_appstate(self):
        """
        AppState is just a key:value pair caching. So test out setting each
        'type' in one test case.
        """
        str_key = 'key_str'
        dbapi.set(str_key, None)
        str_state = dbapi.get(str_key)
        # verify we have an instance
        self.assertIsNone(str_state)
        self.assertIsInstance(str_state, type(None))

        dbapi.set(str_key, 'Just a simple string')
        str_state = dbapi.get(str_key)
        self.assertIsNotNone(str_state)
        self.assertIsInstance(str_state, six.string_types)

        int_key = 'key_int'
        dbapi.set_int(int_key, None)
        int_state = dbapi.get_int(int_key)
        # verify we have an instance
        self.assertIsNotNone(int_state)
        self.assertIsInstance(int_state, six.integer_types)

        dbapi.set_int(int_key, 7)
        int_state = dbapi.get_int(int_key)
        self.assertIsNotNone(int_state)
        self.assertIsInstance(int_state, six.integer_types)

        list_key = 'key_list'
        dbapi.set_list(list_key, None)
        list_state = dbapi.get_list(list_key)
        self.assertIsNotNone(list_state)
        # verify we have an instance
        self.assertIsInstance(list_state, list)

        dbapi.set_list(list_key, 'item1,item2,item3,item4,item5')
        list_state = dbapi.get_list(list_key)
        self.assertIsNotNone(list_state)
        self.assertIsInstance(list_state, list)

        list_state = dbapi.get_list('dummy')
        self.assertIsNone(list_state)
        self.assertIsInstance(list_state, type(None))

        list_state = dbapi.get_list('dummy', ['dummy'])
        self.assertIsNotNone(list_state)
        self.assertIsInstance(list_state, list)
        self.assertEqual(list_state, ['dummy'])

        flag_key = 'key_flag'
        dbapi.set_flag(flag_key, None)
        flag_state = dbapi.get_flag(flag_key)
        print 'flag_state=', flag_state
        # verify we have an instance
        self.assertIsNotNone(flag_state)
        self.assertIsInstance(flag_state, bool)

        dbapi.set_flag(flag_key, True)
        flag_state = dbapi.get_flag(flag_key)
        self.assertIsNotNone(flag_state)
        self.assertIsInstance(flag_state, bool)

        flag_state = dbapi.get_flag('dummy')
        self.assertIsNone(flag_state)
        self.assertIsInstance(flag_state, type(None))

        flag_state = dbapi.get_flag('dummy', False)
        self.assertIsNotNone(flag_state)
        self.assertIsInstance(flag_state, bool)
        self.assertFalse(flag_state)

        date_key = 'key_date'
        dbapi.set_date(date_key, None)
        date_state = dbapi.get_date(date_key)
        self.assertIsNotNone(date_state)
        # verify we have an instance
        self.assertIsInstance(date_state, datetime.datetime)
