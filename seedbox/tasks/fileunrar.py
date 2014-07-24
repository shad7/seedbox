"""
UnrarFile task plugin for decompressing archived files to specified location.
"""
import logging
import os

from oslo.config import cfg
import rarfile

from seedbox.tasks import base

LOG = logging.getLogger(__name__)


class UnrarFile(base.BaseTask):
    """
    Provides the capability of decompressing archived files to specified
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
        return media_file.compressed

    def execute(self):
        """
        Perform the action associated with task for the provided media_file.
        """
        LOG.debug('decompressing file %s', self.media_file.filename)
        with rarfile.RarFile(
                os.path.join(
                    self.media_file.file_path,
                    self.media_file.filename)) as compressed_file:

            archived_files = compressed_file.namelist()
            compressed_file.extractall(path=cfg.CONF.tasks.sync_path)

        self.add_gen_files(archived_files)
        self.media_file.synced = True
