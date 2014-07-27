"""
Holds a group of tools useful by all modules.
"""
import copy
import itertools
import logging
import os

import six

LOG = logging.getLogger(__name__)


def verify_path(path_entry):
    """
    verify a path, if it exists make sure it is
    an absolute path and return. else None

    :param path_entry: path to file or directory on host
    """
    if path_entry and os.path.exists(path_entry):
        if os.path.isabs(path_entry):
            return path_entry
        else:
            return os.path.realpath(path_entry)
    else:
        return None


def format_file_ext(filetypes):
    """
    verifies that each item in the list of filetypes is a string
    and starts with a '.'

    :param list filetypes: a list of extensions representing types of files
    """

    result_list = []
    # first validate we have a value and it is of list type
    if filetypes and isinstance(filetypes, list):
        for filetype in filetypes:
            # make sure None or some other garbage was not put into
            # the list
            if not isinstance(filetype, six.string_types):
                continue

            filetype = filetype.strip()
            if not filetype:
                continue
            # if someone configured it but left off the '.', then we will
            # simply add it for them; otherwise use as-is
            if not filetype.startswith('.'):
                result_list.append('.' + filetype)
            else:
                result_list.append(filetype)

    return result_list


def make_opt_list(opts, group):
    """
    Generate a list of tuple containing group, options

    :param opts: option lists associated with a group
    :type opts: list
    :param group: name of an option group
    :type group: str
    :return: a list of (group_name, opts) tuples
    :rtype: list
    """
    _opts = [(group, list(itertools.chain(*opts)))]
    return [(g, copy.deepcopy(o)) for g, o in _opts]
