"""
Handles all interaction with data model and related persistence.
Basically it provides an interface for all actions you can do to the
objects within our model. Otherwise we could end up with challenges
related to data persistence or even having to understand how things are
persisted outside of the model area.

.. todo::
    Improve performance by investigating bulk operations within sqlobject
    library instead of FOR LOOP. Volumes are currently low but as they
    grow over time it will be a pain point given how often we need to
    update the database.

"""
from __future__ import absolute_import
import logging
import os

from oslo.config import cfg

from seedbox.common import timeutil
from seedbox.common import tools
from seedbox.db import schema

LOG = logging.getLogger(__name__)

CLI_OPTS = [
    cfg.BoolOpt('purge',
                default=False,
                help='DANGER: deletes the database cache and \
                     everything starts over'),
]

cfg.CONF.register_cli_opts(CLI_OPTS, group='db')

cfg.CONF.import_opt('torrent_path', 'seedbox.torrent', group='torrent')


def add_torrent(name):
    """
    Create the initial torrent entry within database and return an instance.

    :param str name:    the name of the torrent file (.torrent)
    :return:            a Torrent instance from database model
    :rtype:             Torrent
    """
    return schema.Torrent(name=name)


def update_state(torrents, state):
    """
    update the list of torrents state attribute to the new state (bulk style)

    :param list torrents:   Torrent instances that need updating
    :param str state:       state/phase associated with Torrent
                            ['init', 'ready', 'active', 'done', 'cancelled']
                            default='init'
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

    :param object torrent:  an instance of Torrent
    :param str exception:   an exception message
    """
    torrent.failed = True
    torrent.error_msg = exception


def set_invalid(torrent):
    torrent.invalid = 1
    torrent.state = schema.CANCELLED


def set_done(torrent):
    torrent.state = schema.DONE


def reset_failed(torrent):
    """
    reset a torrent such that it is eligible to reprocess again

    :param object torrent:  an instance of Torrent
    """
    torrent.failed = False
    torrent.error_msg = None


def fetch_torrent_by_name(name):
    """
    Retrieve torrent by name

    :param str name:    the name of a Torrent (unique/primary key)
    :return:            a Torrent instance from database model
    :rtype:             Torrent
    """
    search = schema.Torrent.selectBy(name=name)
    # because name is unique, it will always be Zero or One entry
    # so we can use the getOne() feature. By passing in None we avoid
    # get back an exception, and therefore we can check for no
    # torrent and simply create it.
    return search.getOne(None)


def fetch_or_create_torrent(name):
    """
    Attempt to fetch the torrent, if not found, then create it

    :param str name:    the name of a Torrent (unique/primary key)
    :return:            a Torrent instance from database model
    :rtype:             Torrent
    """
    torrent = fetch_torrent_by_name(name)

    if not torrent:
        LOG.debug('Torrent [%s] not found; Creating torrent instance...',
                  name)
        torrent = add_torrent(name)

    return torrent


def add_file_to_torrent(torrent, media):
    """
    Add an associated media file to the torrent

    :param object torrent:  an instance of Torrent
    :param dict media:      dict of MediaFile attributes
    """
    schema.MediaFile(filename=media.get('filename'),
                     file_ext=media.get('file_ext'),
                     file_path=media.get('file_path'),
                     size=media.get('size'),
                     compressed=media.get('compressed'),
                     synced=media.get('synced'),
                     missing=media.get('missing'),
                     skipped=media.get('skipped'),
                     torrent=torrent)


def add_files_to_torrent(torrent, file_list):
    """
    Add MediaFile instances to the Torrent

    :param object torrent:  an instance of Torrent
    :param list file_list:  a list of MediaFile instances
    """
    for media in file_list:
        add_file_to_torrent(torrent, media)


def get_files_by_torrent(torrent):
    """
    Retrieves the list of MediaFile for a given Torrent

    :param object torrent:  an instance of Torrent
    :return:                MediaFile instances
    :rtype:                 list
    """
    return list(torrent.media_files)


def get_torrents_by_state(state, failed=False):
    """
    For a given state, retrieve a list of torrents;  by default ignore those
    that are still need to go through retry, but if requested get those
    that need to be retried for a given state.

    :param str state:       state/phase associated with Torrent
                            ['init', 'ready', 'active', 'done', 'cancelled']
    :param bool failed:     a flag indicating to include or not include
                            Torrent that were in failed state.
    :return:                MediaFile instances
    :rtype:                 list
    """
    search = schema.Torrent.selectBy(state=state, failed=failed)

    return list(search)


def delete_torrents(torrents):
    """
    Delete a list of torrents

    :param list torrents:   instances of Torrent
    """
    for torrent in torrents:
        schema.Torrent.delete(id=torrent.id)


