from __future__ import absolute_import

import seedbox.db.schema as schema
import seedbox.db.api as dbapi
from seedbox.tests import test
from seedbox.workflow.tasks import validate_phase


class ValidateTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(ValidateTest, self).setUp()

        # initialize the database and schema details.
        schema.init()

    def test_prepare(self):

        torrent = dbapi.add_torrent('help-funnny.torrent')

        mediafiles = [{'filename': 'vid11',
                       'file_ext': '.rar',
                       'file_path': self.CONF.plugins.sync_path,
                       'compressed': 1,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid2',
                       'file_ext': '.mxx',
                       'file_path': self.CONF.plugins.sync_path,
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 1,
                       },
                      {'filename': 'vid3',
                       'file_ext': '.mp4',
                       'file_path': self.CONF.plugins.sync_path,
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      {'filename': 'vid5',
                       'file_ext': '.mp4',
                       'file_path': self.CONF.plugins.sync_path,
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 0,
                       },
                      ]

        dbapi.add_files_to_torrent(torrent, mediafiles)

        validator = validate_phase.PhaseValidator()
        self.assertEqual(len(validator.validate_init([torrent])), 1)

        files = dbapi.get_files_by_torrent(torrent)
        for file in files:
            file.skipped = 1

        validator = validate_phase.PhaseValidator()
        self.assertEqual(len(validator.validate_init([torrent])), 0)

    def test_activate(self):

        torrent = dbapi.add_torrent('help-funnny.torrent')

        mediafiles = [{'filename': 'vid11',
                       'file_ext': '.rar',
                       'file_path': self.CONF.plugins.sync_path,
                       'compressed': 1,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 1,
                       },
                      {'filename': 'vid2',
                       'file_ext': '.mxx',
                       'file_path': self.CONF.plugins.sync_path,
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 1,
                       },
                      {'filename': 'vid3',
                       'file_ext': '.mp4',
                       'file_path': self.CONF.plugins.sync_path,
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 1,
                       },
                      {'filename': 'vid5',
                       'file_ext': '.mp4',
                       'file_path': self.CONF.plugins.sync_path,
                       'compressed': 0,
                       'synced': 0,
                       'missing': 0,
                       'skipped': 1,
                       },
                      ]

        dbapi.add_files_to_torrent(torrent, mediafiles)

        validator = validate_phase.PhaseValidator()
        self.assertEqual(len(validator.validate_active([torrent])), 1)

        files = dbapi.get_files_by_torrent(torrent)
        for file in files:
            file.skipped = 0

        validator = validate_phase.PhaseValidator()
        self.assertEqual(len(validator.validate_active([torrent])), 0)

    def test_complete(self):

        validator = validate_phase.PhaseValidator()
        self.assertEqual(len(validator.validate_done([])), 0)
