"""
Parses a torrent file and provides method to access the following attributes.
    * Tracker URL
    * Creation date
    * Client name, if any
    * For each file
        * name
        * length
        * checksum

Created on 2012-03-07

@author: mohanr
"""
from datetime import datetime
import io
import logging
import os

import six

from seedbox.torrent import bencode

LOG = logging.getLogger(__name__)


def _is_int(val):
    ret_val = True
    try:
        int(val)
    except ValueError:
        ret_val = False

    return ret_val


class ParsingError(Exception):
    """ Error class representing errors that occur while parsing
    the torrent content.
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

    .. note::
        bencode is supremely more efficient parser of torrents but extremely
        strict in the format of the file. The custom parser is an
        implementation that someone wrote that does a good job of parsing
        but it is not very efficient. So we are going to pair the two
        solutions together. when the file is well formed we will leverage
        most efficient standard but we will leverage the custom parser when
        bencode generates an exception. If the custom parser fails then it
        is really invalid file and the consumer will handle it
        correspondingly.

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
            self.torr_str = six.BytesIO(torr_str)
            self.curr_char = None

        def next_char(self):
            """
            to provide 2 ways of accessing the current parsed char -
                1. as return value,
                2. as self.curr_char (useful in some circumstances)
            """
            self.curr_char = self.torr_str.read(1).decode('utf-8', 'replace')
            return self.curr_char

        def step_back(self, position=-1, mode=1):
            """ Step back, by default, 1 position relative to the
            current position.

            :param position: offset from current position
            :param mode: current position
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
                if not _is_int(parsed_int_char):
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

        .. todo::

            Investigate merging logic from custom parser into bencode code
            base such that a single unit of code supports parsing.

        :param str torrent_file_path: Path to the torrent file to be parsed
        :raises IOError:    when a torrent_file_path does not exists
        """
        if not torrent_file_path or not isinstance(torrent_file_path,
                                                   six.string_types):
            raise ValueError('Path of the torrent file not provided')

        if not os.path.exists(torrent_file_path):
            raise IOError('No file found at %s'.format(torrent_file_path))

        with io.open(file=torrent_file_path, mode='rb') as handle:
            self.torrent_content = handle.read()

        # bencode is supremely more efficient parser of torrents but extremely
        # strict in the format of the file. The custom parser is an
        # implementation that someone wrote that does a good job of parsing
        # but it is not very efficient. So we are going to pair the two
        # solutions together. when the file is well formed we will leverage
        # most efficient standard but we will leverage the custom parser when
        # bencode generates an exception. If the custom parser fails then it
        # is really invalid file and the consumer will handle it
        # correspondingly.
        try:
            self.parsed_content = bencode.bdecode(self.torrent_content)
        except bencode.BTFailure as bterr:
            LOG.info('bencode.bdecode failed: ({0});'
                     'trying alternate approach'.format(bterr))
            self.torrent_str = self._TorrentStr(self.torrent_content)
            self.parsed_content = self._parse_torrent()

    def get_tracker_url(self):
        """
        Retrieves tracker URL from the parsed torrent file

        :returns:   tracker URL from parsed torrent file
        :rtype:     str
        """
        return self.parsed_content.get(b'announce')

    def get_creation_date(self, time_format='iso'):
        """
        Retrieves creation date of the torrent, if present, in ISO
        time_format from the parsed torrent file.

        :param str time_format: determines the time_format of the time value
                                returned. ['iso', 'datetime'] defaults: 'iso'
        :returns:               creation date
        :rtype:                 datetime
        """
        time_stamp = self.parsed_content.get(b'creation date')
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

        :returns:   name of the client that created the torrent
        :rtype:     str
        """
        return self.parsed_content.get(b'created by')

    def get_files_details(self):
        """
        Parses torrent file and returns details of the files contained
        in the torrent.

        File details tuple:
            * name
            * length (size)
            * checksum (of file in the torrent)

        :returns:   file details embedded within torrent
        :rtype:     list of tuples (name, length, checksum)
        """
        parsed_files_info = []
        files_info = self.parsed_content.get(b'info')
        # 'info' should be present in all torrent files. Nevertheless..
        if files_info:
            multiple_files_info = files_info.get(b'files')
            LOG.debug('files: |{0}|'.format(multiple_files_info))
            if multiple_files_info:  # multiple-file torrent
                # the name attribute was holding the directory name that each
                # of the multiple files were contained within.
                dir_name = files_info.get(b'name').decode('utf-8')
                LOG.debug('dirname: |{0}|'.format(dir_name))
                for file_info in multiple_files_info:
                    LOG.debug('file_info: |{0}|'.format(file_info))
                    # simply append the directory to the concatenated list
                    # of items under path, mostly it is a single item.
                    parsed_files_info.append(
                        (os.path.join(dir_name,
                                      os.path.sep.join(
                                          [x.decode('utf-8') for x in
                                           file_info.get(b'path')])),
                         file_info.get(b'length'),))
            else:  # single file torrent
                parsed_files_info.append(
                    (files_info.get(b'name').decode('utf-8'),
                     files_info.get(b'length'), ))

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

        elif _is_int(parsed_char):  # string
            self.torrent_str.step_back()
            return self.torrent_str.parse_str()

        elif parsed_char == self.DICT_START:
            parsed_dict = {}
            while True:
                dict_key = self._parse_torrent()
                if not dict_key:
                    break  # End of dict
                dict_value = self._parse_torrent()  # parse value
                if isinstance(dict_value, six.binary_type):
                    dict_value = dict_value.decode('utf-8', 'replace')
                parsed_dict.setdefault(dict_key.decode('utf-8'),
                                       dict_value)

            return parsed_dict

        elif parsed_char == self.LIST_START:
            parsed_list = []
            while True:
                list_item = self._parse_torrent()
                if not list_item:
                    break  # End of list

                if isinstance(list_item, six.binary_type):
                    list_item = list_item.decode('utf-8', 'replace')
                parsed_list.append(list_item)

            return parsed_list
