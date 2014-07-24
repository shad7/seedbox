"""
DeleteFile task plugin for deleting a file from specified location.
"""
import logging
import os

from oslo.config import cfg

from seedbox.tasks import base

LOG = logging.getLogger(__name__)


class DeleteFile(base.BaseTask):
    """
    Provides capability of deleting file from a specified location.
    """

    @staticmethod
    def is_actionable(media_file):
        """
        Perform check to determine if action should be taken.

        :param media_file: an instance of a MediaFile to check
        :returns: a flag indicating to act or not to act
        :rtype: boolean
        """
        return (media_file.file_path == cfg.CONF.tasks.sync_path and
                media_file.synced and
                os.path.exists(os.path.join(cfg.CONF.tasks.sync_path,
                                            media_file.filename)))

    def execute(self):
        """
        Perform the action associated with task for the provided media_file.
        """
        LOG.debug('delete file: %s', self.media_file.filename)
        os.remove(os.path.join(cfg.CONF.tasks.sync_path,
                               self.media_file.filename))
