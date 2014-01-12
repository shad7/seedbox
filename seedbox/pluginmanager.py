"""
Plugin Loading & Management.
"""
from __future__ import absolute_import
import os
import sys
import re
import logging
import time
import pkgutil
import itertools
import ordereddict

from oslo.config import cfg

from seedbox.action import add_action_handler
from seedbox import processmap
from seedbox import tasks as plugins_pkg

log = logging.getLogger(__name__)

__all__ = ['PluginWarning', 'PluginError', 'register_plugin', 'phase',
           'get_plugin_by_name', 'get_plugins']


class DependencyError(Exception):
    """

    .. py:exception:: DependencyError
        Plugin depends on a module that cannot be loaded.

    """

    def __init__(self, issued_by=None, missing=None, message=None,
                 silent=False):
        """

        :param str issued_by:   name of the plugin trying to do the import
        :param str missing:     name of the plugin or library that is missing
        :param str message:     user readable error message
        :param bool silent:     flag indicating how loudly to share
        """
        super(DependencyError, self).__init__()
        self.issued_by = issued_by
        self.missing = missing
        self._message = message
        self.silent = silent

    def _get_message(self):
        """
        retrieve message
        """
        if self._message:
            return self._message
        else:
            return 'Plugin `%s` requires dependency `%s`' % (self.issued_by,
                                                             self.missing)

    def _set_message(self, message):
        """
        sets message
        """
        self._message = message

    def has_message(self):
        """
        checks message exists
        """
        return self._message is not None

    message = property(_get_message, _set_message)

    def __str__(self):
        return '<DependencyError(issued_by=%r,missing=%r,\
                message=%r,silent=%r)>' % \
            (self.issued_by, self.missing, self.message, self.silent)


class DisabledPluginError(Exception):
    """

    .. py:exception:: DisabledPluginError
        raised when a plugin is configured to be disabled; forcefully stop
        additional loading efforts.

    """
    def __init__(self, value, logger=log, **kwargs):
        """
        :param str value:       a message to provide additional details
        :param object logger:   an instance of logger
        :param dict kwargs:     key-value inputs
        """
        super(DisabledPluginError, self).__init__()
        self.value = value
        self.log = logger
        self.kwargs = kwargs

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.value


class PluginWarning(Warning):
    """

    .. py:exception:: PluginWarning
        enables standard warning messages for plugins

    """
    def __init__(self, value, logger=log, **kwargs):
        """
        :param str value:       a message to provide additional details
        :param object logger:   an instance of logger
        :param dict kwargs:     key-value inputs
        """
        super(PluginWarning, self).__init__()
        self.value = value
        self.log = logger
        self.kwargs = kwargs

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.value


class PluginError(Exception):
    """

    .. py:exception:: PluginError
        enables standard error messages for plugins

    """
    def __init__(self, value, logger=log, **kwargs):
        """
        :param str value:       a message to provide additional details
        :param object logger:   an instance of logger
        :param dict kwargs:     key-value inputs
        """
        super(PluginError, self).__init__()
        self.value = value
        self.log = logger
        self.kwargs = kwargs

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.value


DEFAULT_PRIORITY = 128


def phase(name, priority=DEFAULT_PRIORITY):
    """

    .. py:decorator:: phase(name, priority)
        Set phase name and priority as attributes of the decorated target

    """
    def decorator(target):
        target.phase_name = name
        target.priority = priority
        return target
    return decorator


# Mapping of plugin name to PluginInfo instance (logical singletons)
plugins = {}


