#!/usr/bin/python
"""
Parses a torrent file and provides method to access the following attributes.
    . Tracker URL
    . Creation date
    . Client name, if any
    . For each file
        . name
        . length
        . checksum

Created on 2012-03-07

@author: mohanr
"""
from __future__ import absolute_import
from datetime import datetime
from StringIO import StringIO
import os
import string
import types


def humanize_bytes(in_bytes, precision=1):
    """Return a humanized string representation of a number of bytes.

    >>> humanize_bytes(1)
    '1 byte'
    >>> humanize_bytes(1024)
    '1.0 kB'
    >>> humanize_bytes(1024*123)
    '123.0 kB'
    >>> humanize_bytes(1024*12342)
    '12.1 MB'
    >>> humanize_bytes(1024*12342,2)
    '12.05 MB'
    >>> humanize_bytes(1024*1234,2)
    '1.21 MB'
    >>> humanize_bytes(1024*1234*1111,2)
    '1.31 GB'
    >>> humanize_bytes(1024*1234*1111,1)
    '1.3 GB'
    """
    abbrevs = (
        (1<<50L, 'PB'),
        (1<<40L, 'TB'),
        (1<<30L, 'GB'),
        (1<<20L, 'MB'),
        (1<<10L, 'kB'),
        (1, 'bytes')
    )

    if in_bytes == 1:
        return '1 byte'

    factor = None
    suffix = None
    for factor, suffix in abbrevs:
        if in_bytes >= factor:
            break

    return '%.*f %s' % (precision, in_bytes / factor, suffix)

class ParsingError(Exception):
    """ Error class representing errors that occur while parsing
    the torrent content.
    """
    def __init__(self, error_msg):
        Exception.__init__(self)
        self.error_msg = error_msg        
    
    def __str__(self):
        return repr(self.error_msg) 

class MalformedTorrentError(Exception):
    """ Error class representing a malformed torrent when required
    attributes are missing
    """
    def __init__(self, error_msg):
        Exception.__init__(self)
        self.error_msg = error_msg        

    def __str__(self):
        return repr(self.error_msg) 


