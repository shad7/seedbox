from __future__ import absolute_import

import testtools

from seedbox.tests import test
from seedbox.workflow import _workflow as wfdef


class MyTestFlow(wfdef.BaseFlow):

    def _run(self, torrents):
        return True


class MyBadFlow(wfdef.BaseFlow):
    pass


class WorkflowDefTest(test.BaseTestCase):

    def test_normal(self):

        testflow = MyTestFlow()
        self.assertEqual(testflow.state, 'init')

        testflow.prepare('torrents')
        self.assertEqual(testflow.state, 'ready')

        testflow.activate('torrents')
        self.assertEqual(testflow.state, 'active')

        testflow.complete('torrents')
        self.assertEqual(testflow.state, 'done')

    def test_abnormal_stop(self):

        testflow = MyTestFlow()
        self.assertEqual(testflow.state, 'init')

        testflow.prepare('torrents')
        self.assertEqual(testflow.state, 'ready')

        testflow.cancel()
        self.assertEqual(testflow.state, 'cancelled')

    def test_bad_flow(self):

        badflow = MyBadFlow()

        with testtools.ExpectedException(NotImplementedError):
            badflow.prepare('torrents')

    def test_next_step(self):

        testflow = MyTestFlow()
        self.assertEqual(testflow.state, 'init')

        next_step = testflow.get_next_step('prepare')
        self.assertEqual(next_step, 'prepare')
