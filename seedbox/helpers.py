"""
These are helper functions that individual tasks can leverage to perform some
pre-defined activities without having to understand how we do caching, updates,
or even what the process flow is. By hiding all of these details we can keep
internals private.
"""
from __future__ import absolute_import
from itertools import ifilter
import logging
import os
from seedbox import datamanager

log = logging.getLogger(__name__)


def set_torrent_failed(torrent, error):
    """
    set the torrent as failed and corresponding error

    :param object torrent:  torrent entry provided as input to all plugins
    :param str error:       an exception message
    """
    if torrent.error_msg:
        msg = '+&+'.join(torrent.error_msg, error)
    else:
        msg = error

    datamanager.set_failed(torrent, msg)


def get_media_files(torrent, file_exts=None, file_path=None, compressed=False,
                    synced=False, missing=False, skipped=False):
    """
    Retrieve mediafiles associated with the specified torrent entry.

    :param object torrent:  torrent entry provided as input to all plugins
    :param list file_ext:   file extensions for filtering the results list
    :param str file_path:   the path where the file can be found
    :param bool compressed: flag to include or not include compressed files
    :param bool synced:     flag to include or not include files synced
    :param bool missing:    flag to include or not include files there were
                            not able to be located during loading
    :param bool skipped:    flag to include or not include files that were
                            ignored during parsing (extra type files)
    :return:                mediafiles or empty list if no files found
                            matching criteria
    :rtype:                 list
    :raises ValueError:     when incorrect inputs provided (eg. missing
                            torrent or empty torrent)
    """

    log.trace('looking for media files for torrent %s', torrent)

    if not torrent or not torrent.id:
        raise ValueError('missing input: torrent is a required input')

    media_files = datamanager.get_media_files(torrent, file_path, compressed,
                                              synced, missing, skipped)
    if not media_files:
        log.debug('no mediafiles found for specified torrent')
        # no results found
        return []

    if file_exts:
        log.trace('filtering list of results using list of exts %s',
                  file_exts)
        ext_check = lambda media: media.file_ext in file_exts
        # now filter out any files that don't match the supplied file_ext list
        # also need to perform list otherwise it is an ifilter iterable
        return list(ifilter(ext_check, media_files))

    log.debug('found %d media files', len(media_files))
    return media_files


def is_torrent_processed(torrent):
    """
    determine if ALLL media files associated with torrent are
    completely processed;

    :param object torrent:  torrent entry provided as input to all plugins
    :returns:               flag indicating if torrent was processed;
                            True if all files processed or False if not
    :rtype:                 boolean
    :raises ValueError:     when incorrect inputs provided
                            (eg. missing torrent or empty torrent)
    """

    if not torrent or not torrent.id:
        raise ValueError('missing input: torrent is a required input')

    flag = False
    # how many files are associated with torrent
    total_files = len(datamanager.get_files_by_torrent(torrent))
    # how many files have already been processed
    total_processed = len(datamanager.get_processed_media_files(torrent))

    log.trace('total files [%d] vs. total processed [%d]',
              total_files, total_processed)
    # if the two totals are the same then torrent is fully processed
    # if the torrent has already been purged or is invalid (has no files)
    # then both will return 0, therefore the same.
    if total_files == total_processed:
        flag = True

    return flag


def synced_media_file(media_file):
    """
    perform sync of media file into the cache

    :param object media_file:   a media file entry retrieved when calling
                                get_media_files
    :raises ValueError:         when incorrect inputs provided (eg. missing
                                media_file or empty media_file)
    """
    if not media_file or not media_file.id:
        raise ValueError('missing input: torrent is a required input')

    log.trace('syncing media file to cache %s', media_file)
    media_file.synced = True
    log.trace('synced to cache %s', media_file)


def set_media_files_path(file_location, media_files):
    """
    Update the file path for each of the files in the list.

    :param str file_location:   the path/directory to where the files are
                                stored on disk
    :param list media_files:    the cached files that have an updated location
    :raises OSError:            when a file in the list of filenames
                                doesn't exist
    :raises TypeError:          when added files is not a list
    :raises ValueError:         when incorrect inputs provided;
                                including missing inputs
    """

    # if the file_location wasn't provided/empty, or doesn't actually exist,
    # and is not a directory then we will raise an exception since we can't
    # proceed w/o this
    if (not file_location or not os.path.exists(file_location) or
            not os.path.isdir(file_location)):
        raise ValueError('invalid input file_location provided')

    # if provided and not a list type; then we have an issue
    if media_files and not isinstance(media_files, list):
        raise TypeError(
            'invalid input type for media_files provided: expected a list')

    log.trace('setting location [%s] for %d media files',
              file_location, len(media_files))
    for media_file in media_files:
        media_file.file_path = file_location

    log.trace('location set')


def add_mediafiles_to_torrent(torrent, file_location, added_files):
    """
    Add mediafiles to cache associated to torrent after decompressing
    an archive.

    :param object torrent:      torrent entry provided as input to all plugins
    :param str file_location:   folder where the file was decompressed to
    :param list added_files:    filenames that need to be processed and cached
    :raises OSError:            when one of the files doesn't exist
    :raises TypeError:          when added files is not a list
    :raises ValueError:         when incorrect inputs provided;
                                including missing inputs
    """

    if not torrent or not torrent.id:
        raise ValueError('missing input: torrent is a required input')

    # if the file_location wasn't provided/empty, or doesn't actually exist,
    # and is not a directory then we will raise an exception since we can't
    # proceed w/o this
    if (not file_location or not os.path.exists(file_location) or
            not os.path.isdir(file_location)):
        raise ValueError('invalid input file_location provided')

    # if provided and not a list type; then we have an issue
    if added_files and not isinstance(added_files, list):
        raise TypeError(
            'invalid input type for added_files provided: expected a list')

    media_files = []

    log.trace('start processing files to be added to torrent %s', torrent)
    for added_file in added_files:

        media = {}
        # as part of getting size it checks for the existence of file
        # if it doesn't exist it will raise an OSError()
        media['size'] = os.path.getsize(
            os.path.join(file_location, added_file))
        media['filename'] = added_file
        media['file_ext'] = os.path.splitext(added_file)[1]
        media['file_path'] = file_location
        media['compressed'] = 0
        media['synced'] = 0
        media['skipped'] = 0
        media['missing'] = 0

        media_files.append(media)

    log.trace('total media files to add %d', len(media_files))
    if media_files:
        log.trace('adding files to torrent')
        datamanager.add_files_to_torrent(torrent, media_files)
        log.trace('files added')
