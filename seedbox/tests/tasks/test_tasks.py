import os
from testtools import matchers

from seedbox.db import models
from seedbox.tasks import base
from seedbox.tests import test


class SampleTask(base.BaseTask):

    def execute(self):
        pass


class HighPriorityTask(base.BaseTask):

    PRIORITY = 1

    def execute(self):
        pass


class DefaultPriorityTask(base.BaseTask):

    def execute(self):
        pass


class LowPriorityTask(base.BaseTask):

    PRIORITY = 999

    def execute(self):
        pass


class ExceptionTask(base.BaseTask):

    def execute(self):
        raise RuntimeError('task failed')


class BaseTasksTest(test.ConfiguredBaseTestCase):

    def test_task_str(self):

        task = SampleTask(None)
        print str(task)
        self.assertThat(str(task), matchers.StartsWith("""SampleTask:"""))

    def test_sorted_tasks(self):
        tasks = []
        tasks.append(SampleTask(None))
        tasks.append(HighPriorityTask(None))
        tasks.append(LowPriorityTask(None))

        sorted_tasks = sorted(tasks)

        self.assertIsInstance(sorted_tasks[0], HighPriorityTask)
        self.assertIsInstance(sorted_tasks[1], SampleTask)
        self.assertIsInstance(sorted_tasks[2], LowPriorityTask)

    def test_task_equal(self):

        task1 = SampleTask(None)
        task2 = DefaultPriorityTask(None)
        self.assertEqual(task1, task2)

    def test_task_lessthan(self):

        task1 = SampleTask(None)
        task2 = LowPriorityTask(None)
        self.assertLess(task1, task2)

    def test_task_greaterthan(self):

        task1 = HighPriorityTask(None)
        task2 = LowPriorityTask(None)
        self.assertGreater(task2, task1)

    def test_actionable(self):
        self.assertTrue(SampleTask.is_actionable(None))

    def test_execute(self):
        mf = models.MediaFile.make_empty()
        task = SampleTask(mf)

        files = task()
        self.assertEqual(len(files), 1)

    def test_add_gen_files(self):

        if not os.path.exists(self.CONF.tasks.sync_path):
            os.mkdir(self.CONF.tasks.sync_path)
        filename = 'fake.mp4'
        open(os.path.join(self.CONF.tasks.sync_path,
                          filename), 'w').close()
        files = [filename]

        mf = models.MediaFile.make_empty()
        task = SampleTask(mf)

        task.add_gen_files(files)

        all_files = task()
        self.assertEqual(len(all_files), 2)

    def test_execute_fail(self):

        mf = models.MediaFile.make_empty()
        task = ExceptionTask(mf)

        medias = task()
        self.assertThat(medias[0].error_msg.strip(),
                        matchers.EndsWith('task failed'))
