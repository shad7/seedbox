import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for database connections."""

    def __init__(self, conf):
        """Constructor."""
        self.conf = conf

    @abc.abstractmethod
    def upgrade(self):
        """Migrate the database to `version` or most recent version."""

    @abc.abstractmethod
    def clear(self):
        """Clear database."""

    @abc.abstractmethod
    def backup(self):
        """Backup database."""

    @abc.abstractmethod
    def shrink_db(self):
        """Shrink database."""

    @abc.abstractmethod
    def save(self, instance):
        """Save the instance to the database."""

    @abc.abstractmethod
    def bulk_create(self, instances):
        """Save the instances in bulk to the database."""

    @abc.abstractmethod
    def bulk_update(self, instances):
        """Save the updated instances in bulk to the database."""

    @abc.abstractmethod
    def delete_by(self, entity_type, qfilter):
        """Delete instances of a specific type based on filter criteria"""

    @abc.abstractmethod
    def delete(self, qfilter):
        """Delete the instance(s) based on filter from the database."""

    @abc.abstractmethod
    def fetch_by(self, entity_type, qfilter):
        """Fetch the instance(s) based on filter from the database."""

    @abc.abstractmethod
    def fetch(self, qfilter):
        """Fetch the instance(s) based on filter from the database."""
