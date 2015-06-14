import logging
import logging.handlers
import os
import shutil
import tempfile

import fixtures
from oslo_config import cfg
from testtools import matchers

from seedbox import service
from seedbox.tests import test


class ServiceTest(test.ConfiguredBaseTestCase):

    cfg_data = []
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

    log_cfg_data = []
    log_cfg_data.append('[loggers]\n')
    log_cfg_data.append('keys = root\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[logger_root]\n')
    log_cfg_data.append('level = DEBUG\n')
    log_cfg_data.append('handlers = consoleHandler\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[formatters]\n')
    log_cfg_data.append('keys = simple\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[formatter_simple]\n')
    log_cfg_data.append(
        'format = %(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[handlers]\n')
    log_cfg_data.append('keys = consoleHandler\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[handler_consoleHandler]\n')
    log_cfg_data.append('class=StreamHandler\n')
    log_cfg_data.append('level=DEBUG\n')
    log_cfg_data.append('formatter=simple\n')
    log_cfg_data.append('args=(sys.stdout,)\n')

    def test_setup_logging(self):
        del logging.getLogger().handlers[:]
        service._setup_logging()
        self.assertEqual(logging.getLogger().getEffectiveLevel(),
                         logging.INFO)
        self.assertEqual(logging.getLogger('sqlalchemy').getEffectiveLevel(),
                         logging.ERROR)

        for hndler in logging.getLogger().handlers:
            self.assertThat(
                hndler,
                matchers.MatchesAny(
                    matchers.IsInstance(logging.handlers.RotatingFileHandler),
                    matchers.IsInstance(logging.StreamHandler),
                    matchers.IsInstance(logging.NullHandler)))

    def test_setup_logging_no_logfile(self):
        self.CONF.set_override('logfile', None)
        del logging.getLogger().handlers[:]
        service._setup_logging()
        for hndler in logging.getLogger().handlers:
            self.assertThat(
                hndler,
                matchers.MatchesAny(
                    matchers.IsInstance(logging.StreamHandler),
                    matchers.IsInstance(logging.NullHandler)))

    def test_setup_logging_cron(self):
        self.CONF.set_override('cron', True)
        del logging.getLogger().handlers[:]
        service._setup_logging()
        for hndler in logging.getLogger().handlers:
            self.assertThat(
                hndler,
                matchers.MatchesAny(
                    matchers.IsInstance(logging.handlers.RotatingFileHandler),
                    matchers.IsInstance(logging.NullHandler)))

    def test_setup_logging_no_logging(self):
        self.CONF.set_override('logfile', None)
        self.CONF.set_override('cron', True)
        del logging.getLogger().handlers[:]
        service._setup_logging()
        for hndler in logging.getLogger().handlers:
            self.assertThat(
                hndler,
                matchers.MatchesAny(
                    matchers.IsInstance(logging.NullHandler)))

    def test_setup_logging_via_file(self):
        logfile = self.create_tempfiles([('seedbox',
                                          ''.join(self.log_cfg_data))],
                                        '.log')[0]
        self.CONF.set_override('logconfig', logfile)
        service._setup_logging()
        root = logging.getLogger()
        self.assertEqual(logging.DEBUG, root.getEffectiveLevel())

    def test_configure_with_venv(self):

        cfg.CONF.reset()
        cfg.CONF.import_opt('base_client_path', 'seedbox.options')

        vdir = tempfile.mkdtemp()
        dirname = os.path.join(vdir, 'etc')
        os.mkdir(dirname)

        with fixtures.EnvironmentVariable('VIRTUAL_ENV', vdir):
            cfgfile = self.create_tempfiles(
                [(os.path.join(dirname, 'seedbox'),
                  ''.join(self.cfg_data))])[0]
            self.addCleanup(shutil.rmtree, os.path.dirname(cfgfile), True)
            service._configure([])
            self.assertEqual(cfg.CONF.base_client_path,
                             '/home/shad/torrent-test/deluge')

    def test_configure_without_venv(self):

        cfg.CONF.reset()
        cfg.CONF.import_opt('base_client_path', 'seedbox.options')

        with fixtures.EnvironmentVariable('VIRTUAL_ENV'):
            cfgfile = self.create_tempfiles(
                [(os.path.join(os.path.expanduser('~'),
                               'seedbox'),
                    ''.join(self.cfg_data))])[0]
            self.addCleanup(shutil.rmtree, os.path.dirname(cfgfile), True)
            service._configure([])
            self.assertEqual(cfg.CONF.base_client_path,
                             '/home/shad/torrent-test/deluge')

    def test_prepare_service(self):

        cfg.CONF.reset()
        cfg.CONF.import_opt('base_client_path', 'seedbox.options')

        with fixtures.EnvironmentVariable('VIRTUAL_ENV'):
            cfgfile = self.create_tempfiles(
                [(os.path.join(os.path.expanduser('~'),
                               'seedbox'),
                    ''.join(self.cfg_data))])[0]
            self.addCleanup(shutil.rmtree, os.path.dirname(cfgfile), True)
            service.prepare_service([])

        self.assertEqual(logging.getLogger('sqlalchemy').getEffectiveLevel(),
                         logging.ERROR)
        self.assertEqual(cfg.CONF.base_client_path,
                         '/home/shad/torrent-test/deluge')
