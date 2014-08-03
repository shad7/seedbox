import logging
import os

from seedbox.tests import test
from seedbox import logext


class LogextTest(test.ConfiguredBaseTestCase):

    CFG_FILE = 'logging.cfg'

    cfg_data = []
    cfg_data.append('[loggers]\n')
    cfg_data.append('keys = root\n')
    cfg_data.append('\n')
    cfg_data.append('[logger_root]\n')
    cfg_data.append('level = DEBUG\n')
    cfg_data.append('handlers = consoleHandler\n')
    cfg_data.append('\n')
    cfg_data.append('[formatters]\n')
    cfg_data.append('keys = simple\n')
    cfg_data.append('\n')
    cfg_data.append('[formatter_simple]\n')
    cfg_data.append(
        'format = %(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
    cfg_data.append('\n')
    cfg_data.append('[handlers]\n')
    cfg_data.append('keys = consoleHandler\n')
    cfg_data.append('\n')
    cfg_data.append('[handler_consoleHandler]\n')
    cfg_data.append('class=StreamHandler\n')
    cfg_data.append('level=DEBUG\n')
    cfg_data.append('formatter=simple\n')
    cfg_data.append('args=(sys.stdout,)\n')

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

    def test_configure(self):
        logext.configure()
        self.assertEqual(logging.getLogger('xworkflows').getEffectiveLevel(),
                         logging.ERROR)

    def test_configure_via_file(self):

        location = os.path.expanduser('~')
        self._write_cfg_file(location)

        self.CONF.set_override('logconfig',
                               os.path.join(location, self.CFG_FILE))

        logext.configure()
        root = logging.getLogger()
        self.assertEqual(logging.DEBUG, root.getEffectiveLevel())
        self._delete_cfg_file(location)
