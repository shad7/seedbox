"""
Model classes to represent the structures of data.
"""
import inspect


class Model(object):

    PK_NAME = 'id'

    def __init__(self, **kwds):
        self.fields = list(kwds)
        for k, v in kwds.iteritems():
            setattr(self, k, v)

    def as_dict(self):
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
        return {cls.PK_NAME: value}

    @classmethod
    def make_empty(cls):
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
        Model.__init__(
            self,
            name=name,
            value=value
        )
