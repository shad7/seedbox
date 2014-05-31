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