class TorrentParser(object):
    """
    Parses a torrent file and returns various properties based on the 
    content of the torrent file.
    """
        
    DICT_START = 'd'
    LIST_START = 'l'
    DICT_LIST_END = 'e'
    DICT_KEY_VALUE_SEP = ': '
    DICT_LIST_ITEM_SEP = ', '
    INT_START = 'i'    
    
    class _TorrentStr(object):
        """ StringIO wrapper over the torrent string. 
        
            TODO:
                . Create unittests to cover this class.
                . Should this rather extend StringIO class. Explore.
        """
        
        STR_LEN_VALUE_SEP = ':'
        INT_END = 'e'    
        
        def __init__(self, torr_str):
            self.torr_str = StringIO(torr_str)
            self.curr_char = None
        
        def next_char(self):
            """
            to provide 2 ways of accessing the current parsed char - 
                1. as return value,
                2. as self.curr_char (useful in some circumstances)
            """
            self.curr_char = self.torr_str.read(1)
            return self.curr_char
        
        def step_back(self, position=-1, mode=1):
            """ Step back, by default, 1 position relative to the 
            current position.
            """
            self.torr_str.seek(position, mode) 
        
        def parse_str(self):
            """ Parse and return a string from the torrent file content. 
            Format <string length>:<string>
            
                Returns:
                    Parsed string (from the current position).
                Raises:
                    ParsingError, when expected string format is not 
                    encountered.
            
                TODO: 
                    . Explore using regex to accomplish the parsing.            
            """                                   
            str_len = self._parse_number(delimiter=self.STR_LEN_VALUE_SEP)
            
            if not str_len:
                raise ParsingError(
                    'Empty string length found while parsing at position %d'
                     % self.torr_str.pos)
            
            return self.torr_str.read(str_len)        
            
        def parse_int(self):
            """ Parse and return an integer from the torrent file content.
            Format i[0-9]+e

                Returns:
                    Parsed integer (from the current position).
                Raises:
                    ParsingError, when expected integer format is not
                    encountered.
            
                TODO: 
                    . Explore using regex to accomplish the parsing.
                    . Could re-purpose this function to parse str_length.
            """
            # just to make sure we are parsing the integer of correct format
            self.step_back()
            
            if self.next_char() != TorrentParser.INT_START:
                raise ParsingError(
                    'Error while parsing for an integer. Found %s at \
                    position %d while %s is expected.' % 
                    (self.curr_char,
                    self.torr_str.pos,
                    TorrentParser.INT_START))
                            
            return self._parse_number(delimiter=self.INT_END)
        
        def _parse_number(self, delimiter):
            """
            Parses a sequence of digits representing either an integer or
            string length and returns the number.
            """
            parsed_int = ''
            while True:
                parsed_int_char = self.next_char()
                if parsed_int_char not in string.digits:
                    if parsed_int_char != delimiter:
                        raise ParsingError(
                            'Invalid character %s found after parsing an \
                            integer (%s expected) at position %d.' % 
                            (parsed_int_char, delimiter, self.torr_str.pos))
                    else:                                          
                        break
                
                parsed_int += parsed_int_char
                
            return int(parsed_int)
       

    def __init__(self, torrent_file_path):
        """
        Reads the torrent file and sets the content as an object attribute.
        
        Args:
            torrent_file_path - String containing path to the torrent file
            to be parsed
        Returns:
            None
        Raises:
            ValueError - when passed arg is not of string type
            IOError - when the string arg passed points to a non-existent file
                    
        """
        if not isinstance(
            torrent_file_path, types.StringType) and not isinstance(
                torrent_file_path, types.UnicodeType):
            raise ValueError(
                'Path of the torrent file expected in string format.'
                )
        
        if not os.path.exists(torrent_file_path):
            raise IOError("No file found at '%s'" % torrent_file_path)
        
        self.torrent_file = open(torrent_file_path)
        self.torrent_content = self.torrent_file.read()
        self.torrent_str = self._TorrentStr(self.torrent_content)
        
        self.parsed_content = self._parse_torrent()
  
    def get_tracker_url(self):
        """ Returns the tracker URL from the parsed torrent file. """        
        return self.parsed_content.get('announce')

    
    def get_creation_date(self, time_format='iso'):
        """ Returns creation date of the torrent, if present, in ISO 
        time_format from the parsed torrent file.
            
            Args:
                time_format - determines the time_format of the time value 
                returned. 
                Valid values 'iso' or 'datetime'.
                Defaults to 'iso'.        
        """
        time_stamp = self.parsed_content.get('creation date')
        if time_stamp:
            time_stamp = datetime.utcfromtimestamp(time_stamp)
            
            if time_format == 'iso':
                return time_stamp.isoformat()
            else:
                return time_stamp
            
    
    def get_client_name(self):
        """
        Returns the name of the client that created the torrent if present,
        from the parsed torrent file.
        """
        return self.parsed_content.get('created by')

    def get_files_details(self):
        """
        Parses torrent file and returns details of the files contained
        in the torrent. Details include name, length and checksum for each
        file in the torrent.
        """
        parsed_files_info = []
        files_info = self.parsed_content.get('info')
        # 'info' should be present in all torrent files. Nevertheless.. 
        if files_info:
            multiple_files_info = files_info.get('files')
            if multiple_files_info: # multiple-file torrent
                # the name attribute was holding the directory name that each
                # of the multiple files were contained within.
                dir_name = files_info.get('name')
                for file_info in multiple_files_info:
                    # simply append the directory to the concatenated list
                    # of items under path, mostly it is a single item.
                    parsed_files_info.append(
                        (os.path.join(dir_name, os.path.sep.join(file_info.get('path'))),
                            file_info.get('length'),))
            else: # single file torrent
                parsed_files_info.append((files_info.get('name'),
                    files_info.get('length'), ))
            
        return parsed_files_info            
    
    
    def _parse_torrent(self):
        """
        Parse the torrent content in bencode format into python data format.
        
            Returns:
                A dictionary containing info parsed from torrent file.
                                
        """
        parsed_char = self.torrent_str.next_char()
        
        if not parsed_char:
             # EOF
            return
        
        # Parsing logic 
        if parsed_char == self.DICT_LIST_END: 
            return
        
        elif parsed_char == self.INT_START:
            return self.torrent_str.parse_int()
        
        elif parsed_char in string.digits: # string
            self.torrent_str.step_back()
            return self.torrent_str.parse_str()
        
        elif parsed_char == self.DICT_START:
            parsed_dict = {}
            while True:
                dict_key = self._parse_torrent()
                if not dict_key: 
                    break # End of dict                
                dict_value = self._parse_torrent() # parse value
                parsed_dict.setdefault(dict_key, dict_value)               
            
            return parsed_dict        
        
        elif parsed_char == self.LIST_START:
            parsed_list = []
            while True:
                list_item = self._parse_torrent()
                if not list_item: 
                    break # End of list  
                parsed_list.append(list_item)
            
            return parsed_list                
        
        
if __name__ == '__main__':
        
    source_dir = '/home/shad/projects/seed-sync/orig/torrentparse-master/test_data'
    files = os.listdir(u""+source_dir)

    for test_file in files:
        tp = TorrentParser(os.path.join(source_dir, test_file))
        print tp.get_tracker_url()
        print tp.get_creation_date()
        print tp.get_client_name()
        print tp.get_files_details()
        print '*' * 80

