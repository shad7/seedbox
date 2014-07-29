"""
Defines tasks to execute as part of the process
"""


def list_opts():
    """
    Returns a list of oslo.config options available in the library.

    The returned list includes all oslo.config options which may be registered
    at runtime by the library.

    Each element of the list is a tuple. The first element is the name of the
    group under which the list of elements in the second element will be
    registered. A group name of None corresponds to the [DEFAULT] group in
    config files.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users by this library.

    :returns: a list of (group_name, opts) tuples
    """
    from seedbox.common import tools
    from seedbox.tasks import base
    from seedbox.tasks import filesync
    from seedbox.tasks import subprocessext

    _opts = tools.make_opt_list([base.OPTS], 'tasks')
    _opts.extend(tools.make_opt_list([filesync.OPTS], 'tasks_filesync'))
    _opts.extend(tools.make_opt_list([subprocessext.OPTS], 'tasks_synclog'))

    return _opts
