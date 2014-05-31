"""
Holds a group of tools useful by all modules.
"""
import logging
import os

import six

LOG = logging.getLogger(__name__)


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
