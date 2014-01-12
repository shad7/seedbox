"""
Provides a base plugin definition for registering options available to all
plugins and the ability to disable any specific plugin via configuration.
"""
from __future__ import absolute_import
from oslo.config import cfg
from seedbox.common import tools

cfg.CONF.register_group(cfg.OptGroup('plugins',
                                     help='Group of common plugin options'))


class BasePlugin(object):

    _VERSION = None

    def __init__(self):
        self._disabled = None

    @property
    def disabled(self):
        """
        property to hold flag indicating if the plugin is disabled.
        """
        if self._disabled is None:
            self._disabled = cfg.CONF['plugins'][
                tools.get_disable_optname(self.__class__.__name__,
                                          self._VERSION)]

        return self._disabled

    def __str__(self):
        """
        Create a string representation of a plugin
        """
        return '{0}: {1}'.format(self.__class__.__name__, self.__dict__)
