from seedbox import db
from seedbox.db import models
from seedbox import process
from seedbox.tests import test


class FakeManager(object):

    DBAPI = None

    class TaskManager(object):

        def __init__(self):
            self.tasks = []

        def add_tasks(self, tasks):
            self.tasks.extend(tasks)

        def run(self):
            _medias = []
            for i in range(1, 3):
                _medias.append(models.MediaFile(
                    media_id=None,
                    torrent_id=None,
                    filename='movie-{0}.mp4'.format(i),
                    file_ext='.mp4',
                    file_path='/tmp/media'))
            medias = FakeManager.DBAPI.bulk_create_medias(_medias)

            return medias

        def shutdown(self):
            pass


class ProcessTestCase(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(ProcessTestCase, self).setUp()

        self.patch(db, '_DBAPI', None)
        self.dbapi = db.dbapi(self.CONF)

    def test_process_no_work(self):
        process.start()
        self.assertTrue(True)

    def test_process(self):

        tor1 = self.dbapi.save_torrent(
            models.Torrent(torrent_id=None,
                           name='fake19.torrent'))

        _medias = []
        for i in range(1, 3):
            _medias.append(models.MediaFile(
                media_id=None,
                torrent_id=tor1.torrent_id,
                filename='movie-{0}.mp4'.format(i),
                file_ext='.mp4',
                file_path='/tmp/media'))
        self.dbapi.bulk_create_medias(_medias)

        FakeManager.DBAPI = self.dbapi
        self.patch(process, 'manager', FakeManager)

        process.start()
        self.assertTrue(True)

    def test_process_empty_torrent(self):

        self.dbapi.save_torrent(
            models.Torrent(torrent_id=None,
                           name='fake21.torrent'))

        FakeManager.DBAPI = self.dbapi
        self.patch(process, 'manager', FakeManager)

        process.start()
        self.assertTrue(True)
