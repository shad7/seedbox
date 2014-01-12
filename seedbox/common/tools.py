"""
Holds a group of tools useful by all modules.
"""
import logging
import os
import re
from six import moves

log = logging.getLogger(__name__)

# Traditional
SYS_TRADITIONAL_NAME = 'traditional'
SYS_TRADITIONAL = 1024
# SI
SYS_SI_NAME = 'si'
SYS_SI = 1000

DEFAULT_SYSTEM = SYS_TRADITIONAL_NAME
SYSTEMS = [SYS_TRADITIONAL_NAME, SYS_SI_NAME]
SYSTEM_MAP = {SYS_TRADITIONAL_NAME: SYS_TRADITIONAL, SYS_SI_NAME: SYS_SI}

DEFAULT_INT = -99999

BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                  '0': False, 'no': False, 'false': False, 'off': False}


def to_bool(value):
    """
    converts the variety of possible values used to represent true/false to
    and actual recognized python boolean
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, basestring) and value.lower() in BOOLEAN_STATES:
        return BOOLEAN_STATES[value.lower()]
    if isinstance(value, int) and value in [0, 1]:
        return (True if value else False)

    # if value wasn't a boolean or a boolean like value
    # we are simply going to check if not None which will result
    # in a True/False.
    return value is not None


def to_list(value, separator=None):
    """
    converts a value (delimited most likely) to an actual list
    """
    delimiters = [',', ';']
    if separator:
        delimiters.append(separator)

    results = []
    # if we got an actual list just send it back as-is
    if isinstance(value, list):
        return value
    # if we got a string then we will need to split it
    if isinstance(value, basestring):
        # check for the following list of separators
        # if found in string, then split it; else try
        # the next one.
        for sep in delimiters:
            if value.find(sep) != -1:
                results = value.split(sep)
                break   # we got our sep now get out
        # if no results after looping try splitting based on just whitespace
        if not results:
            results = value.split()

        # strip away excess whitespace after the splits
        results[:] = map(str.strip, results)

    # we'll either send back an empty list or list based on splitting
    return results


def list_to_str(values):
    """
    converts a list to a delimited string list
    """
    result = None

    # if we get an actual list simply join and store as delimited list
    if values and isinstance(values, list):
        result = ','.join(values)

    # if the values are already a delimited list of values then use as-is
    elif values and isinstance(values, basestring) and values.find(',') != -1:
        result = values

    # if the values missing or not of correct format; we could throw
    # a ValueError but for now we will simply set the value to None
    return result


def to_int(value):
    """
    makes sure the value is an int, if not result will be a default int
    """
    if value is not None and isinstance(value, int):
        return value
    # ok so we got a string that needs to become an int
    elif isinstance(value, basestring):
        # remove any whitespace
        use_value = value.strip()
        # if we have a value then we will convert to int
        if use_value:
            try:
                use_value = int(use_value)
            except ValueError:
                #oops not really an int so setting to default
                use_value = DEFAULT_INT
        else:
            # value was not a value at all so setting to default
            use_value = DEFAULT_INT

    else:
        # not sure what was passed to us, but we are going
        # to set to default
        use_value = DEFAULT_INT

    # now just give them a result
    return use_value


def verify_path(path_entry):
    """
    verify a path, if it exists make sure it is
    an absolute path and return. else None
    """
    if path_entry and os.path.exists(path_entry):
        if os.path.isabs(path_entry):
            return path_entry
        else:
            return os.path.realpath(path_entry)
    else:
        return None


def get_exec_path(program):
    """
    performs a which on the program to get full path for
    the specified program
    """
    import shutil
    try:
        return shutil.which(program)
    except AttributeError:
        # monkeypatch needed prior to python 3.3;
        import shutilwhich  # flake8: noqa
        return shutil.which(program)


def format_file_ext(filetypes):
    """
    verifies that each item in the list of filetypes is a string
    and starts with a '.'
    """

    result_list = []
    # first validate we have a value and it is of list type
    if filetypes and isinstance(filetypes, list):
        for filetype in filetypes:
            # make sure None or some other garbage was not put into
            # the list
            if not filetype or not isinstance(filetype, basestring):
                continue
            # if someone configured it but left off the '.', then we will
            # simply add it for them; otherwise use as-is
            if not filetype.startswith('.'):
                result_list.append('.' + filetype)
            else:
                result_list.append(filetype)

    return result_list


def get_system(system):
    """
    Retrieves storage system based on supplied system

    :param str system:  system key ['tradition', 'si']
    :returns:           system value (1024, 1000) default: 1024
    :rtype:             int
    """
    if system in SYSTEM_MAP:
        return SYSTEM_MAP[system]
    else:
        return DEFAULT_SYSTEM


def byte_to_gb(size, precision=2, system=SYS_TRADITIONAL):
    """
    Converts bytes to gigabytes

    :param int size:    a number (in bytes)
    :param int precision:   number of points of precision default: 2
    :param str system:  system key ['tradition', 'si']
    :returns:       number in gigabytes based on system to specified precision
    :rtype:         float
    """
    gb_offset = system ** 3
    return round(float(size)/gb_offset, precision)


def get_home_disk_usage(system=None):
    """
    Gets the total amount of diskspace used based on user home directory;
    a typical seedbox provides user with a home directory and associated
    storage is allocated per user.

    :param str system:  system key ['tradition', 'si']
                        if None, no size conversion
    :returns:       amount of storage consumed/used default: bytes
    :rtype:         int
    """
    dirs_dict = {}
    my_size = 0

    # We need to walk the tree from the bottom up so that a directory can have easy
    # access to the size of its subdirectories.
    for root, dirs, files in os.walk(os.path.expanduser('~'), topdown = False):

        # update list to include full path of files; then remove
        # all files that are symlinks.
        real_files = list(os.path.join(root, name) for name in files)
        real_files = list(moves.filterfalse(os.path.islink, real_files))

        # Loop through every non directory file in this directory and sum their sizes
        size = sum(os.path.getsize(name) for name in real_files) 

        # update list to include full path of directories; then remove
        # all directories that are symlinks
        real_dirs = list(os.path.join(root, name) for name in dirs)
        real_dirs = list(moves.filterfalse(os.path.islink, real_dirs))

        # Look at all of the subdirectories and add up their sizes from the `dirs_dict`
        subdir_size = sum(dirs_dict[d] for d in real_dirs)

        # store the size of this directory (plus subdirectories) in a dict so we 
        # can access it later
        my_size = dirs_dict[root] = size + subdir_size

    log.debug('home usage: %s --> GB %s', my_size, byte_to_gb(my_size, system=system))
    # requested to convert bytes (default size type) to gigabyte
    # using either the traditional or si system
    if system is not None:
        log.debug('system provided; converting bytes to gigabytes')
        return byte_to_gb(my_size, system=system)
    return my_size


def get_plugin_name(klass_name, klass_version=None):
    """
    Retrieves a formatted plugin name based on class name holding plugin.

    :param str klass_name:  name of class holding plugin
    :param str klass_version:   the version of a plugin if None, version not
                                included in plugin name
    :returns:   formatted name of a plugin based on class and plugin version
    :rtype:     str
    """
    name = re.sub('[A-Z]+', lambda i: '_' + i.group(0).lower(),
                  klass_name).lstrip('_')

    if klass_version is not None:
        return '{0}_v{1}'.format(name, klass_version)
    else:
        return name


def get_disable_optname(klass_name, klass_version=None):
    """
    Generates a formatted plugin disabled option name

    :param str klass_name:  name of class holding plugin
    :param str klass_version:   the version of a plugin if None, version not
                                included in option name
    :returns:   formatted name of a disabled plugin option based on class
                and plugin version
    :rtype:     str
    """
    return '{0}_disabled'.format(get_plugin_name(klass_name, klass_version))
