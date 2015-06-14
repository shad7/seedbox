"""Process flow

The core process flow for managing the syncing of torrents to remote location.
"""
import logging

from seedbox import db
from seedbox.process import manager
from seedbox.process import workflow
from seedbox.torrent import loader

LOG = logging.getLogger(__name__)


def _get_work(dbapi):

    # search through the directory of torrents and load any
    # new ones into the cache.
    loader.load_torrents(dbapi)

    flows = []
    # now retrieve any torrents that are eligible for processing
    # and kick off the workflows.
    for tor in dbapi.get_torrents_active():
        # need to make sure there are actually media files that
        # were parsed for the torrent.
        LOG.debug('torrent %s media files: %s',
                  tor.torrent_id, tor.media_files)
        if tor.media_files:
            LOG.debug('creating workflow for torrent: %s', tor)
            flows.append(workflow.Workflow(dbapi, tor))

    return flows


def start():
    """The primary entry point for the process"""
    dbapi = db.dbapi()
    mgr = manager.TaskManager()
    flows = []

    try:
        while True:

            # if no flows which should happen on initial run
            # or after processing all the previously found
            # torrents.
            if not flows:
                # attempt to load the torrents and generate
                # workflows for each active torrent
                flows = _get_work(dbapi)
                # if still no torrents break out
                if not flows:
                    break

            # for each flow get the next list of tasks to process
            for wf in flows:
                mgr.add_tasks(list(wf.next_tasks()))

            # now execute the via TaskManager
            results = mgr.run()
            for item in results:
                LOG.debug('saving media: %s', item)
                # the results should be the updated media so save it
                dbapi.save_media(item)

            # for each flow execute it, if wf is done then remove it
            # from the list.
            for wf in flows:
                if wf.run():
                    flows.remove(wf)
    finally:
        mgr.shutdown()
        dbapi.clean_up()
