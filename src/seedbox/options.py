"""
Manages all Options for system.
"""
from __future__ import absolute_import
from argparse import ArgumentParser, SUPPRESS
from configparser import ConfigParser
import logging
import os, sys

log = logging.getLogger(__name__)

DEFAULT_CFG_FILENAME = 'seedbox.cfg'
DEFAULT_LOG_FILENAME = 'seedbox.log'
DEFAULT_LOG_LEVEL = 'info'

class _Namedspace(object):
    """
    simple namespace holder
    """
    def __init__(self, **kwargs):
        """
        This is how we initialize our instance variables. If we are provided with
        any inputs then we will add those as attributes to ourself.

        Side-effect: A flag was needed to identify if we have been configured or
            not because we are leveraged by argparse to set any command line
            arguments onto us. So hasattr has to get an exception when an
            attribute does not exist. But in general use after we have been
            configured, we just want to simply return None when the attribute
            is missing. Therefore we set our hidden flag to false initially, and
            once we are configured, we will flip the flag to true. For those
            instances that pass in values to start with, we will go ahead and flip
            the flag for them. For those that manually set attributes via 
            setattr, they will need to manually flip the flag via configured()
            method.
        """
        self.__configured = False
        if kwargs:
            self.add(**kwargs)

    __hash__ = None

    def add(self, **kwargs):
        """
        Provides the ability to add a list of attributes to ourself in 
        bulk other than during init(). Even init() will call us so that
        not matter when this happens it is consistent.
        """
        self.__configured = True
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def configured(self):
        """
        handles the manual flipping of the flag after configuration is completed.
        """
        self.__configured = True

    def __getattr__(self, name):
        """
        The normal functionality for this would be to throw an
        AttributeError if the name does not exist in the dict.
        But we are scoping this to represent information from
        within configuration file. That means some sections might
        not have the same set of attributes. Instead of each piece
        of code trying to check for AttributeError, we will perform
        a get on the dict and therefore return None when the name/key
        is not within our attribute dict.
        Update: Need to raise the exception as normal otherwise hasattr
        will cause issues as argparse adds 'hidden' attributes in some
        scenarios. And then tries to remove them. So if hidden, then we
        will raise exception.
        """
        if self.__configured:
            return self.__dict__.get(name)
        return object.__getattribute__(self, name)

    def __eq__(self, other):
        """
        provide implementation
        """
        return vars(self) == vars(other)

    def __ne__(self, other):
        """
        provide implementation
        """
        return not (self == other)

    def __contains__(self, key):
        """
        provide implementation
        """
        return key in self.__dict__

    def __repr__(self):
        """
        provide implementation
        """
        type_name = type(self).__name__
        arg_strings = []
        for arg in self._get_args():
            arg_strings.append(repr(arg))
        for name, value in self._get_kwargs():
            # if I went through the trouble to 'hide' it by using
            # double underscore, I do not want it as part of the visible
            # representation of the instance either!
            if name.startswith('_Namedspace__'):
                continue
            arg_strings.append('%s=%r' % (name, value))
        return '%s(%s)' % (type_name, ', '.join(arg_strings))

    def _get_kwargs(self):
        """
        provide implementation
        """
        return sorted(self.__dict__.items())

    def _get_args(self):
        """
        provide implementation
        """
        return []

# end _Namedspace

class ConfigOptions(_Namedspace):
    """
    Create a combined solution for brining both arparse and configparser together.
    I prefer being able to access the values like an attribute vs. figure out
    what section I need, then check if key exists, and then convert to correct type.

    Also it would be nice to simply pass a method a set based on namespace (module name)
    vs. passing the entire configuration set which is not applicable for most areas in the
    code.
    """

    def __init__(self, appversion):
        """
        process command line inputs, using those inputs and some defaults; attempt
        to load config file. That is where the magic will start, then we will need
        to merge the results together and generate a namespace for each of the 
        'sections' identified within configuration file.
        """
        super(ConfigOptions, self).__init__()
        self.appversion = appversion
        self._namedspaces = {}
        self._basespace = _Namedspace()
        self._configparser = ConfigParser(allow_no_value=True)

        _load_args(self._basespace, appversion)
        # need to set the flag that we are configured so accessing attributes
        # results in a value. See parent class for details.
        self._basespace.configured()

    def _generate_namespaces(self):
        """
        generate namespaces for configs
        """
        # to use interpolation, we have to call items on the parser otherwise we get back
        # just raw data with all the placeholders showing up
        self._basespace.add(**_validate_and_format(self._configparser.items('DEFAULT')))

        for sect in self._configparser.sections():
            self._namedspaces[sect] = _Namedspace(**_validate_and_format(self._configparser.items(sect)))

    def load_configs(self):
        """
        Now we are ready to load the configuration files
        """
        _find_configs(self._configparser, self._basespace)
        self._generate_namespaces()

    def get_configs(self, module_name=None):
        """
        return configs as requested
        """
        return self._namedspaces.get(module_name, self._basespace)


# end ConfigOptions

_boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                   '0': False, 'no': False, 'false': False, 'off': False}

