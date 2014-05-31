from __future__ import absolute_import
import os

import fixtures
from oslo.config import cfg

from seedbox.tests import test
# now include what we need to test
from seedbox import options


class OptionsTest(test.BaseTestCase):

    CFG_FILE = 'seedbox.conf'

    cfg_data = []
    cfg_data.append('[DEFAULT]\n')
    cfg_data.append('base_path=/home/shad\n')
    cfg_data.append('base_client_path=$base_path/torrent-test/deluge\n')
    cfg_data.append('\n')
    cfg_data.append('[torrent]\n')
    cfg_data.append('torrent_path=$base_client_path/torrents\n')
    cfg_data.append(
        'media_paths=$base_client_path/complete, $base_client_path/seedLT\n')
    cfg_data.append('incomplete_path=$base_client_path/inprogress\n')
    cfg_data.append('video_filetypes=.avi,.mp4,.mkv,.mpg\n')
    cfg_data.append('compressed_filetypes=.rar\n')
    cfg_data.append('minimum_file_size=75000000\n')
    cfg_data.append('\n')
    cfg_data.append('[process]\n')
    cfg_data.append('prepare=filecopy, fileunrar\n')
    cfg_data.append('activate=filesync\n')
    cfg_data.append('complete=filedelete\n')
    cfg_data.append('#max_processes=4\n')
    cfg_data.append('\n')
    cfg_data.append('[tasks_filesync]\n')
    cfg_data.append('#dryrun=false\n')
    cfg_data.append('verbose=true\n')
    cfg_data.append('progress=true\n')
    cfg_data.append('perms=true\n')
    cfg_data.append('delayupdates=true\n')
    cfg_data.append('recursive=true\n')
    cfg_data.append('chmod=ugo+rwx\n')
    cfg_data.append('#identity=\n')
    cfg_data.append('#port=22\n')
    cfg_data.append('#remote_user=\n')
    cfg_data.append('#remote_host=\n')
    cfg_data.append('#remote_path=\n')
    cfg_data.append('\n')

    def _write_cfg_file(self, location):

        # create the directory if it does not actually exist
        if not os.path.exists(location):
            try:
                os.mkdir(location)
            except OSError:
                pass

        with open(os.path.join(location, self.CFG_FILE), 'a') as cfg_file:
            cfg_file.writelines(self.cfg_data)

    def _delete_cfg_file(self, location):

        try:
            os.unlink(os.path.join(location, self.CFG_FILE))
        except Exception:
            # just ignore the exception
            pass

    def test_initialize_home(self):

        location = os.path.expanduser('~')
        self._write_cfg_file(location)

        self.assertTrue(os.path.exists(
            os.path.join(location, self.CFG_FILE)))

        options.initialize([])
        self.assertIsNotNone(cfg.CONF.config_file)
        self.assertIsNotNone(cfg.CONF.config_dir)

        cfg.CONF.reset()
        self._delete_cfg_file(location)

    def test_initialize_venv(self):

        location = os.path.join(os.getenv('VIRTUAL_ENV'), 'etc')
        self._write_cfg_file(location)

        self.assertTrue(os.path.exists(
            os.path.join(location, self.CFG_FILE)))

        options.initialize([])
        self.assertIsNotNone(cfg.CONF.config_file)
        self.assertIsNotNone(cfg.CONF.config_dir)

        cfg.CONF.reset()
        self._delete_cfg_file(location)

    def test_without_venv(self):

        location = os.path.expanduser('~')

        with fixtures.EnvironmentVariable('VIRTUAL_ENV'):

            self._write_cfg_file(location)

            self.assertTrue(os.path.exists(
                os.path.join(location, self.CFG_FILE)))

            options.initialize([])
            self.assertIsNotNone(cfg.CONF.config_file)
            self.assertIsNotNone(cfg.CONF.config_dir)

            cfg.CONF.reset()
            self._delete_cfg_file(location)

    def test_for_windows_home(self):

        location = os.path.join(os.path.expanduser('~'), options.PROJECT_NAME)

        with fixtures.MonkeyPatch('sys.platform', 'win'):

            self._write_cfg_file(location)

            self.assertTrue(os.path.exists(
                os.path.join(location, self.CFG_FILE)))

            options.initialize([])
            self.assertIsNotNone(cfg.CONF.config_file)
            self.assertEqual(cfg.CONF.config_dir, location)

            cfg.CONF.reset()
            self._delete_cfg_file(location)
