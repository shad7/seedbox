#!/usr/bin/python

from itertools import ifilter
import logging, logging.config
import ordereddict
import os, sys

__version__ = '0.1'

# adding logging extension here given how minimal this is
# didn't seem to make sense to create a whole module for something
# so simple; if things change later we can move it then
class TraceLogger(logging.Logger):
    """
    Need to keep some low level logging messages included in case a bug
    ever pops up in the future, but this gives me the ability to separate
    tracing the propram from the actual basic debugging.
    """

    # a bit more detail than normal debug
    TRACE = 5

    def trace(self, msg, *args, **kwargs):
        """
        Log at TRACE level (more detailed than DEBUG).
        """
        self.log(TraceLogger.TRACE, msg, *args, **kwargs)


# Set our custom logger class as default; need to make sure
# the class has been defined before we set this; then add corresponding 
# level to be supported; then do the default configuring from our default
# configuration file. all done
logging.setLoggerClass(TraceLogger)
logging.addLevelName(TraceLogger.TRACE, 'TRACE')
logging.config.fileConfig('logging.cfg', disable_existing_loggers=False)

# now that we have our Logger defined we can access it
log = logging.getLogger('main')

from sqlobject import *
from sqlobject.sqlbuilder import *
from seedbox.model.schema import Torrent, MediaFile

def fetch_media(torrent_id):
    """
    Get media by torrent_id
    """
    search = MediaFile.selectBy(torrent=torrent_id)

    return list(search)

def fetch_torrent(name):
    """
    Retrieve torrent by name
    """
    torrent = None
    print 'Looking up torrent [%s]' % name

    search = Torrent.selectBy(name=name)

    # because name is unique, it will always be Zero or One entry
    # so we can use the getOne() feature. By passing in None we avoid
    # get back an exception, and therefore we can check for no
    # torrent and simply create it.
    torrent = search.getOne(None)

    if not torrent:
        print 'Not found: Create it...'
        torrent = Torrent(name=name)

    print 'torrent: [%s]' % torrent
    print 'Torrent: name=[%s] crDate=[%s]' % (torrent.name, torrent.create_date)

    return torrent

def add_all_media(torrent, files):
    """
    Add all media files found on a single torrent
    """
    for media in files:
        (name, ext) = media.split('.')
        MediaFile(filename=name, file_ext='.'+ext, size=100, torrent=torrent)



tornames = ['xxxx.torrent', 'xxxxx5.torrent', 'xxxx10.torrent', 'x1.torrent', 'XXXX10.torrent', 'test2.torrent']
mediafiles = ['vid11.mp4', 'vid2.mp4', 'vid3.mp4', 'vid4.mp4', 'vid5.avi']

for torname in tornames:
    torrent = fetch_torrent(torname)
    print 'fetched_torrent [%s]: result: [%s]' % (torname, torrent)
    add_all_media(torrent,  mediafiles)


torrent = fetch_torrent('xxxx.torrent')
tor_media = torrent.media_files
print 'Media [%s]' % list(tor_media)
print 'Torrent Media: [%s]' % tor_media.count()

for media in tor_media:
    print 'file [%s] ext [%s]' % (media.filename, media.file_ext)

exts = ['.it', '.db', '.avi', '.jd']

ext_check = lambda media: media.file_ext in exts
# now filter out any files that don't match the supplied file_ext list
results = list(ifilter(ext_check, tor_media))

print 'media filtered...[%s]' % results

for media in results:
    print 'filtered file [%s] ext [%s]' % (media.filename, media.file_ext)

print 'Torrent table: [%s]' % Torrent.sqlmeta.table
print 'Torrent Columns: [%s]' % Torrent.sqlmeta.columns.keys()
print 'Torrent Columns: [%s]' % Torrent.sqlmeta.columnList

print 'MediaFile table: [%s]' % MediaFile.sqlmeta.table
print 'MediaFile Columns: [%s]' % MediaFile.sqlmeta.columns.keys()
print 'MediaFile Columns: [%s]' % MediaFile.sqlmeta.columnList

#torrent = fetch_torrent('xxxx.torrent')
#
#for media_file in tor_media:
#    print 'deleting media file: [%s]' % media_file
#    MediaFile.delete(id=media_file.id)
#
#torrent = fetch_torrent('xxxx.torrent')
#tor_media = torrent.media_files
#print 'Media [%s]' % tor_media
#print 'Torrent Media: [%s]' % tor_media.count()
#
#MediaFile.deleteBy(torrent=torrent.id)
#
#torrent = fetch_torrent('xxxx.torrent')
#tor_media = torrent.media_files
#print 'Media [%s]' % tor_media
#print 'Torrent Media: [%s]' % tor_media.count()




