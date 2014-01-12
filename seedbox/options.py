"""
Defines all the common configurations for the application, and then
manages loading all Options for system.
"""
from __future__ import absolute_import, print_function
import os
import sys

from six import moves
from oslo.config import cfg

from seedbox.common import tools
from seedbox import version
from seedbox.configs import generator

PROJECT_NAME = 'seedbox'

OPTS = [
    cfg.StrOpt('base_path',
               default=os.getcwd(),
               deprecated_group='DEFAULT',
               required=True,
               help='Base path'),
    cfg.StrOpt('base_client_path',
               deprecated_group='DEFAULT',
               help='Location torrent client stores data files'),
    cfg.StrOpt('torrent_path',
               deprecated_group='DEFAULT',
               required=True,
               help='Location of the .torrent files'),
    cfg.ListOpt('media_paths',
                deprecated_group='DEFAULT',
                required=True,
                help='Location(s) of the media files'),
    cfg.StrOpt('incomplete_path',
               deprecated_group='DEFAULT',
               required=True,
               help='Location of the downloading torrents'),
    cfg.StrOpt('sync_path',
               deprecated_group='DEFAULT',
               required=True,
               help='Location to temp media copies for syncing to library'),
    cfg.ListOpt('plugin_paths',
                default=[],
                deprecated_group='DEFAULT',
                help='Location(s) of additional plugins'),
    cfg.ListOpt('disabled_phases',
                default=[],
                deprecated_group='DEFAULT',
                help='List of phases to disable for execution (prepare, activate, complete)'),  # noqa
    cfg.ListOpt('video_filetypes',
                default=['.avi', '.mp4', '.mkv', '.mpg'],
                deprecated_group='DEFAULT',
                help='List of video filetypes to support. (ignore others)'),
    cfg.ListOpt('compressed_filetypes',
                default=['.rar'],
                deprecated_group='DEFAULT',
                help='List of compressed filetypes to support. (ignore others)'),  # noqa
    cfg.IntOpt('max_retry',
               default=5,
               deprecated_group='DEFAULT',
               help='Maximum number of times to retry a failed torrent'),
]

cfg.CONF.register_opts(OPTS)

CLI_OPTS = [
#   cfg.BoolOpt('gen_config_sample',
#               default=False,
#               help='Generate a sample configuration file to resource path'),
    cfg.BoolOpt('purge',
                default=False,
                help='DANGER: deletes the database cache and \
                     everything starts over'),
    cfg.BoolOpt('retry',
                default=False,
                help='only executes entries that failed previously'),
]

cfg.CONF.register_cli_opts(CLI_OPTS)


def _build_group_opts(group_name):

    opts = []
    for opt_name in sorted(cfg.CONF._groups[group_name]._opts):
        print(group_name, opt_name)
        opts.append(cfg.CONF._get_opt_info(opt_name, group_name)['opt'])
    return opts


def _gen_config_sample():


    opts_by_group = {generator.DEFAULT_GROUP: []}

    opts = []
    for opt_name in sorted(cfg.CONF._opts):
        print('DEFAULT', opt_name)
        opts.append(cfg.CONF._get_opt_info(opt_name)['opt'])

    opts_by_group.setdefault(generator.DEFAULT_GROUP, []).append(
        (generator.DEFAULT_GROUP, opts))

    cfg.CONF.import_group('plugins', 'seedbox.tasks.filecopy')
    opts_by_group.setdefault('plugins', []).append(
        ('seedbox.tasks.filecopy', _build_group_opts('plugins')))

    cfg.CONF.import_group('plugins', 'seedbox.tasks.filedelete')
    opts_by_group.setdefault('plugins', []).append(
        ('seedbox.tasks.filedelete', _build_group_opts('plugins')))

    cfg.CONF.import_group('plugins', 'seedbox.tasks.fileunrar')
    opts_by_group.setdefault('plugins', []).append(
        ('seedbox.tasks.fileunrar', _build_group_opts('plugins')))

    cfg.CONF.import_group('plugins', 'seedbox.tasks.validate_phase')
    opts_by_group.setdefault('plugins', []).append(
        ('seedbox.tasks.validate_phase', _build_group_opts('plugins')))

    cfg.CONF.import_group('plugins', 'seedbox.tasks.prepare')
    opts_by_group.setdefault('plugins', []).append(
        ('seedbox.tasks.prepare', _build_group_opts('plugins')))

    cfg.CONF.import_group('prepare', 'seedbox.tasks.prepare')
    opts_by_group.setdefault('prepare', []).append(
        ('seedbox.tasks.prepare', _build_group_opts('prepare')))

    cfg.CONF.import_group('plugins', 'seedbox.tasks.filesync')
    opts_by_group.setdefault('plugins', []).append(
        ('seedbox.tasks.filesync', _build_group_opts('plugins')))

    cfg.CONF.import_group('filesync', 'seedbox.tasks.filesync')
    opts_by_group.setdefault('filesync', []).append(
        ('seedbox.tasks.filesync', _build_group_opts('filesync')))

    cfg.CONF.import_group('prsync', 'seedbox.tasks.filesync')
    opts_by_group.setdefault('prsync', []).append(
        ('seedbox.tasks.filesync', _build_group_opts('prsync')))


