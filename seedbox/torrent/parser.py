"""Parses a torrent file."""
import io
import logging
import os

import six

from seedbox.torrent import bencode

LOG = logging.getLogger(__name__)


class ParsingError(Exception):
    """Holds parsing error messages.

    Error class representing errors that occur while parsing
    the torrent content.
    """
    def __init__(self, error_msg):
        Exception.__init__(self)
        self.error_msg = error_msg

    def __str__(self):
        return repr(self.error_msg)


DICT_TOKEN = 'd'
LIST_TOKEN = 'l'
INT_TOKEN = 'i'
END_TOKEN = 'e'
NEGATIVE = '-'
STR_SEP_TOKEN = ':'


class Bdecode(object):

    def __init__(self, data):
        self.data = six.BytesIO(data)

    def _next_char(self):
        return self.data.read(1).decode('utf-8', 'replace')

    def _prev_char(self):
        # offset: -1
        # mode/whence: SEEK_CUR => 1
        self.data.seek(-1, 1)

    def _parse_str(self):
        self._prev_char()
        str_len = self._parse_number(delimiter=STR_SEP_TOKEN)

        if not str_len:
            raise ParsingError(
                'Empty string length found while parsing at position %d'
                % self.data.tell())

        return self.data.read(str_len)

    def _parse_int(self):
        return self._parse_number(delimiter=END_TOKEN)

    def _parse_number(self, delimiter):
        parsed_int = ''
        while True:
            parsed_int_char = self._next_char()
            if parsed_int_char != NEGATIVE and not parsed_int_char.isdigit():
                if parsed_int_char != delimiter:
                    raise ParsingError(
                        'Invalid character %s found after parsing an '
                        'integer (%s expected) at position %d.' %
                        (parsed_int_char, delimiter, self.data.tell()))
                else:
                    break

            parsed_int += parsed_int_char

        return int(parsed_int)

    def _parse_dict(self):
        parsed_dict = {}
        while True:
            dict_key = self.decode()
            if not dict_key:
                # End of dict
                break
            # parse value
            dict_value = self.decode()
            if isinstance(dict_value, six.binary_type):
                dict_value = dict_value.decode('utf-8', 'replace')
            parsed_dict.setdefault(dict_key.decode('utf-8'),
                                   dict_value)

        return parsed_dict

    def _parse_list(self):
        parsed_list = []
        while True:
            list_item = self.decode()
            if not list_item:
                # End of list
                break

            if isinstance(list_item, six.binary_type):
                list_item = list_item.decode('utf-8', 'replace')
            parsed_list.append(list_item)

        return parsed_list

    def decode(self):
        """Decode torrent content.

        :returns: parsed content
        """
        parsed_char = self._next_char()

        if parsed_char == END_TOKEN:
            return None

        elif parsed_char == INT_TOKEN:
            return self._parse_int()

        elif parsed_char.isdigit():
            return self._parse_str()

        elif parsed_char == DICT_TOKEN:
            return self._parse_dict()

        elif parsed_char == LIST_TOKEN:
            return self._parse_list()

    @classmethod
    def parse(cls, data):
        """Helper method that creates decoder and decodes content.

        :returns: parsed content
        """
        return cls(data).decode()


class TorrentParser(object):

    def __init__(self, filepath):
        """Reads the torrent file and parses content.

        :param str filepath: Path to the torrent file to be parsed
        :raises IOError: when a file does not exists
        """
        if not os.path.exists(filepath):
            raise IOError('No file found at %s' % filepath)

        self.file = filepath
        self._content = None

    @property
    def content(self):
        if self._content is None:
            self._content = self.load_content()
        return self._content

    def load_content(self):
        """Reads the torrent file and decodes content.

        .. note::
            bencode is supremely more efficient parser for torrents but
            extremely strict in the format of the file. A custom parser based
            on another implementation handles parsing that is more flexible
            but it is not as efficient. Therefore when the file is well formed
            bencode is used but if it fails then the custom parser is used.
            If the custom parser fails then a ParsingError is raised.
        """

        with io.open(file=self.file, mode='rb') as handle:
            content = handle.read()

        try:
            return bencode.bdecode(content)
        except bencode.BTFailure as bterr:
            LOG.info('bencode.bdecode failed: (%s); trying alternate approach',
                     bterr)
            return Bdecode.parse(content)

    def get_file_details(self):
        """Retrieves details of the file(s) contained in the torrent.

        File details tuple:
            * name
            * length (size)

        :returns: file details embedded within torrent
        :rtype: list of tuples (name, length)
        """
        parsed_files_info = []
        files_info = self.content.get(b'info')
        if not files_info:
            return parsed_files_info

        multiple_files_info = files_info.get(b'files')
        LOG.debug('files: %s', multiple_files_info)
        if multiple_files_info:
            # the name attribute was holding the directory name that each
            # of the multiple files were contained within.
            dir_name = files_info.get(b'name').decode('utf-8')
            LOG.debug('dirname: %s', dir_name)

            for file_info in multiple_files_info:
                LOG.debug('file_info: %s', file_info)
                # simply append the directory to the concatenated list
                # of items under path, mostly it is a single item.
                parsed_files_info.append(
                    (os.path.join(dir_name,
                                  os.path.sep.join(
                                      [x.decode('utf-8') for x in
                                       file_info.get(b'path')])),
                     file_info.get(b'length')))
        else:
            parsed_files_info.append(
                (files_info.get(b'name').decode('utf-8'),
                 files_info.get(b'length')))

        return parsed_files_info
