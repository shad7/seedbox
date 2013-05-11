"""
extension to logging
"""
from __future__ import absolute_import
import logging, logging.config, logging.handlers
import os, sys

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

# a simple hack to make sure as a developer you can see all trace action
# that happens prior to logging getting configured.
if '--dev' in sys.argv:
    rootlog = logging.getLogger()
    rootlog.setLevel(TraceLogger.TRACE)
    streamhandle = logging.StreamHandler(sys.stdout)
    simpleformatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamhandle.setFormatter(simpleformatter)
    rootlog.addHandler(streamhandle)



def configure(loglevel=logging.INFO, logfile='seedbox.log', resourceloc=None, devmode=False):
    """
    configure all logging for this execution
    """

    use_resource = resourceloc
    if not use_resource:
        if sys.platform.startswith('win'):
            # On windows look in ~/seedbox as well, as explorer does not let you create a 
            # folder starting with a dot
            default_path = os.path.join(os.path.expanduser('~'), 'seedbox')
        else:
            default_path = os.path.join(os.path.expanduser('~'), '.seedbox')

        # if the user folder exists; then we'll use it if we were not provided one
        if os.path.exists(default_path):
            use_resource = default_path
        else:
            # if all else fails then we just use the current working directory
            use_resource = os.getcwd()

    if devmode:
        logging.config.fileConfig(os.path.join(use_resource, 'logging.cfg'), disable_existing_loggers=False)
    else:
        logger = logging.getLogger()
        logger.setLevel(loglevel)

        logloc_filename = os.path.join(use_resource, logfile)
        handler = logging.handlers.RotatingFileHandler(logloc_filename, maxBytes=1000 * 1024, backupCount=9)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # shut off logging from 3rd party frameworks
        xlogger = logging.getLogger('xworkflows')
        xlogger.setLevel(logging.ERROR)
