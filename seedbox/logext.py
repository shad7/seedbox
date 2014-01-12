"""
logging module that provides an extension to the python logging module
by adding a more fine grained log level (TRACE), and then configures
logging for the entire application.
"""
from __future__ import absolute_import
import logging
import logging.config
import logging.handlers
import os
from oslo.config import cfg

DEFAULT_LOG_FILENAME = 'seedbox.log'
DEFAULT_LOG_LEVEL = 'info'

CLI_OPTS = [
    cfg.StrOpt('logfile',
               metavar='LOG_FILE',
               default=DEFAULT_LOG_FILENAME,
               deprecated_group='DEFAULT',
               help='specify name of log file (location is resource path)'),
    cfg.StrOpt('loglevel',
               metavar='LOG_LEVEL',
               default=DEFAULT_LOG_LEVEL,
               deprecated_group='DEFAULT',
               help='specify logging level to log messages at',
               choices=['none',
                        'critical',
                        'error',
                        'warning',
                        'info',
                        'debug',
                        'trace']),
    cfg.StrOpt('logconfig',
               metavar='LOG_CONFIG',
               deprecated_group='DEFAULT',
               help='specific path and filename of logging configuration \
                    (override defaults)'),
]

cfg.CONF.register_cli_opts(CLI_OPTS)


# adding logging extension here given how minimal this is
# didn't seem to make sense to create a whole module for something
# so simple; if things change later we can move it then
class TraceLogger(logging.Logger):
    """
    Need to keep some low level logging messages included in case a bug
    ever pops up in the future, but this gives me the ability to separate
    tracing the propram from the actual basic debugging.
    """

    # a bit more detail than normal debug
    TRACE = 5

    def trace(self, msg, *args, **kwargs):
        """
        Log at TRACE level (more detailed than DEBUG).
        """
        self.log(TraceLogger.TRACE, msg, *args, **kwargs)


# Set our custom logger class as default; need to make sure
# the class has been defined before we set this; then add corresponding
# level to be supported; then do the default configuring from our default
# configuration file. all done
logging.setLoggerClass(TraceLogger)
logging.addLevelName(TraceLogger.TRACE, 'TRACE')

# add default handler to make sure that cli only actions do not
# generate logging handler errors
logging.getLogger().addHandler(logging.NullHandler())


def configure():
    """
    configure all logging for this execution
    """

    if cfg.CONF.logconfig and os.path.exists(cfg.CONF.logconfig):
        logging.config.fileConfig(cfg.CONF.logconfig,
                                  disable_existing_loggers=False)
    else:
        logger = logging.getLogger()
        logger.setLevel(logging.getLevelName(cfg.CONF.loglevel.upper()))

        logloc_filename = os.path.join(cfg.CONF.config_dir, cfg.CONF.logfile)
        handler = logging.handlers.RotatingFileHandler(
            logloc_filename, maxBytes=1000 * 1024, backupCount=9)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # shut off logging from 3rd party frameworks
        xlogger = logging.getLogger('xworkflows')
        xlogger.setLevel(logging.ERROR)
