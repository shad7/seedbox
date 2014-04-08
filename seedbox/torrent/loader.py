from __future__ import absolute_import
import logging
import glob
import os

from oslo.config import cfg

from seedbox.common import tools
from seedbox.db import api as dbapi
from seedbox.torrent import parser

LOG = logging.getLogger(__name__)


def load_torrents():
    """
    Find all the torrents in the specified directory, verify it is a valid
    torrent file (via parsing) and capture the relevant details. Next create
    a record in the cache for each torrent.
    """

    for torrent_file in glob.glob(os.path.join(cfg.CONF.torrent.torrent_path,
                                               '*.torrent')):

        # get the entry in the cache or creates it if it doesn't exist
        torrent = dbapi.fetch_or_create_torrent(
            os.path.basename(torrent_file))

        if _is_parsing_required(torrent):

            try:
                torparser = parser.TorrentParser(torrent_file)
                media_items = torparser.get_files_details()
                LOG.trace('Total files in torrent %d', len(media_items))

                # determine if any of the files are still inprogress of
                # being downloaded; if so then go to next torrent.
                # Because no files were added to the cache for the torrent
                # we will once again parse and attempt to process it.
                if _is_torrent_downloading(media_items):
                    LOG.trace('torrent still downloading, next...')
                    continue

                dbapi.add_files_to_torrent(torrent,
                                           _filter_media(media_items))
            except parser.ParsingError as ape:
                dbapi.set_invalid(torrent)
                LOG.error('Torrent Parsing Error: [%s] [%s]',
                          torrent_file, ape)


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
    if torrent.invalid is True:
        parse = False

    # if we have already purged the torrent media files, then no need
    # to perform any parsing again
    if torrent.purged is True:
        parse = False

    # we have already parsed the file previously, which is why there are
    # files already associated to the torrent, otherwise it would have
    # been zero
    if torrent.media_files.count() > 0:
        parse = False

    return parse


def _is_torrent_downloading(media_items):
    """
    Verify if atleast one item still located in the
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


def _filter_media(media_items):
    """
    Handles interacting with torrent parser and getting required details
    from the parser.

    args:
        torrent: includes access to torrent and its location
    """
    compressed_types = tools.format_file_ext(
        cfg.CONF.torrent.compressed_filetypes)
    video_types = tools.format_file_ext(cfg.CONF.torrent.video_filetypes)
    # 75000000 ~= 75MB
    # need to change to be specific to filetype as music is always
    # smaller than video, etc.
    min_file_size = cfg.CONF.torrent.minimum_file_size

    file_list = []
    for (filename, filesize) in media_items:
        if filename:

            details = {}
            details['filename'] = filename
            details['size'] = filesize

            in_ext = os.path.splitext(filename)[1]
            details['file_ext'] = in_ext

            # default to missing; no need to check all the paths for a file
            # if we don't really care about the file to start with, ie a file
            # we plan to skip
            details['file_path'] = None

            # we will assume each file is not synced
            # desired (not skipped), and accessible
            details['compressed'] = 0
            details['synced'] = 0
            details['skipped'] = 0
            details['missing'] = 0

            # if ends with rar, then it is a compressed file;
            if in_ext in compressed_types:
                details['compressed'] = 1
                LOG.debug('adding compressed file: %s', filename)

            # if the file is a video type, but less than 75Mb then
            # the file is just a sample video and as such we will
            # skip the file
            elif in_ext in video_types:
                if filesize < min_file_size:
                    details['skipped'] = 1
                    LOG.debug(
                        'Based on size, this is a sample file [%s].\
                         Skipping..', filename)
                else:
                    LOG.debug('adding video file: %s', filename)

            # if the file has any other extension (rNN, etc.) we will
            # simply skip the file
            else:
                details['skipped'] = 1
                LOG.debug(
                    'Unsupported filetype (%s); skipping file', in_ext)

            # now that we know if the file should be skipped or not from above
            # we will determine if the file is truly available based on the
            # full path and filename. If file is not found, then we will set
            # the file to missing
            if not details.get('skipped'):
                details['file_path'] = _get_file_path(filename)
                if not details['file_path']:
                    details['missing'] = 1
                    LOG.info('Media file [%s] not found', filename)

            # now we can add the file to the torrent
            file_list.append(details)
            LOG.trace('Added file to torrent with details: [%s]', details)

        else:
            LOG.warn('No indexed files found in torrent.')

    return file_list


def _get_file_path(filename):
    """
    A list of locations/paths/directories where the media file could exist.

    return:
        location if found
        None if not found
    """

    found_location = None
    for location in cfg.CONF.torrent.media_paths:

        # if the file is found then break out of the loop and
        # return found; else we will return default not found
        if os.path.exists(os.path.join(location, filename)):
            found_location = location
            break

    return found_location