def _set_type(value):
    """
    a workaround for a problem where we set flags using strings in a config file
    but we really need them to be booleans when we consume them. Also handles
    converting values to their proper types so they are consumable.
    """
    if value.lower() in _boolean_states:
        return _boolean_states[value.lower()]
    elif isinstance(value, int):
        return int(value)
    elif isinstance(value, list):
        return list(value)
    else:
        if not value:
            return None
        return str(value)

def _verify_path(path_entry):
    """
    verify a path, if it exists make sure it is 
    and absolute path and return. else None
    """
    if path_entry and os.path.exists(path_entry):
        if os.path.isabs(path_entry):
            return path_entry
        else:
            return os.path.realpath(path_entry)
    else:
        return None

def _verify_paths(path_list):
    """
    verify list of paths; return list -- it will also handle splitting any string list
    that is provided vs. an actual list. 
    """
    to_verify_paths = []
    # if we got a list then simply use it
    if isinstance(path_list, list):
        to_verify_paths = path_list
    # if we got a string then we will need to split it
    if isinstance(path_list, basestring):
        # check for the following list of separators
        # if found in string, then split it; else try
        # the next one.
        for sep in [',', ';']:
            if path_list.find(sep) != -1:
                to_verify_paths = path_list.split(sep)
        # if after looping try splitting based on just whitespace
        if not to_verify_paths:
            to_verify_paths = path_list.split()

        # strip away excess whitespace after the splits
        to_verify_paths[:] = map(str.strip, to_verify_paths)

    # if after all those attempts we will be left with an empty list
    # to process and as a result we will return an empty list back.

    valid_items = []
    for item in to_verify_paths:
        verified_item = _verify_path(item)
        if verified_item:
            valid_items.append(verified_item)

    return valid_items

def _to_list(attributes):
    """
    convert a comma separated list into an actual list
    """
    attr_list = []

    if isinstance(attributes,  basestring):
        # check for the following list of separators
        # if found in string, then split it; else try
        # the next one.
        for sep in [',', ';']:
            if attributes.find(sep) != -1:
                attr_list = attributes.split(sep)
        # if after looping try splitting based on just whitespace
        if not attr_list:
            attr_list = attributes.split()

        # strip away excess whitespace after the splits
        attr_list[:] = map(str.strip,  attr_list)

    # now send back the results; empty list or not
    return attr_list

def _validate_and_format(configs):
    """
    convert the items within each section of the configuration file into a dict
    while also converting the value to a proper type (boolean, list, str, etc.)
    Also validate that required common entries are present, and convert knowns
    paths into absolute paths when they are relative, while also removing any
    non-existent paths to avoid issues later.

    args:
        configs: the list of tuples (items) from each section of the configuration
            file that needs to be converted to dict.
    exception:
        ValueError: if any of the required entries within the configuration
            file are not found or found to be missing or invalid.
    """
    config_group = {}
    missing_required = []

    for key, value in configs:
        config_group[str(key)] = _set_type(value)
    log.trace('updated group: %s', config_group)


    # Need to verify the path and convert to absolute path if relative.
    # if the entry is missing all together, then None will be sent for
    # verification and None will be return. So the entry will be always
    # a full and complete path or None. If None then we'll raise an error
    # down below. 
    config_group['torrent_path'] = _verify_path(config_group.get('torrent_path'))
    if not config_group.get('torrent_path'):
        log.debug('torrent_path was not supplied in the configuration file')
        missing_required.append('TORRENT_PATH')

    config_group['incomplete_path'] = _verify_path(config_group.get('incomplete_path'))
    if not config_group.get('incomplete_path'):
        log.debug('incomplete_path was not supplied in the configuration file')
        missing_required.append('INCOMPLETE_PATH')

    config_group['media_paths'] = _verify_paths(config_group.get('media_paths'))
    if not config_group.get('media_paths'):
        log.debug('media_paths was not supplied in the configuration file')
        missing_required.append('MEDIA_PATHS')

    # plugin paths is optional; so if it exists it will be a list separated
    # by commas. Unable to split None, so the default will be an empty string
    # which when split will result in an empty list. If the verified list is
    # empty then the verified list will also be empty. If the items in the list
    # are not valid then it will again be an empty list.
    config_group['plugin_paths'] = _verify_paths(config_group.get('plugin_paths', ''))

    # disabled phases is optional; so if it exists it will be a list separated
    # by commas. Unable to split None, so the default will be an empty string
    # which when split will result in an empty list. If the verified list is
    # empty then the verified list will also be empty.
    config_group['disabled_phases'] = _to_list(config_group.get('disabled_phases', ''))

    log.trace('final config group: %s', config_group)
    if missing_required:
        raise ValueError('missing required input(s) [%s] not supplied in configuration file)' % missing_required)

    return config_group


