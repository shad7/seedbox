from seedbox import db
from seedbox.db import models
from seedbox.tests import test
from seedbox.process import flow


class FlowTestCase(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(FlowTestCase, self).setUp()

        self.patch(db, '_DBAPI', None)
        self.dbapi = db.dbapi(self.CONF)

        self.torrent = self.dbapi.save_torrent(
            models.Torrent(torrent_id=None,
                           name='fake1.torrent'))

        self.CONF.set_override('prepare',
                               ['filecopy', 'fileunrar'],
                               group='process')

        self.CONF.set_override('activate',
                               ['filesync'],
                               group='process')

        self.CONF.set_override('complete',
                               ['filedelete'],
                               group='process')

    def test_base_flow(self):

        _medias = []
        _medias.append(models.MediaFile(
            media_id=None,
            torrent_id=self.torrent.torrent_id,
            filename='movie-1.mp4',
            file_ext='.mp4',
            file_path='/tmp/media/',
            compressed=0,
            synced=0,
            missing=0,
            skipped=0
            ))
        _medias.append(models.MediaFile(
            media_id=None,
            torrent_id=self.torrent.torrent_id,
            filename='movie-2.rar',
            file_ext='.rar',
            file_path='/tmp/media/',
            compressed=1,
            synced=0,
            missing=0,
            skipped=0
            ))
        self.dbapi.bulk_create_medias(_medias)

        wf = flow.BaseFlow(self.torrent)

        tasks = wf.next_tasks()
        self.assertEqual(len(list(tasks)), 2)
