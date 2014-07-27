"""
seedbox package
"""
from oslo.config import cfg

OPTS = [
    cfg.StrOpt('torrent_path',
               required=True,
               help='Location of the .torrent files'),
    cfg.ListOpt('media_paths',
                required=True,
                help='Location(s) of the media files'),
    cfg.StrOpt('incomplete_path',
               required=True,
               help='Location of the downloading torrents'),
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

cfg.CONF.register_opts(OPTS, group='torrent')


def load():
    """
    Simple wrapper to provide parsing and loading torrents into a
    database cache.
    """
    from seedbox.torrent import loader
    loader.load_torrents()


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
    return tools.make_opt_list([OPTS], 'torrent')
