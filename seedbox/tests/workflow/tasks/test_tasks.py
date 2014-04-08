from __future__ import absolute_import

from seedbox.tests import test
from seedbox.workflow.tasks import base


class SampleTask(base.BasePlugin):
    pass


class DisabledTask(base.BasePlugin):

    def __init__(self):
        super(DisabledTask, self).__init__()
        self._disabled = True


class BaseTasksTest(test.ConfiguredBaseTestCase):

    def test_plugin(self):

        task = SampleTask()
        self.assertEqual(str(task), """SampleTask: {'_disabled': None}""")

    def test_disabled_plugin(self):

        task = DisabledTask()
        self.assertTrue(task.disabled)