class PluginInfo(dict):
    """
    Allows accessing key/value pairs of this dictionary subclass via
    attributes. Also instantiates a plugin and initializes properties.
    """
    # Counts duplicate registrations
    dupe_counter = 0

    def __init__(self, plugin_class, name=None):
        """
        Register a plugin.

        :param class plugin_class:  a class object representing a plugin/Task
        :param str name:            a name associated with a plugin/Task
        """
        dict.__init__(self)

        if name is None:
            # Convention is to take camel-case class name and rewrite it to an
            # underscore form, e.g. 'PluginName' to 'plugin_name'
            name = re.sub('[A-Z]+', lambda i: '_' + i.group(0).lower(),
                          plugin_class.__name__).lstrip('_')

        # Set basic info attributes
        self.name = name
        self.phase_handlers = {}

        # Create plugin instance
        self.plugin_class = plugin_class
        self.plugin_module = (plugin_class.__module__).rsplit('.', 1).pop()
        self.instance = self.plugin_class()
        self.instance.plugin_info = self  # give plugin easy access to it self

        if self.name in plugins:
            PluginInfo.dupe_counter += 1
            log.critical('Error while registering plugin %s. %s' %
                         (self.name,
                             ('Plugin name %s is already registered'
                                 % self.name)))
        else:
            # don't even load the plugin if disabled
            if self.instance.disabled:
                log.info('during configuration %s was disabled', self.name)
                raise DisabledPluginError(
                    'disabled plugin based on configuration (%s)' % self.name)

            self.map_action_methods()
            plugins[self.name] = self

    def map_action_methods(self):
        """
        Search through the provided class and determine which methods are
        associated with an action and generate an Action for the method.
        Ignoring all private '_' methods.
        """
        import inspect

        plugin_valid = False
        log.trace('Check plugin for action methods [%s]',
                  self.plugin_class.__name__)
        for class_method in inspect.getmembers(self.plugin_class,
                                               predicate=inspect.ismethod):
            method_name = class_method[0]
            log.trace('method=[%s]', method_name)
            # ignore any method name that is private, doesn't matter if it is
            # single or double underscore. Just go to next method
            if method_name.startswith('_'):
                log.trace('method=[%s] is private; skipping', method_name)
                continue

            # now we need to convert method_name to an object, so that we
            # can access it and retrieve the decorated attributes; since we
            # just got the name from the class itself, there is no need to
            # check hasattr or set a default value on getattr
            method = getattr(self.instance, method_name)
            if not callable(method):
                log.trace('method=[%s] is not callable; skipping',
                          method_name)
                continue

            # retrieve values from action decorator if they exist;
            # if they are not found, or have used an incorrect type or value
            # then we will ignore the corresponding error and just continue
            # to the next method in the list
            try:
                log.trace('method=[%s] checking for decorated attributes',
                          method_name)
                handler_prio = _check_value('priority', method.priority)
                handler_phase = _check_value('phase', method.phase_name)
                if not handler_phase in processmap.get_run_phases():
                    raise ValueError(
                        'attribute [%s] has unsupported value [%s]; \
                         supported values: %s' % ('phase',
                                                  handler_phase,
                                                  processmap.get_run_phases())
                        )
                log.trace('method=[%s] decorated attributes found',
                          method_name)
                plugin_valid = True
            except ValueError as valerr:
                log.debug('method=[%s] decorated attribute has ValueError: %s',
                          method_name, valerr)
                continue
            except TypeError as tyerr:
                log.debug('method=[%s] decorated attribute has TypeErorr: %s',
                          method_name, tyerr)
                continue
            except AttributeError as aterr:
                log.debug('method=[%s] not decorated; AttributeError: %s',
                          method_name, aterr)
                continue
            except Exception as err:
                log.debug('method=[%s] not decorated; generic error: %s',
                          method_name, err)
                continue

            # now create the action and link phase to action
            action = add_action_handler('%s.%s' % (handler_phase, self.name),
                                        method, handler_prio)
            self.phase_handlers[handler_phase] = action
            log.trace('method=[%s] linked to action [%s] with priority [%d]',
                      method_name, action.name, handler_prio)

        if not plugin_valid:
            errmsg = ('class [%s] is not a valid plugin; no methods defined \
                       for a supported phase. Check @phase for proper \
                       configuration.' % self.plugin_class.__name__)
            log.trace(errmsg)
            raise PluginError(errmsg)

    def __getattr__(self, attr):
        """
        override getattr
        """
        if attr in self:
            return self[attr]
        return dict.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        """
        override setattr
        """
        self[attr] = value

    def __str__(self):
        """
        override str
        """
        return '<PluginInfo(name=%s)>' % self.name

    __repr__ = __str__


register_plugin = PluginInfo


def _check_value(name, val):
    """
    Need to verify if we have actual values of the correct type
    provided as inputs to our action decorator
    """
    if not isinstance(val, (basestring, int)):
        raise TypeError(
            'attribute [%s] value not string/int: [%s]' %
            (name, type(val).__name__))

    if isinstance(val, basestring):
        if not val:
            raise ValueError('attribute [%s] has no value [%s]' % (name, val))

        use_val = val.strip()
        if not use_val:
            raise ValueError(
                'attribute [%s] has empty value [%s]' % (name, use_val))
    else:
        # this means it is of type int, but just in case we will call
        # int function to make sure so we get ValueError if it is not
        # an actual int
        use_val = int(val)

    return use_val