def get_eligible_for_purging():
    """
    Search for torrents which the Torrents are eligible for purging.
    Eligible for purging means Torrent is not 'invalid' and not 'purged'
    and state IN [done, cancelled]

    :return:    Torrent instances where the attributes correspond to
                definition of eligible for purging
    :rtype:     list
    """
    where_clause = []
    where_clause.append('torrent.invalid = 0')
    where_clause.append('AND torrent.purged = 0')
    where_clause.append(
        'AND (torrent.state = {0}'.format(
            schema.Torrent.sqlrepr(schema.DONE)))
    where_clause.append(
        'OR torrent.state = {0})'.format(
            schema.Torrent.sqlrepr(schema.CANCELLED)))
    str_where_clause = ' '.join(where_clause)

    LOG.debug('WHERE: [%s]', str_where_clause)
    search = schema.Torrent.select(str_where_clause, distinct=True)

    return list(search)


def get_eligible_for_removal():
    """
    Search for torrents which could be eligible for actual removal.
    Eligible for removal means Torrent is 'purged' and
    state IN [done, cancelled]

    :return:    Torrent instances where the attributes correspond to
                definition of eligible for removal.
    :rtype:     list
    """
    where_clause = []
    where_clause.append('torrent.purged = 1')
    where_clause.append(
        'AND (torrent.state = {0}'.format(
            schema.Torrent.sqlrepr(schema.DONE)))
    where_clause.append(
        'OR torrent.state = {0})'.format(
            schema.Torrent.sqlrepr(schema.CANCELLED)))
    str_where_clause = ' '.join(where_clause)

    LOG.debug('WHERE: [%s]', str_where_clause)
    search = schema.Torrent.select(str_where_clause, distinct=True)

    return list(search)


###
# Helper private implementations; see seedbox.helpers for public interface
# to these private interfaces. All validation, default values, and other
# checks are handled on the public side so we can keep our interface and
# implementation as clean and simple as possible. Also then if someone
# wants to see what is going on, they can see checks there vs. digging around
# in our private implementation.
###

def get_media_files(torrent, file_path, compressed, synced, missing, skipped):
    """
    Search for MediaFile based on any combination of parameter values.

    .. note::
        helpers implementation; No default values for parameters.

    :param object torrent:  a Torrent instance
    :param str file_path:   a file path/directory location. None means ignore
                            the file_path from search.
    :param bool compressed: a flag indicating to include compressed or
                            uncompressed files. None means include both.
    :param bool synced:     a flag indicating to include synced or not synced
                            files. None means include both.
    :param bool missing:    a flag indicating to include missing or not
                            missing files; None means include both.
    :param bool skipped:    a flag indicating to include skipped or not
                            skipped files; None means include both.
    :return:                MediaFile instances or empty list
    :rtype:                 list
    """
    where_clause = []
    where_clause.append('media_file.torrent_id = %d' % torrent.id)

    if file_path is not None:
        where_clause.append(
            'AND media_file.file_path = {0}'.format(
                schema.MediaFile.sqlrepr(file_path)))
    if compressed is not None:
        where_clause.append(
            'AND media_file.compressed = %d' % (1 if compressed else 0))
    if synced is not None:
        where_clause.append(
            'AND media_file.synced = %d' % (1 if synced else 0))
    if missing is not None:
        where_clause.append(
            'AND media_file.missing = %d' % (1 if missing else 0))
    if skipped is not None:
        where_clause.append(
            'AND media_file.skipped = %d' % (1 if skipped else 0))

    str_where_clause = ' '.join(where_clause)

    LOG.debug('WHERE: [%s]', str_where_clause)
    search = schema.MediaFile.select(str_where_clause, distinct=True)

    return list(search)


def get_processed_media_files(torrent):
    """
    Get all media files that fall in the category of processed
    synced = True; missing = True; or skipped = True

    :param object torrent:  an instance of Torrent
    :return:                MediaFile instances matching definition
                            of processed.
    :rtype:                 list
    """
    # if the torrent is been listed as invalid or has been purged
    # already then no need to query for more data.
    if torrent.invalid or torrent.purged:
        LOG.debug('no media files: torrent is invalid or already purged')
        return []

    where_clause = []
    where_clause.append('media_file.torrent_id = %d' % torrent.id)
    where_clause.append('AND (media_file.synced = 1')
    where_clause.append('OR media_file.missing = 1')
    where_clause.append('OR media_file.skipped = 1)')
    str_where_clause = ' '.join(where_clause)

    LOG.debug('WHERE: [%s]', str_where_clause)
    search = schema.MediaFile.select(str_where_clause, distinct=True)

    return list(search)


def purge_media(torrent):
    """
    Delete the corresponding media files from the table based on
    the specified torrent (means all processing is done, so no need to keep
    track of all the files originally associated with torrent.

    :param object torrent:  an instance of Torrent
    """
    schema.MediaFile.deleteBy(torrent=torrent.id)
    torrent.purged = True


###
# Functions for managing the application state data entries
###
def _fetch(name):
    """
    Checks to see if the name already exists in db
    """
    search = schema.AppState.selectBy(name=name)
    # because name is unique, it will always be Zero or One entry
    # so we can use the getOne() feature. By passing in None we avoid
    # get back an exception, and therefore we can check for no
    # results and simply create it if needed
    return search.getOne(None)


def _create(name):
    """
    Creates the new entry in the app state
    """
    return schema.AppState(name=name)