#   for opt_name in sorted(cfg.CONF._opts):
#       opt = cfg.CONF._get_opt_info(opt_name)['opt']
#       value = cfg.CONF[opt_name]
#       print(opt_name, value, 'dest:', opt.dest, 'default:', opt.default, 'help:', opt.help, 'req:', opt.required, 'opt:', opt)
#
#   for group_name in cfg.CONF._groups:
#       print(group_name)
#       group_attr = cfg.CONF.GroupAttr(cfg.CONF, cfg.CONF._get_group(group_name))
#       print(group_attr)
#       for opt_name in sorted(cfg.CONF._groups[group_name]._opts):
#           print(opt_name)
#           opt = cfg.CONF._get_opt_info(opt_name, group_name)['opt']
#           value = cfg.CONF[group_name][opt_name]
#           print(group_name, opt_name, value, 'dest:', opt.dest, 'default:', opt.default, 'help:', opt.help, 'req:', opt.required, 'group_attr:', group_attr, 'opt:', opt)


    output = []
    map(output.append,
        generator._gen_group_opts_output(generator.DEFAULT_GROUP,
                                         opts_by_group.pop(generator.DEFAULT_GROUP,
                                                           [])))
    for group in sorted(opts_by_group.keys()):
        map(output.append, generator._gen_group_opts_output(group,
                                                            opts_by_group[group]))

    generator._write_output(output, os.path.join(cfg.CONF.config_dir,
                                                 PROJECT_NAME + '.conf.sample'))

#   src_dir = os.path.dirname(os.path.abspath(__file__))
#
#   srcfiles = []
#   for root, dirs, files in os.walk(src_dir):
#
#       if (os.path.basename(root) == 'tests' or
#           os.path.dirname(root).endswith('tests')):
#           continue
#
#       for name in files:
#           ext = os.path.splitext(name)[1]
#           if ext == generator.PY_EXT:
#               srcfiles.append(os.path.join(root, name))
#
#   for name in srcfiles:
#       print(name)
#
#   generator.generate(srcfiles,
#                      os.path.join(cfg.CONF.config_dir,
#                      PROJECT_NAME + '.conf.sample'))


def _find_config_files():

    virtual_path = os.getenv('VIRTUAL_ENV')
    default_cfg_type = '.conf'
    legacy_cfg_type = '.cfg'

    possible = []
    # in reverse order as the last one loaded always takes precendence
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
        * /etc/seedbox
        * ~/VIRTUAL_ENV/etc/
        * ~/VIRTUAL_ENV/etc/seedbox/
        * ~/
        * ~/.seedbox/
        * . (current working directory)


    :param list args:   command line inputs
    """
    # configure the program to start....
    cfg.CONF(
        args,
        project=PROJECT_NAME,
        version=version.version_info.version_string(),
        default_config_files=_find_config_files(),
    )

    # if no config_dir was provided then we will set it to the
    # path of the most specific config file found.
    if not cfg.CONF.config_dir:
        cfg.CONF.config_dir = os.path.dirname(cfg.CONF.config_file[-1])

#   if cfg.CONF.gen_config_sample:
#       _gen_config_sample()
#       sys.exit(0)

    # validate the know directory locations that we depend on within
    # the application to make sure we have valid paths
    validate_paths = [cfg.CONF.base_path, cfg.CONF.base_client_path,
                      cfg.CONF.torrent_path, cfg.CONF.incomplete_path,
                      cfg.CONF.sync_path]
    map(validate_paths.append, cfg.CONF.media_paths)
    map(validate_paths.append, cfg.CONF.plugin_paths)

    invalid_paths = []
    for entry in validate_paths:
        if tools.verify_path(entry) is None:
            invalid_paths.append(entry)

    if invalid_paths:
        raise ValueError('Invalid paths provided in configuration file(s): %s',
                         invalid_paths)