def _strip_trailing_sep(path):
    """
    simple function to strip trailing separator
    """
    return path.rstrip("\\/")


def get_standard_plugins_path(user_paths=None):
    """
    Generates a list of locations from where to load plugins
    currently our tasks package is the only location for accessing plugins

    If the user provides specific paths, then we will attempt to access those
    and load those plugins as well.

    :param list user_paths: the directory paths provided by user to
                            search for plugins
    :returns:               directory paths where to access plugins
    :rtype:                 list
    """
    # Use standard default
    paths = []

    # Add tasks directory (plugins)
    paths.append(os.path.abspath(os.path.dirname(plugins_pkg.__file__)))

    # now add any paths provided by user
    for user_path in user_paths:
        if os.path.exists(user_path):
            paths.append(user_path)
        else:
            log.warning('plugin-path specified not found [%s]', user_path)

    return paths


def _load_plugins_from_dirs(dirs):
    """
    performs the actual loading of plugins from specified directory
    """

    log.trace('Trying to load plugins from: %s' % dirs)
    # add all dirs to plugins_pkg load path so that plugins are loaded
    # from provided directories
    plugins_pkg.__path__ = map(_strip_trailing_sep, dirs)
    for importer, name, ispkg in pkgutil.walk_packages(
            dirs, plugins_pkg.__name__ + '.'):
        if ispkg:
            continue
        # Don't load any plugins again if they are already loaded
        # This can happen if one plugin imports from another plugin
        if name in sys.modules:
            continue
        loader = importer.find_module(name)
        # Don't load from pyc files
        if not loader.filename.endswith('.py'):
            continue
        try:
            loaded_module = loader.load_module(name)
        except DependencyError as deperr:
            if deperr.has_message():
                msg = deperr.message
            else:
                msg = 'Plugin `%s` requires `%s` to load.' % (
                    deperr.issued_by or name,
                    deperr.missing or 'N/A')
            if not deperr.silent:
                log.warning(msg)
            else:
                log.debug(msg)
        except DisabledPluginError as dperr:
            log.warning('Plugin %s was not loaded. %s', name, dperr)
        except PluginError as plugerr:
            log.critical('Plugin %s was not loaded. %s', name, plugerr)
            log.exception(plugerr)
        except ImportError as imperr:
            log.critical('Plugin `%s` failed to import dependencies', name)
            log.exception(imperr)
        except Exception as err:
            log.critical('Exception while loading plugin %s', name)
            log.exception(err)
            raise
        else:
            log.debug('Loaded module %s from %s',
                      name, loaded_module.__file__)


def load_plugins():
    """
    Load plugins from the standard plugin paths.
    """

    start_time = time.time()
    _load_plugins_from_dirs(get_standard_plugins_path(cfg.CONF.plugin_paths))
    took = time.time() - start_time
    log.trace('Plugins took %.2f seconds to load' % took)

    # generate a map by phase of each of the plugins we just
    # loaded so the Manager knows what we have to offer
    phasemap = ordereddict.OrderedDict()
    for phase in processmap.get_run_phases():
        phasemap[phase] = get_plugins(phase)

    return phasemap


def get_plugins(phase=None):
    """
    Retrieve a list of plugins; all if no input provided else those that match
    the criteria provided

    :param str phase:   the name of the phase that a plugin supports
                        (default: None)

    :returns:           PlugInfo instances
    :rtype:             iterable
    """
    def matches(plugin):
        """
        filters out plugins that don't match
        """
        if phase and not phase in plugin.phase_handlers:
            log.trace('Phase resulted in filtering out plugin: [%s]', plugin)
            return False
        return True
    return itertools.ifilter(matches, plugins.itervalues())


def get_plugin_by_name(name):
    """
    Get plugin by name, preferred way since this structure may be changed at
    some point.
    @UNUSED

    :param str name:    name of a plugin
    """
    if not name in plugins:
        raise DependencyError(missing=name, message='Unknown plugin %s' % name)
    return plugins[name]
