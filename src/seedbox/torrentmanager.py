"""
Handles all interaction with data model and related persistence.
Basically it provides an interface for all actions you can do to the
objects within our model. Otherwise we could end up with challenges
related to data persistence or even having to understand how things are
persisted outside of the model area.
"""
from __future__ import absolute_import
import logging
import os
import time
from seedbox.model.schema import Torrent, MediaFile, init as schema_init, backup as schema_backup
from seedbox.torrentparser import TorrentParser, MalformedTorrentError, ParsingError

log = logging.getLogger(__name__)

def add_torrent(name):
    """
    Create the torrent and return it
    """
    torrent = Torrent(name=name)

    return torrent

def update_state(torrents, state):
    """
    update the list of torrents state attribute to the new state (bulk style)
    """
    # there has to be a faster method for doing this in bulk w/o
    # enabling lazy updates for the entire object...blah!!!
    # TODO: investigate further
    for torrent in torrents:
        # we'll progress the state of the torrent only if processing did not
        # result in an error. Such that we need to go through retry logic
        if not torrent.failed:
            torrent.state = state

def set_failed(torrent, exception):
    """
    Update torrent to a failed/error state
    """
    torrent.failed = True
    torrent.error_msg = exception

def reset_failed(torrent):
    """
    reset a torrent such that it is eligible to reprocess again
    """
    torrent.failed = False
    torrent.error_msg = None

def fetch_torrent_by_name(name):
    """
    Retrieve torrent by name
    """
    search = Torrent.selectBy(name=name)
    # because name is unique, it will always be Zero or One entry
    # so we can use the getOne() feature. By passing in None we avoid
    # get back an exception, and therefore we can check for no
    # torrent and simply create it.
    torrent = search.getOne(None)

    return torrent


def fetch_or_create_torrent(name):
    """
    Attempt to fetch the torrent, if not found, then create it
    """
    torrent = fetch_torrent_by_name(name)

    if not torrent:
        log.debug('Torrent [%s] not found; Creating torrent instance...', name)
        torrent = add_torrent(name)

    return torrent


def add_file_to_torrent(torrent, media):
    """
    Add a file to the torrent
    """
    MediaFile(filename=media.get('filename'), file_ext=media.get('file_ext'),
        file_path=media.get('file_path'),
        size=media.get('size'), compressed=media.get('compressed'),
        synced=media.get('synced'), missing=media.get('missing'),
        skipped=media.get('skipped'), torrent=torrent)


def add_files_to_torrent(torrent, file_list):
    """
    Add files to the torrent
    """
    for media in file_list:
        add_file_to_torrent(torrent, media)


def get_files_by_torrent(torrent):
    """
    retrieves the list of files for a given torrent
    """
    return list(torrent.media_files)


def get_files_by_torrentname(name):
    """
    simple convience method for get files with only a torrent name
    """
    return get_files_by_torrent(fetch_torrent_by_name(name))


def get_torrents_by_state(state, failed=False):
    """
    For a given state, retrieve a list of torrents;  by default ignore those
    that are still need to go through retry, but if requested get those
    that need to be retried for a given state.
    """
    search = Torrent.selectBy(state=state, failed=failed)

    return list(search)

def get_torrents_to_retry():
    """
    To all the torrents that have not been aborted/cancelled that are in
    and error state.
    """
    search = Torrent.selectBy(failed=True)

    return list(search)

def delete_torrents(torrents):
    """
    Delete a list of torrents
    """
    for torrent in torrents:
        Torrent.delete(id=torrent.id)

def delete_media_files(media_files):
    """
    Delete a list of media files
    """
    for media_file in media_files:
        MediaFile.delete(id=media_file.id)


###
# Helper private implementations; see seedbox.helpers for public interface
# to these private interfaces. All validation, default values, and other
# checks are handled on the public side so we can keep our interface and
# implementation as clean and simple as possible. Also then if someone
# wants to see what is going on, they can see checks there vs. digging around
# in our private implementation.
###

def get_media_files(torrent, compressed, synced, missing, skipped):
    """
    implementation for helpers; the public interface is provided
    by helpers so we don't provide any default values on this interface
    """
    search = MediaFile.selectBy(torrent=torrent.id, compressed=compressed,
        synced=synced, missing=missing, skipped=skipped)

    return list(search)

def get_processed_media_files(torrent):
    """
    Get all media files that fall in the category of processed
    synced = True; missing = True; or skipped = True
    """
    # if the torrent is been listed as invalid or has been purged
    # already then no need to query for more data.
    if torrent.invalid or torrent.purged:
        log.debug('no media files to retrieve as torrent is invalid or already purged')
        return []

    where_clause = []
    where_clause.append('media_file.torrent_id = %d' % torrent.id)
    where_clause.append('AND (media_file.synced = 1')
    where_clause.append('OR media_file.missing = 1')
    where_clause.append('OR media_file.skipped = 1)')
    str_where_clause = ' '.join(where_clause)

    log.debug('WHERE: [%s]', str_where_clause)
    search = MediaFile.select(str_where_clause, distinct=True)

    return list(search)

