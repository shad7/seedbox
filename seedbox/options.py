"""Handles configuration options.

Defines all the common configurations for the application, and then
manages loading all Options for system.
"""
import os

from oslo_config import cfg

CLI_OPTS = [
    cfg.BoolOpt('cron',
                default=False,
                help='Disable console output when running via cron'),
    cfg.StrOpt('logfile',
               metavar='LOG_FILE',
               default='{0}.log'.format(__package__),
               help='specify name of log file default: %(default)s'),
    cfg.StrOpt('loglevel',
               metavar='LOG_LEVEL',
               default='info',
               help='specify logging level to log messages: %(choices)s',
               choices=['none',
                        'critical',
                        'error',
                        'warning',
                        'info',
                        'debug',
                        'trace']),
    cfg.StrOpt('logconfig',
               metavar='LOG_CONFIG',
               help='specific path and filename of logging configuration \
                    (override defaults)'),
]

cfg.CONF.register_cli_opts(CLI_OPTS)

OPTS = [
    cfg.StrOpt('base_path',
               default=os.getcwd(),
               required=True,
               help='Base path',
               sample_default='/home/username'),
    cfg.StrOpt('base_client_path',
               help='Location torrent client stores data files',
               sample_default='$base_path/torrents/data'),
]

cfg.CONF.register_opts(OPTS)

DB_OPTS = [
    cfg.StrOpt('connection',
               default='sqlite:///$config_dir/torrent.db',
               help='The connection string used to connect to the database'),
    cfg.IntOpt('idle_timeout',
               default=3600,
               help='Timeout before idle sql connections are reaped'),
    cfg.IntOpt('connection_debug',
               default=0,
               help='Verbosity of SQL debugging information. 0=None, 100=All'),
]

cfg.CONF.register_opts(DB_OPTS, 'database')

PROC_OPTS = [
    cfg.IntOpt('max_processes',
               default=4,
               help='max processes to use for performing sync of torrents'),
    cfg.ListOpt('prepare',
                default=[],
                help='name of tasks associated with prepare phase',
                sample_default='filecopy, fileunrar'),
    cfg.ListOpt('activate',
                default=[],
                help='name of tasks associated with activate phase',
                sample_default='filesync'),
    cfg.ListOpt('complete',
                default=[],
                help='name of tasks associated with complete phase',
                sample_default='filedelete'),
]

cfg.CONF.register_opts(PROC_OPTS, group='process')

TASK_OPTS = [
    cfg.StrOpt('sync_path',
               default='/tmp/sync',
               help='Location to temp media copies for syncing to library'),
]

cfg.CONF.register_opts(TASK_OPTS, group='tasks')

SYNC_OPTS = [
    cfg.BoolOpt('dryrun',
                default=False,
                help='rsync dryrun option'),
    cfg.BoolOpt('verbose',
                default=False,
                help='rsync verbose option'),
    cfg.BoolOpt('progress',
                default=False,
                help='rsync progress option'),
    cfg.BoolOpt('perms',
                default=True,
                help='rsync perms option'),
    cfg.BoolOpt('delayupdates',
                default=True,
                help='rsync delayupdates option'),
    cfg.BoolOpt('recursive',
                default=True,
                help='rsync recursive option'),
    cfg.StrOpt('chmod',
               default='ugo+rwx',
               help='rsync chmod option'),
    cfg.StrOpt('identity',
               help='rsync-ssh identity option (ssh key)',
               sample_default='/home/username/.ssh/my_home.key'),
    cfg.StrOpt('port',
               default='22',
               help='rsync-ssh port'),
    cfg.StrOpt('remote_user',
               help='User name on remote system (ssh)',
               sample_default='username'),
    cfg.StrOpt('remote_host',
               help='Host name/IP Address of remote system',
               sample_default='home.example.com'),
    cfg.StrOpt('remote_path',
               help='rsync destination path',
               sample_default='/media/downloads'),
]

cfg.CONF.register_opts(SYNC_OPTS, group='tasks_filesync')

SYNCLOG_OPTS = [
    cfg.StrOpt('stdout_dir',
               default='$config_dir/sync_out',
               help='Output directory for stdout files'),
    cfg.StrOpt('stderr_dir',
               default='$config_dir/sync_err',
               help='Output directory for stderr files'),
    cfg.BoolOpt('stdout_verbose',
                default=False,
                help='Write output to stdout'),
    cfg.BoolOpt('stderr_verbose',
                default=True,
                help='Output verbose details about exceptions'),
]

cfg.CONF.register_opts(SYNCLOG_OPTS, group='tasks_synclog')

TORRENT_OPTS = [
    cfg.StrOpt('torrent_path',
               required=True,
               help='Location of the .torrent files',
               sample_default='/home/username/.config/state'),
    cfg.ListOpt('media_paths',
                required=True,
                help='Location(s) of the media files',
                sample_default='$base_client_path/completed'),
    cfg.StrOpt('incomplete_path',
               required=True,
               help='Location of the downloading torrents',
               sample_default='$base_client_path/inprogress'),
    cfg.ListOpt('video_filetypes',
                default=['.avi', '.mp4', '.mkv', '.mpg'],
                help='List of video filetypes to support. (ignore others)'),
    cfg.ListOpt('compressed_filetypes',
                default=['.rar'],
                help='List of compressed filetypes to support. '
                     '(ignore others)'),
    cfg.IntOpt('minimum_file_size',
               default=75000000,
               help='Minimum file size of a media file'),
]

cfg.CONF.register_opts(TORRENT_OPTS, group='torrent')


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
    all_opts = []
    all_opts.extend(tools.make_opt_list([OPTS], None))
    all_opts.extend(tools.make_opt_list([DB_OPTS], 'database'))
    all_opts.extend(tools.make_opt_list([PROC_OPTS], 'process'))
    all_opts.extend(tools.make_opt_list([TASK_OPTS], 'tasks'))
    all_opts.extend(tools.make_opt_list([SYNC_OPTS], 'tasks_filesync'))
    all_opts.extend(tools.make_opt_list([SYNCLOG_OPTS], 'tasks_synclog'))
    all_opts.extend(tools.make_opt_list([TORRENT_OPTS], 'torrent'))
    return all_opts
