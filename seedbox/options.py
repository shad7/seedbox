"""Handles configuration options.

Defines all the common configurations for the application, and then
manages loading all Options for system.
"""
import os

from oslo_config import cfg
from six import moves

from seedbox import version

PROJECT = __package__
DEFAULT_FILENAME = PROJECT + '.conf'

OPTS = [
    cfg.StrOpt('base_path',
               default=os.getcwd(),
               required=True,
               help='Base path'),
    cfg.StrOpt('base_client_path',
               help='Location torrent client stores data files'),
]

cfg.CONF.register_opts(OPTS)


def _find_config_files():

    def _fixpath(p):
        """Apply tilde expansion and absolutization to a path."""
        return os.path.abspath(os.path.expanduser(p))

    virtual_env = os.environ.get('VIRTUAL_ENV', '')

    config_files = [
        _fixpath(os.path.join('~', '.' + PROJECT, DEFAULT_FILENAME)),
        _fixpath(os.path.join('~', DEFAULT_FILENAME)),
        os.path.join(os.sep + 'etc', PROJECT, DEFAULT_FILENAME),
        os.path.join(os.sep + 'etc', DEFAULT_FILENAME),
        os.path.join(PROJECT, 'etc', PROJECT, DEFAULT_FILENAME),
        os.path.join(virtual_env, 'etc', PROJECT, DEFAULT_FILENAME),
        os.path.join(virtual_env, 'etc', DEFAULT_FILENAME),
        os.path.join(os.getcwd(), DEFAULT_FILENAME)
    ]

    # return back the list of the config files found
    return list(moves.filter(os.path.exists, config_files))


def initialize(args=None):
    """Initialize options.

    Handles finding and loading configuration options for the entire
    system. Searches for configuration files in the following locations:

    .. envvar:: VIRTUAL_ENV
        defined when virtualenv is started
        source bin/activation


        * /etc/
        * /etc/seedbox/
        * ~/VIRTUAL_ENV/etc/
        * ~/VIRTUAL_ENV/etc/seedbox/
        * ~/
        * ~/.seedbox/
        * ./ (current working directory)


    :param list args:   command line inputs
    """
    # configure the program to start....
    cfg.CONF(
        args,
        project=PROJECT,
        version=version.version_string(),
        default_config_files=_find_config_files(),
    )

    # if no config_dir was provided then we will set it to the
    # path of the most specific config file found.
    if not cfg.CONF.config_dir:
        cfg.CONF.set_default('config_dir',
                             os.path.dirname(cfg.CONF.config_file[-1]))


def list_opts():
    """Returns a list of oslo_config options available in the library.

    The returned list includes all oslo_config options which may be registered
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
    return tools.make_opt_list([OPTS], None)