def purge_media(torrent):
    """
    Delete the corresponding media files from the table based on
    the specified torrent (means all processing is done, so no need to keep
    track of all the files originally associated with torrent.
    """
    MediaFile.deleteBy(torrent=torrent.id)
    torrent.purged = True

def backup_db(resource_path):
    """
    perform backup of the database, typical right before a purge action
    """
    schema_backup(resource_path)

###
# This is where we handle the loading and/or initializing of the database and all the
# torrents and associated media files.
###
def start(configs):
    """
    Make sure the database is configured and connection established
    """
    schema_init(configs.resource_path, configs.reset)
    # as part of running in retry mode; we don't want to load anything
    # new so we will skip the load aspect and only handle the database
    # aspect of starting up
    if not configs.retry:
        load_torrents(configs.torrent_path, configs.media_paths)


def load_torrents(torrent_location, media_locations):
    """
    Find all the torrents in the specified directory, verify it is a valid
    torrent file (via parsing) and capture the relevant details. Next create
    a record in the cache for each torrent.
    """
    torrent_files = os.listdir(u""+torrent_location)

    log.trace('torrent files found [%d] processing', len(torrent_files))
    start_time = time.time()
    total_media_files = 0

    for torrent_file in torrent_files:
        ext = os.path.splitext(torrent_file)[1]
        # some torrents don't always end with .torrent,
        # so let the parser reject it
        if  not ext or ext == '.torrent':
            # get the entry in the cache or creates it if it doesn't exist
            torrent = fetch_or_create_torrent(torrent_file)

            if _is_parsing_required(torrent):

                try:
                    parser = TorrentParser(os.path.join(torrent_location, torrent.name))
                    media_items = parser.get_files_details()
                    log.trace('Total files in torrent %d', len(media_items))
                    total_media_files += len(media_items)

                    media_files = _parse_torrent(media_locations, media_items)
                    add_files_to_torrent(torrent, media_files)
                except MalformedTorrentError as mte:
                    torrent.invalid = 1
                    # probably not wise to do this, but better than trying to
                    # include multiple conditions in queries when this would
                    # immeidiately filter out the truly invalid torrents when
                    # our workflow process is executing torrents based on current
                    # state of the torrent (state = workflow state)
                    torrent.state = 'cancelled'
                    log.error(
                        'Malformed Torrent: [%s] [%s]', torrent_file, mte)
                except ParsingError as ape:
                    torrent.invalid = 1
                    # probably not wise to do this, but better than trying to
                    # include multiple conditions in queries when this would
                    # immeidiately filter out the truly invalid torrents when
                    # our workflow process is executing torrents based on current
                    # state of the torrent (state = workflow state)
                    torrent.state = 'cancelled'
                    log.error('Torrent Parsing Error: [%s] [%s]', 
                        torrent_file, ape)

        else:
            log.warn('Skipping unknown file: [%s]', torrent_file)

    took = time.time() - start_time
    log.debug('torrents and media files [%d] took %.2f seconds to load', total_media_files, took)


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

def _parse_torrent(media_locations, media_items):
    """
    Handles interacting with torrent parser and getting required details
    from the parser.

    args:
        torrent: includes access to torrent and its location
    """

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
            if in_ext in ('.rar'):
                details['compressed'] = 1

            # if the file is a video type, but less than 75Mb then
            # the file is just a sample video and as such we will
            # skip the file
            elif in_ext in ('.mp4', '.avi'):
                if filesize < 75000000:
                    details['skipped'] = 1
                    log.debug(
                        'Based on size, this is a sample file [%s].\
                         Skipping..', filename)

            # if the file has any other extension (rNN, etc.) we will
            # simply skip the file
            else:
                details['skipped'] = 1
                log.debug(
                    'Unsupported filetype (%s); skipping file', in_ext)

            # now that we know if the file should be skipped or not from above
            # we will determine if the file is truly available based on the
            # full path and filename. If file is not found, then we will set
            # the file to missing
            if not details.get('skipped'):
                details['file_path'] = _get_file_path(media_locations, filename)
                if not details['file_path']:
                    details['missing'] = 1
                    log.info('Media file [%s] not found', filename)

            # now we can add the file to the torrent
            file_list.append(details)
            log.trace('Added file to torrent with details: [%s]', details)

        else:
            raise MalformedTorrentError('No indexed files found in torrent.')

    return file_list

def _get_file_path(media_locations, filename):
    """
    A list of locations/paths/directories where the media file could exist.

    return:
        location if found
        None if not found
    """

    found_location = None
    for location in media_locations:

        # if the file is found then break out of the loop and
        # return found; else we will return default not found
        if os.path.exists(os.path.join(location, filename)):
            found_location = location
            break

    return found_location

