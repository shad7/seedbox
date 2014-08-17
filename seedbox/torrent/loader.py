"""
Torrent loader handles searches the directory where torrent files are stored
and adds them to the database cache if not already found.
"""
import logging
import glob
import os

from oslo.config import cfg

from seedbox import constants
from seedbox import db
from seedbox.common import tools
from seedbox.db import models
from seedbox.torrent import parser

LOG = logging.getLogger(__name__)

COMPRESSED_TYPES = tools.format_file_ext(cfg.CONF.torrent.compressed_filetypes)
VIDEO_TYPES = tools.format_file_ext(cfg.CONF.torrent.video_filetypes)


def load_torrents():
    """
    Find all the torrents in the specified directory, verify it is a valid
    torrent file (via parsing) and capture the relevant details. Next create
    a record in the cache for each torrent.
    """

    dbapi = db.dbapi()

    for torrent_file in glob.glob(os.path.join(cfg.CONF.torrent.torrent_path,
                                               '*.torrent')):

        # get the entry in the cache or creates it if it doesn't exist
        torrent = dbapi.fetch_or_create_torrent(
            os.path.basename(torrent_file))

        if _is_parsing_required(torrent):

            try:
                torparser = parser.TorrentParser(torrent_file)
            except parser.ParsingError as ape:
                torrent.invalid = True
                torrent.state = constants.CANCELLED
                dbapi.save_torrent(torrent)
                LOG.error('Torrent Parsing Error: [%s] [%s]',
                          torrent_file, ape)
                continue

            media_items = torparser.get_files_details()
            LOG.debug('Total files in torrent %d', len(media_items))

            # determine if any of the files are still inprogress of
            # being downloaded; if so then go to next torrent.
            # Because no files were added to the cache for the torrent
            # we will once again parse and attempt to process it.
            if _is_torrent_downloading(media_items):
                LOG.debug('torrent still downloading, next...')
                continue

            dbapi.bulk_create_medias(
                _filter_media(torrent.torrent_id, media_items))


def _is_parsing_required(torrent):
    """
    Determines if parsing is required. Checks the following attributes
    to determine if we should skip parsing or not:
    - if torrent.invalid is True, skip parsing
    - if torrent.purged is True, skip parsing
    - if len(torrent.media_files) > 0, skip parsing
    """
    parse = True

    # if we have parse the file previous and marked it invalid, then no
    # need to bother doing it again
    if torrent.invalid:
        parse = False

    # if we have already purged the torrent media files, then no need
    # to perform any parsing again
    if torrent.purged:
        parse = False

    # we have already parsed the file previously, which is why there are
    # files already associated to the torrent, otherwise it would have
    # been zero
    if torrent.media_files:
        parse = False

    return parse


def _is_torrent_downloading(media_items):
    """
    Verify if at least one item still located in the
    inprogress/downloading location

    args:
        media_items: files found inside a torrent
    returns:
        true: if any file is still within incomplete_path
        false: if no file is within incomplete_path
    """

    found = False
    for (filename, filesize) in media_items:

        # if the file is found then break out of the loop and
        # return found; else we will return default not found
        if os.path.exists(os.path.join(
                cfg.CONF.torrent.incomplete_path, filename)):
            found = True
            break

    return found


def _filter_media(torrent_id, media_items):
    """
    Handles interacting with torrent parser and getting required details
    from the parser.

    args:
        torrent: includes access to torrent and its location
    """

    file_list = []
    for (filename, filesize) in media_items:

        media = models.MediaFile.make_empty()
        media.torrent_id = torrent_id
        media.filename = filename
        media.size = filesize

        in_ext = os.path.splitext(filename)[1]
        media.file_ext = in_ext

        # default to missing; no need to check all the paths for a file
        # if we don't really care about the file to start with, ie a file
        # we plan to skip
        media.file_path = None

        # we will assume each file is not synced
        # desired (not skipped), and accessible
        media.compressed = False
        media.synced = False

        # if ends with rar, then it is a compressed file;
        if in_ext in COMPRESSED_TYPES:
            media.compressed = True
            LOG.debug('found compressed file: %s', filename)

        # if the file is a video type, but less than 75Mb then
        # the file is just a sample video and as such we will
        # skip the file
        elif in_ext in VIDEO_TYPES:
            if filesize < cfg.CONF.torrent.minimum_file_size:
                LOG.debug(
                    'Based on size, this is a sample file [%s]. Skipping..',
                    filename)
                continue
            else:
                LOG.debug('found video file: %s', filename)

        # if the file has any other extension (rNN, etc.) we will
        # simply skip the file
        else:
            LOG.debug(
                'Unsupported filetype (%s); skipping file', in_ext)
            continue

        (media.file_path, media.filename) = _get_file_path(filename)
        if media.file_path is None:
            LOG.info('Media file [%s] not found', filename)
            continue

        # now we can add the file to the torrent
        file_list.append(media)
        LOG.debug('Added file to torrent with details: [%s]', media)

    return file_list


def _get_file_path(filename):
    """
    A list of locations/paths/directories where the media file could exist.

    return:
        location if found
        None if not found
    """

    found_path = None
    found_file = None
    for location in cfg.CONF.torrent.media_paths:

        full_path = os.path.join(location, filename)
        # if the file is found then break out of the loop and
        # return found; else we will return default not found
        if os.path.exists(full_path):
            (found_path, found_file) = os.path.split(full_path)
            break

    return (found_path, found_file)
