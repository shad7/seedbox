from seedbox.process import manager
from seedbox.tests import test


class SampleTask(object):

    def __call__(self):
        return [True]


class ManagerTestCase(test.ConfiguredBaseTestCase):

    def test_manager(self):
        mgr = manager.TaskManager()

        _tasks = []
        _tasks.append(SampleTask())
        _tasks.append(SampleTask())
        _tasks.append(SampleTask())

        mgr.add_tasks(_tasks)
        mgr.add_tasks(SampleTask())

        self.assertEqual(len(mgr.tasks), 4)

        results = mgr.run()
        self.assertEqual(len(mgr.tasks), 0)
        self.assertEqual(len(results), 4)

        mgr.shutdown()