def _fetch_or_create(name):
    """
    convience function that handles retrieving existing entry or creating
    a new one for us.
    """
    entry = _fetch(name)

    if not entry:
        entry = _create(name)

    return entry


def set(name, value):
    """
    set name to value where value is stored as string

    :param str name:    name identifier of AppState item
    :param str value:   the value associated to name
    """
    entry = _fetch_or_create(name)
    entry.val_str = value


def set_int(name, value):
    """
    set name to value where value is stored as int

    :param str name:    name identifier of AppState item
    :param int value:   the value associated to name
    """
    entry = _fetch_or_create(name)
    entry.val_int = tools.to_int(value)


def set_list(name, values):
    """
    set name to value where value is stored as delimited list

    :param str name:    name identifier of AppState item
    :param list values: multiple associated string values associated to name
    """
    entry = _fetch_or_create(name)
    entry.val_list = tools.list_to_str(values)


def set_flag(name, value):
    """
    set name to value where value is stored as boolean

    :param str name:    name identifier of AppState item
    :param bool value:  the boolean/boolean like values associated to name
    """
    entry = _fetch_or_create(name)
    entry.val_flag = tools.to_bool(value)


def set_date(name, value):
    """
    set name to value where value is stored as date; if date is None
    we will let it default to current date.

    :param str name:    name identifier of AppState item
    :param datetime value:  the value associated to name
    """
    entry = _fetch_or_create(name)
    entry.val_date = timeutil.nvl_date(value)


def get(name, default=None):
    """
    retrieve named value where value is stored as string

    :param str name:    name identifier of AppState item
    :param str default: default value to use if item missing
    :return:            AppState value
    :rtype:             str
    """
    entry = _fetch(name)
    return default if not entry else entry.val_str


def get_int(name, default=None):
    """
    retrieve named value where value is stored as int

    :param str name:    name identifier of AppState item
    :param str default: default value to use if item missing
    :return:            AppState value
    :rtype:             int
    """
    entry = _fetch(name)
    return default if not entry else entry.val_int


def get_list(name, default=None):
    """
    retrieve named value where value is stored as delimited list of values

    :param str name:    name identifier of AppState item
    :param str default: default value to use if item missing
    :return:            AppState value
    :rtype:             list
    """
    entry = _fetch(name)
    return default if not entry else tools.to_list(entry.val_list)


def get_flag(name, default=None):
    """
    retrieve named value where value is stored as boolean

    :param str name:    name identifier of AppState item
    :param str default: default value to use if item missing
    :return:            AppState value
    :rtype:             bool
    """
    entry = _fetch(name)
    return default if entry is None else entry.val_flag


def get_date(name, default=None):
    """
    retrieve named value where value is stored as date

    :param str name:    name identifier of AppState item
    :param str default: default value to use if item missing
    :return:            AppState value
    :rtype:             datetime
    """
    entry = _fetch(name)
    return default if not entry else entry.val_date


def _set_last_purge_date(purge_date=None):
    set_date('last_purge_date', purge_date)


def _get_last_purge_date():
    return get_date('last_purge_date')


def initialize():
    """
    Make sure the database is configured and connection established;
    perform clean up activities.
    """
    if cfg.CONF.db.purge:
        schema.purge()
        _set_last_purge_date()
    else:
        schema.clean_db()
        schema.init()
        # step to clean up database
        _perform_db_cleanup()


def _perform_db_cleanup():
    """
    Determine if it is time to clean up the database, if it is then backup
    database and start purging the necessary data.
    """
    LOG.trace('starting perform_db_cleanup...')

    last_purge_date = _get_last_purge_date()
    LOG.debug('last_purge_date: %s', last_purge_date)

    if last_purge_date is None:
        LOG.info('First running...setting last purge date to now')
        # never been purged so need to set an initial date (today)
        _set_last_purge_date()
        return

    if timeutil.is_older_than(last_purge_date, timeutil.ONE_WEEK):
        LOG.trace('last purge > 1 week ago....ready for some clean up.')
        # ready to start purge process....
        torrents = get_eligible_for_purging()
        if torrents:
            LOG.trace('found torrents eligible for purging: %s',
                      len(torrents))
            # perform database backup
            schema.backup()

            LOG.debug('purging media associated with torrents....')
            for torrent in torrents:
                purge_media(torrent)

            # done deleting mediafiles; now delete any torrents that were
            # found to be missing from filesystem thereby no longer in need
            # of caching.
            torrents = get_eligible_for_removal()
            torrents_to_delete = []
            for torrent in torrents:
                if not os.path.exists(os.path.join(
                        cfg.CONF.torrent.torrent_path, torrent.name)):
                    # actual torrent file no longer exists so we can safely
                    # delete the torrent from cache
                    torrents_to_delete.append(torrent)

            LOG.debug('found torrents eligible for removal: %s',
                      len(torrents_to_delete))
            delete_torrents(torrents_to_delete)

            # now reset the last purge date to now.
            _set_last_purge_date()

        else:
            # no torrents eligible for purging
            LOG.debug('no torrents found eligible for purging...')

    LOG.trace('perform_db_cleanup completed')
