"""
An abstract class representing the required capabilities of a database API.
"""
import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for database connections."""

    def __init__(self, conf):
        """
        :param conf: an instance of configuration file
        :type conf: oslo.config.cfg.ConfigOpts
        """
        self.conf = conf

    @abc.abstractmethod
    def upgrade(self):
        """Migrate the database to `version` or most recent version."""
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self):
        """Clear database."""
        raise NotImplementedError

    @abc.abstractmethod
    def backup(self):
        """Backup database."""
        raise NotImplementedError

    @abc.abstractmethod
    def shrink_db(self):
        """Shrink database."""
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, instance):
        """Save the instance to the database.
        :param instance: an instance of modeled data object
        """
        raise NotImplementedError

    @abc.abstractmethod
    def bulk_create(self, instances):
        """Save the instances in bulk to the database.
        :param instances: a list of instance of modeled data object
        """
        raise NotImplementedError

    @abc.abstractmethod
    def bulk_update(self, value_map, entity_type, qfilter):
        """Save the updated instances in bulk to the database.
        :param value_map: a dict of key-value pairs representing the data of
        an instance.
        :param entity_type: the model type
        :param qfilter: query filter to determine which rows to update
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by(self, entity_type, qfilter):
        """Delete instances of a specific type based on filter criteria
        :param entity_type: the model type
        :param qfilter: query filter to determine which rows to update
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, instance):
        """Delete the instance(s) based on filter from the database.
        :param instance: an instance of modeled data object
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_by(self, entity_type, qfilter):
        """Fetch the instance(s) based on filter from the database.
        :param entity_type: the model type
        :param qfilter: query filter to determine which rows to update
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch(self, entity_type, pk):
        """Fetch the instance(s) based on filter from the database.
        :param entity_type: the model type
        :param pk: primary key value
        """
        raise NotImplementedError
