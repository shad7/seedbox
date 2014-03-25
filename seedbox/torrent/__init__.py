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
    from seedbox.torrent import loader
    loader.load_torrents()
