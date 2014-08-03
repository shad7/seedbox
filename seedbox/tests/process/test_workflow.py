from seedbox import db
from seedbox.db import models
from seedbox.tests import test
from seedbox.process import workflow


class WorkflowTestCase(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(WorkflowTestCase, self).setUp()

        self.patch(db, '_DBAPI', None)
        self.dbapi = db.dbapi(self.CONF)

        self.torrent = self.dbapi.save_torrent(
            models.Torrent(torrent_id=None,
                           name='fake1.torrent'))

    def test_workflow(self):
        wf = workflow.Workflow(self.torrent)
        status = wf.run()
        self.assertFalse(status)
        status = wf.run()
        self.assertFalse(status)
        status = wf.run()
        self.assertTrue(status)
        status = wf.run()
        self.assertTrue(status)

    def test_cancelled(self):
        self.torrent.state = 'cancelled'
        wf = workflow.Workflow(self.torrent)
        status = wf.run()
        self.assertTrue(status)

    def test_stop_workflow(self):

        torrent = self.dbapi.save_torrent(
            models.Torrent(torrent_id=None,
                           name='fake177.torrent',
                           state='active'))

        media = models.MediaFile(media_id=None,
                                 torrent_id=torrent.torrent_id,
                                 filename='movie-177.mp4',
                                 file_ext='.mp4',
                                 file_path='/tmp/media',
                                 error_msg='bad thing happened')
        media = self.dbapi.save_media(media)

        wf = workflow.Workflow(torrent)
        status = wf.run()
        self.assertTrue(status)
