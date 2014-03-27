from __future__ import absolute_import
import os

from oslo.config import cfg

from seedbox.tests import test
# now include what we need to test
from seedbox import options


class OptionsTest(test.BaseTestCase):

    def setUp(self):
        super(OptionsTest, self).setUp()

        self.cfg_data = []
        self.cfg_data.append('[DEFAULT]\n')
        self.cfg_data.append('base_path=/home/shad\n')
        self.cfg_data.append('base_client_path=$base_path/torrent-test/deluge\n')
        self.cfg_data.append('\n')
        self.cfg_data.append('[torrent]\n')
        self.cfg_data.append('torrent_path=$base_client_path/torrents\n')
        self.cfg_data.append('media_paths=$base_client_path/complete, $base_client_path/seedLT\n')
        self.cfg_data.append('incomplete_path=$base_client_path/inprogress\n')
        self.cfg_data.append('video_filetypes=.avi,.mp4,.mkv,.mpg\n')
        self.cfg_data.append('compressed_filetypes=.rar\n')
        self.cfg_data.append('minimum_file_size=75000000\n')
        self.cfg_data.append('\n')
        self.cfg_data.append('[workflow]\n')
        self.cfg_data.append('#plugin_paths=\n')
        self.cfg_data.append('#disabled_phases=\n')
        self.cfg_data.append('#max_retry=5\n')
        self.cfg_data.append('\n')
        self.cfg_data.append('[filesync]\n')
        self.cfg_data.append('#dryrun=false\n')
        self.cfg_data.append('verbose=true\n')
        self.cfg_data.append('progress=true\n')
        self.cfg_data.append('perms=true\n')
        self.cfg_data.append('delayupdates=true\n')
        self.cfg_data.append('recursive=true\n')
        self.cfg_data.append('chmod=ugo+rwx\n')
        self.cfg_data.append('#identity=\n')
        self.cfg_data.append('#port=22\n')
        self.cfg_data.append('#remote_path=\n')
        self.cfg_data.append('\n')
        self.cfg_data.append('[plugins]\n')
        self.cfg_data.append('sync_path=$base_client_path/toSync\n')
        self.cfg_data.append('#copy_file_v1_disabled=true\n')
        self.cfg_data.append('delete_file_v1_disabled=false\n')
        self.cfg_data.append('#sync_file_v1_disabled=true\n')
        self.cfg_data.append('unrar_file_v1_disabled=false\n')
        self.cfg_data.append('copy_file_v2_disabled=false\n')
        self.cfg_data.append('unrar_file_v2_disabled=false\n')
        self.cfg_data.append('phase_validator_v1_disabled=false\n')
        self.cfg_data.append('\n')
        self.cfg_data.append('[prepare]\n')
        self.cfg_data.append('slot_size=500\n')
        self.cfg_data.append('min_storage_threshold=5\n')
        self.cfg_data.append('storage_check_override=false\n')
        self.cfg_data.append('storage_system=si\n')
        self.cfg_data.append('\n')

    def test_initialize_home(self):

        with open(os.path.join(os.path.expanduser('~'),
                               'seedbox.conf'), 'a') as cfg_file:
            cfg_file.writelines(self.cfg_data)

        options.initialize([])
        self.assertIsNotNone(cfg.CONF.config_file)
        self.assertIsNotNone(cfg.CONF.config_dir)

    def test_initialize_venv(self):
        try:
            os.mkdir(os.path.join(os.getenv('VIRTUAL_ENV'), 'etc'))
        except OSError:
            pass

        with open(os.path.join(os.getenv('VIRTUAL_ENV'), 'etc',
                               'seedbox.conf'), 'a') as cfg_file:
            cfg_file.writelines(self.cfg_data)

        self.assertTrue(os.path.exists(os.path.join(os.getenv('VIRTUAL_ENV'),
                                       'etc', 'seedbox.conf')))

        options.initialize([])
        self.assertIsNotNone(cfg.CONF.config_file)
        self.assertIsNotNone(cfg.CONF.config_dir)
