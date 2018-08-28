from __future__ import print_function

import string
import doctest


def format_file_name(file_name):
    '''
    >>> format_file_name("oh Yeah!&&")
    'oh_Yeah'
    '''
    valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)
    file_name = ''.join(c for c in file_name if c in valid_chars)
    file_name = file_name.replace(' ', '_')
    return file_name


if __name__ == '__main__':
  doctest.testmod(raise_on_error=False)
