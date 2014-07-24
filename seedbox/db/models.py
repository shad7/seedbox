"""
Model classes to represent the structures of data.
"""
import inspect

import six


class Model(object):

    """
    Provides base methods for interacting with database model

    :param kwds: keyword parameters and values of the model
    :type kwds: dict
    """
    PK_NAME = 'id'

    def __init__(self, **kwds):
        self.fields = list(kwds)
        for k, v in six.iteritems(kwds):
            setattr(self, k, v)

    def as_dict(self):
        """
        Generates a dictionary representation of the model.

        :return: model as dict
        :rtype: dict
        """
        _d = dict()
        for f in self.fields:
            v = getattr(self, f)
            if isinstance(v, Model):
                v = v.as_dict()
            elif isinstance(v, list) and v and isinstance(v[0], Model):
                v = [sub.as_dict() for sub in v]
            _d[f] = v
        return _d

    def items(self):
        """
        Provides a generator of key-value pair attributes for a model.
        """
        for n in self.fields:
            yield n, getattr(self, n)

    def __eq__(self, other):
        return self.as_dict() == other.as_dict()

    def __iter__(self):
        return iter(self.fields)

    def __getitem__(self, name):
        if name in self.fields:
            return getattr(self, name)
        raise KeyError(name)

    def __setitem__(self, name, value):
        if name not in self.fields:
            raise KeyError(name)
        return setattr(self, name, value)

    def __contains__(self, name):
        try:
            val = getattr(self, name)
            return val is not None
        except AttributeError:
            return False

    def __str__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self.as_dict())

    @classmethod
    def pk_filter(cls, value=None):
        """
        Creates a primary key filter for the given model.

        :param value: primary key value
        :return: primary key filter
        :rtype: dict
        """
        return {cls.PK_NAME: value}

    @classmethod
    def make_empty(cls):
        """
        Create an instance of the model using the defined attributes from the
        parameters of the model.

        :return: model class
        :rtype: :class:`~seedbox.db.models.Model`
        """
        args = inspect.getargspec(cls.__init__).args
        # remove self; always first arg of __init__
        args = args[1:]
        return cls(**dict.fromkeys(args))


class Torrent(Model):
    """
    Represents the attributes of a torrent and the associated state based
    on parsing and processing of the torrent.
    """

    PK_NAME = 'torrent_id'

    def __init__(self, torrent_id, name, created_at=None, updated_at=None,
                 state=None, retry_count=None, failed=None, error_msg=None,
                 invalid=None, purged=None, media_files=None):
        """
        :param int torrent_id: primary key identifier of torrent
        :param str name: name of the torrent file
        :param datetime.datetime created_at: date when db entry created
        :param datetime.datetime updated_at: date when db entry updated
        :param str state: current state of processing of torrent
                          (**init**, **ready**, **active**, **done**,
                          **cancelled**)
        :param int retry_count: number of times entry was reprocessed
        :param bool failed: flag indicating processing failed
        :param str error_msg: error message generated during processing
        :param bool invalid: flag indicating entry was invalid
        :param bool purged: flag indicating entry details were purged
        :param list media_files: list of associated media file(s)
        :return: an instance of the Torrent object
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        Model.__init__(
            self,
            torrent_id=torrent_id,
            name=name,
            created_at=created_at,
            updated_at=updated_at,
            state=state,
            retry_count=retry_count,
            failed=failed,
            error_msg=error_msg,
            invalid=invalid,
            purged=purged,
            media_files=media_files if media_files else []
        )


class MediaFile(Model):
    """
    Represents the attributes of media files associated to a torrent and the
    associated state based on parsing and processing.
    """

    PK_NAME = 'media_id'

    def __init__(self, media_id, torrent_id, filename, file_ext,
                 file_path=None, size=None, compressed=None, synced=None,
                 missing=None, skipped=None, error_msg=None, total_time=None):
        """
        :param int media_id: primary key identifier of media file
        :param int torrent_id: foreign key identifier of torrent
        :param str filename: name of media file
        :param str file_ext: extension of media file
        :param str file_path: location of media file
        :param int size: file size of media file
        :param bool compressed: flag indicating compressed file
        :param bool synced: flag indicating sync to remote location
        :param bool missing: flag indicating file not found on file system
        :param bool skipped: flag indicating if skipped during processing
        :param str error_msg: error message that happened during processing
        :param int total_time: total amount of time to process file
        :return: an instance of the MediaFile object
        :rtype: :class:`~seedbox.db.models.MediaFile`
        """
        Model.__init__(
            self,
            media_id=media_id,
            torrent_id=torrent_id,
            filename=filename,
            file_ext=file_ext,
            file_path=file_path,
            size=size,
            compressed=compressed,
            synced=synced,
            missing=missing,
            skipped=skipped,
            error_msg=error_msg,
            total_time=total_time
        )


class AppState(Model):
    """
    Represents the state of the application and internal processing.
    """

    PK_NAME = 'name'

    def __init__(self, name, value):
        """
        :param name: an identifier for the capturing a state attribute
        :type name: str
        :param value: the data associated with the identifier
        :type value: str | int | bool | datetime.datetime
        :return: an instance of the AppState object
        :rtype: :class:`~seedbox.db.models.AppState`
        """
        Model.__init__(
            self,
            name=name,
            value=value
        )
