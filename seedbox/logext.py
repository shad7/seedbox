"""
Configures logging module for the entire application, setting default log
levels for library code.
"""
import logging
import logging.config
import logging.handlers
import os

from oslo.config import cfg
import six

if hasattr(logging, 'NullHandler'):
    NullHandler = logging.NullHandler
else:
    # NullHandler added in Python 2.7
    class NullHandler(logging.Handler):
        """
        Copied from Python 2.7 logging module
        """
        def handle(self, record):
            """
            @see logging module
            :param record:
            """
            pass

        def emit(self, record):
            """
            @see logging module
            :param record:
            """
            pass

        def createLock(self):
            """
            @see logging module
            """
            self.lock = None

DEFAULT_LOG_FILENAME = 'seedbox.log'
DEFAULT_LOG_LEVEL = 'info'

CLI_OPTS = [
    cfg.StrOpt('logfile',
               metavar='LOG_FILE',
               default=DEFAULT_LOG_FILENAME,
               help='specify name of log file default: %(default)s'),
    cfg.StrOpt('loglevel',
               metavar='LOG_LEVEL',
               default=DEFAULT_LOG_LEVEL,
               help='specify logging level to log messages: %(choices)s',
               choices=['none',
                        'critical',
                        'error',
                        'warning',
                        'info',
                        'debug',
                        'trace']),
    cfg.StrOpt('logconfig',
               metavar='LOG_CONFIG',
               help='specific path and filename of logging configuration \
                    (override defaults)'),
]

cfg.CONF.register_cli_opts(CLI_OPTS)


# add default handler to make sure that cli only actions do not
# generate logging handler errors
logging.getLogger().addHandler(NullHandler())

DEFAULT_LIBRARY_LOG_LEVEL = {'xworkflows': logging.ERROR,
                             'stevedore': logging.ERROR,
                             'sqlalchemy': logging.ERROR,
                             'migrate': logging.ERROR,
                             }


def configure():
    """
    configure all logging for this execution
    """

    if cfg.CONF.logconfig and os.path.exists(cfg.CONF.logconfig):
        logging.config.fileConfig(cfg.CONF.logconfig,
                                  disable_existing_loggers=False)
    else:
        logger = logging.getLogger()
        logger.setLevel(cfg.CONF.loglevel.upper())

        logloc_filename = os.path.join(cfg.CONF.config_dir, cfg.CONF.logfile)
        handler = logging.handlers.RotatingFileHandler(
            logloc_filename, maxBytes=1000 * 1024, backupCount=9)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # shut off logging from 3rd party frameworks
        for xlib, xlevel in six.iteritems(DEFAULT_LIBRARY_LOG_LEVEL):
            xlogger = logging.getLogger(xlib)
            xlogger.setLevel(xlevel)