def _find_configs(parser, args):
    """
    look for the config file in all the common locations so we can load it
    and figure out how we should execute

    args:
        parser: configparser instance that will be used to process the actual 
            configuration file once we find it of course.
        args: any inputs we got back from the command line that will used to find
            the configuration file (rcfile or resource_path)
    exceptions:
        IOError: if no configuration file found
    """

    log.trace('ready to load configuration files')

    possible = []
    # if the user specified a path within rcfile then we will try to use it;
    # if there is no dirname that means it is just the default filename only.
    if os.path.dirname(args.rcfile):
        log.debug('using command line specified configuration file %s', args.rcfile)
        if os.path.isabs(args.rcfile):
            # explicit path given, don't try anything too fancy
            possible.append(args.rcfile)
        else:
            # specified sure, but it was a relative path so we need 
            # expand it out otherwise things will fail
            possible.append(os.path.realpath(args.rcfile))
    elif args.resource_path and os.path.exists(args.resource_path):
        log.debug('using command line specified resource location %s', args.resource_path)
        # so we will look in this location only
        if os.path.isabs(args.resource_path):
            possible.append(args.resource_path)
        else:
            # specified sure, but it was a relative path so we need 
            # expand it out otherwise things will fail later
            possible.append(os.path.realpath(args.resource_path))
    else:
        log.debug('no configuration details specified, checking usual locations')
        # normal lookup locations
        possible.append(os.path.dirname(os.path.abspath(sys.path[0])))
        possible.append(os.getcwd())
        possible.append(sys.path[0])
        possible.append(os.path.join(os.path.expanduser('~'), '.seedbox'))
        if sys.platform.startswith('win'):
            # On windows look in ~/flexget as well, as explorer does not let you create a folder starting with a dot
            possible.append(os.path.join(os.path.expanduser('~'), 'seedbox'))

    log.trace('possibles: %s', possible)
    for location in possible:
        log.debug('checking location %s', location)
        # if the user specified an actual location and file via rcfile
        # then there is nothing to add, but if we are looking at a location
        # only (ie directory) then we need to append the default filename
        if os.path.isdir(location):
            config_file = os.path.join(location, DEFAULT_CFG_FILENAME)
        else:
            config_file = location
        log.trace('checking file %s', config_file)
        if os.path.exists(config_file):
            log.trace('file exists: %s', config_file)
            # load it up
            found = parser.read(config_file)
            if not found:
                log.warn('loading of config file %s had no results; both rare and strange', config_file)
                continue
            log.debug('loaded config file found: [%s]', found)
            # need to set the resource path (include in args and configuration file)
            parser.set('DEFAULT', 'resource_path', os.path.dirname(config_file))
            args.resource_path = os.path.dirname(config_file)
            log.debug('setting resource path to %s', os.path.dirname(config_file))
            # if this break is never reached then the else block will be executed
            # and the corresponding exception will be raised
            break
    else:
        log.error('tried to read from %s but no configuration file found', possible)
        raise IOError('no configuration file found; searched %s' % possible)

def _load_args(namespace, app_version):
    """
    setups what command arguments there are, and then processes the input on execution

    args:
        namespace: a class instance that will hold all the command arguments as attributes
            once the command has been processed.
        app_version: the version of the application
    returns:
        N/A
    """

    prog_desc = 'This program is the main interface for executing a series of \
        tasks in sequence. The types of task are intended for managing \
        torent files and the associated media files on a seedbox.'

    parser = ArgumentParser(description=prog_desc)

    parser.add_argument('--version', action='version',
        version='%(prog)s '+app_version)

    parser.add_argument('--resource', dest='resource_path', metavar='RESOURCE_PATH',
        help='path where all resource files are located; config file, logfile, etc.')
    parser.add_argument('--rcfile', dest='rcfile', metavar='RESOURCE_FILE', default=DEFAULT_CFG_FILENAME,
        help='specify a configuration file (location is resource path)')

    parser.add_argument('--logfile', dest='logfile', metavar='LOG_FILE', default=DEFAULT_LOG_FILENAME,
        help='specify name of log file (location is resource path)')
    parser.add_argument('--loglevel', dest='loglevel', metavar='LOG_LEVEL', default=DEFAULT_LOG_LEVEL,
        choices=['none', 'critical', 'error', 'warning', 'info', 'debug', 'trace'],
        help=SUPPRESS)

    parser.add_argument('--reset', action='store_true',
        help='DANGER: deletes the database cache and everything starts over')
    parser.add_argument('--retry', action='store_true',
        help='only executes entries that failed previously')

    parser.add_argument('--dev', action='store_true', help=SUPPRESS)

    log.trace('all known arguments added to parser....now parse')
    # the namespace is an object that will actually hold a reference to each value in
    # a corresponding attribute field. dest=attribute name
    parser.parse_args(namespace=namespace)
    log.debug('found command line arguments: [%s]', namespace)


def initialize(appversion):
    """
    just a convience method, and allows us to expand over time as required w/o changing
    our manager module.
    creates an instance of ConfigOptions which will be our handle to arguments passed
    on the command line, and later references to the namespaces holding the
    configuration file that is loaded.

    args:
        appversion: string representing the current version of application. Used as part of help
            and --version commands.
    returns:
        and instance ConfigOptions which will act as the handle/container for all
        options/configurations provided via command line and configuration file.
    """
    log.trace('initializing setup...processing command line arguments')
    return ConfigOptions(appversion)

