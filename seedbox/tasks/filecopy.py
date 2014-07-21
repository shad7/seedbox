"""
CopyFile task plugin for copying a file to specified location.
"""
import logging
import os
import shutil

from oslo.config import cfg

from seedbox.tasks import base

LOG = logging.getLogger(__name__)


class CopyFile(base.BaseTask):
    """
    Provides the capability of copying files from seeding location to another
    location.
    """

    @staticmethod
    def is_actionable(media_file):
        """
        Perform check to determine if action should be taken.

        :param media_file: an instance of a MediaFile to check
        :returns: a flag indicating to act or not to act
        :rtype: boolean
        """
        return (not media_file.compressed and
                media_file.file_path != cfg.CONF.tasks.sync_path)

    def execute(self):
        """
        Perform the action associated with task for the provided media_file.
        """
        LOG.debug('copying file: %s', self.media_file.filename)
        shutil.copy2(
            os.path.join(self.media_file.file_path,
                         self.media_file.filename),
            cfg.CONF.tasks.sync_path)

        self.media_file.file_path = cfg.CONF.tasks.sync_path
