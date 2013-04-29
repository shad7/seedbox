#!/usr/bin/python

from configparser import ConfigParser
import logging, logging.config
import os, sys

__version__ = '0.1'


#startup_path = os.path.dirname(os.path.abspath(sys.path[0]))
#home_path = os.path.expanduser('~')
#current_path = os.getcwd()
#exec_path = sys.path[0]
#
#print 'startup: [%s]' % startup_path
#print 'home: [%s]' % home_path
#print 'current: [%s]' % current_path
#print 'exec: [%s]' % exec_path
#
#print 'abs sys.path[0] = %s' % os.path.abspath(sys.path[0])
#print 'exec split = %s + %s' % os.path.split(exec_path)
#print 'current split = %s + %s' % os.path.split(current_path)
#print 'home split = %s + %s' % os.path.split(home_path)


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
logging.config.fileConfig('logging.cfg', disable_existing_loggers=False)

import argparse
import seedbox.options as opt_loader


class Core(argparse.Namespace):
    pass

log = logging.getLogger('seedbox.options')
log.setLevel(logging.DEBUG)

configs = opt_loader.ConfigOptions(__version__)

defaults = configs.get_configs()
print defaults
print defaults.disabled

configs.load_configs()

defaults = configs.get_configs()
print defaults
print defaults.disabled

print '\n\n'
filedelete = configs.get_configs('filedelete')
print filedelete
print filedelete.disabled


exit(0)

configs = opt_loader.initialize(__version__)

#print 'configs: %s' % configs.defaults()

core = Core()

arggroups = []
coreparser = argparse.ArgumentParser()
coreparser.set_defaults(**configs.defaults())
coreargs = coreparser.parse_args(namespace=core)
arggroups.append(coreargs)

for sect in configs.sections():
    print '\n'
    print 'sect %s' % sect
    new_class = type(str(sect).capitalize(), (argparse.Namespace,), dict(argparse.Namespace.__dict__))
    print dict(configs.items(sect))
    parser = argparse.ArgumentParser()
    parser.set_defaults(**dict(configs.items(sect)))
    args = parser.parse_args(namespace=new_class())
    print '*********************'
    print args
    print '*********************'
    arggroups.append(args)

for arg in arggroups:
    print '++++++++++++++++++++++++++'
    print 'arg: %s' % arg
    print '++++++++++++++++++++++++++'

exit(0)


plug_attrs = {
    'dryrun': False,
    'verbose': False,
    'progress': False,
    'perms': True,
    'delayupdates': True,
    'recursive': True,
    'chmod': None,
    'logfile': None,
    'identity': None,
    'port': None,
    'sync_directory': None,
    'remote_directory': None,
}
###
print '********************************************************'
print 'default attribute values: '
for key, value in plug_attrs.items():
    print '%s:%s' % (key, value)

print '********************************************************'
###
for attr_key in plug_attrs.keys():
    print 'checking key: %s' % attr_key
    if hasattr(configs, attr_key):
        print 'key found in config: %s' % attr_key
        config_val = getattr(configs, attr_key)
        print 'value from config: %s' % config_val
        if config_val is not None:
            print 'value from config is not None; setting as our attr'
            plug_attrs[attr_key] = config_val
        else:
            print 'value from config is None; skipping...'
    else:
        print 'key not found in config %s' % attr_key

###
print '********************************************************'
print 'updated attribute values:'
for key, value in plug_attrs.items():
    print '%s:%s' % (key, value)

print '********************************************************'

