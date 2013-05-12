"""
Holds a group of tools useful by all modules.
"""
import os
import shutil
# only need prior to python 3.3; after upgrade shutilwhich will do nothing
import shutilwhich

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

    # if the values missing or not of correct format; we could throw a ValueError
    # but for now we will simply set the value to None
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
    return shutil.which(program)
