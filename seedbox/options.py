"""
Defines all the common configurations for the application, and then
manages loading all Options for system.
"""
import os
import sys

from six import moves
from oslo.config import cfg

from seedbox import version

PROJECT_NAME = 'seedbox'

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

    virtual_path = os.getenv('VIRTUAL_ENV')
    default_cfg_type = '.conf'
    legacy_cfg_type = '.cfg'

    possible = []
    # in reverse order as the last one loaded always takes precedence
    # system-level /etc and /etc/<project>
    possible.append(os.sep + 'etc')
    possible.append(os.path.join(os.sep, 'etc', PROJECT_NAME))

    # if virtualenv is active; then leverage <virtualenv>/etc
    # and <virtualenv>/etc/<project>
    if virtual_path:
        possible.append(os.path.join(virtual_path, 'etc'))
        possible.append(os.path.join(virtual_path, 'etc', PROJECT_NAME))

    # the user's home directory
    possible.append(os.path.expanduser('~'))

    # the user's home directory with project specific directory
    possible.append(os.path.join(os.path.expanduser('~'), '.' + PROJECT_NAME))
    if sys.platform.startswith('win'):
        # On windows look in ~/seedbox as well, as explorer does not
        # let you create a folder starting with a dot
        possible.append(os.path.join(os.path.expanduser('~'), PROJECT_NAME))

    # current working directory as a last ditch effort
    possible.append(os.getcwd())

    # now append the filename to the possible locations we search
    config_files = []
    for loc in possible:
        config_files.append(
            os.path.join(loc, PROJECT_NAME + default_cfg_type))
        config_files.append(
            os.path.join(loc, PROJECT_NAME + legacy_cfg_type))

    # return back the list of the config files found
    return list(moves.filter(os.path.exists, config_files))


def initialize(args):
    """
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
        project=PROJECT_NAME,
        version=version.version_string(),
        default_config_files=_find_config_files(),
    )

    # if no config_dir was provided then we will set it to the
    # path of the most specific config file found.
    if not cfg.CONF.config_dir:
        cfg.CONF.set_default('config_dir',
                             os.path.dirname(cfg.CONF.config_file[-1]))


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
    return tools.make_opt_list([OPTS], None)
