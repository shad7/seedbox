from __future__ import print_function
import os
from testtools import matchers

from seedbox.db import models
from seedbox.tasks import base
from seedbox.tests import test


class SampleTask(base.BaseTask):

    def execute(self):
        pass


class ExceptionTask(base.BaseTask):

    def execute(self):
        raise RuntimeError('task failed')


class BaseTasksTest(test.ConfiguredBaseTestCase):

    def test_task_str(self):

        task = SampleTask(None)
        print(str(task))
        self.assertThat(str(task), matchers.StartsWith("""SampleTask:"""))

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
