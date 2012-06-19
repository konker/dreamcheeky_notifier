#!/usr/bin/env python
#
# dreamcheeky_notifier.py
#
# Copyright 2012 Konrad Markus
#
# Author: Konrad Markus <konker@gmail.com>
#

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import time
import getpass

from notifier.dreamcheeky import DreamcheekyNotifier
from checker.imap import Imap 

NOW  = 0
PREV = 1

def main(notifier, checker=None, poll_delay_secs=60, debug=False):
    """ main loop """

    if notifier.device is None:
        sys.stderr.write("main: device not found.\n")
        exit(1)

    try:
        notifier.init_device()
    except Exception as ex:
        sys.stderr.write("main: init_device: %s: %s\n" % (type(ex), ex))

        if debug:
            raise

        exit(2)

    notifier.welcome()

    if checker is None:
        sys.stderr.write("main: no checker. exiting.\n")
        exit(0)

    read_count = [None, None]
    try:
        while(1):
            # Check IMAP
            read_count[NOW] = checker.check()

            if read_count[NOW] is None:
                # ignore and carry on
                read_count[NOW] = read_count[PREV]

            if read_count[NOW] < read_count[PREV]:
                # user has done something, switch off
                notifier.off()
                read_count[PREV] = read_count[NOW]

            elif read_count[NOW] > read_count[PREV]:
                # have new messages
                notifier.notify()
                read_count[PREV] = read_count[NOW]

            time.sleep(poll_delay_secs)

    except KeyboardInterrupt:
        notifier.off()
        exit(3)

    except Exception as ex:
        sys.stderr.write("main: %s\n" % ex)
        notifier.error()

        if debug:
            raise

        exit(9)


def parse_options():
    """ Read in command line options. """
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('--imap-host', dest='imap_host',
                      default='imap.gmail.com',
                      help='IMAP host (default is %default)')
    parser.add_option('--imap-port', type='int', dest='imap_port',
                      default=993,
                      help='IMAP port (default is %default)')
    parser.add_option('--imap-ssl', dest='imap_ssl', action='store_true',
                      default=False,
                      help='Use secure imap connection')
    parser.add_option('--imap-username', dest='imap_username',
                      default=None,
                      help='IMAP username')
    parser.add_option('--imap-password', dest='imap_password',
                      default=None,
                      help='IMAP password')
    parser.add_option('--poll-delay-secs', type='int', dest='poll_delay_secs',
                      default=30,
                      help='Interval in seconds between server checks (default is %default)')
    parser.add_option('--debug', dest='debug', action='store_true',
                      default=False,
                      help='Debug mode')

    options, _ = parser.parse_args()

    # if password not given on command line, read it in
    try:
        if options.imap_username != None:
            if options.imap_password == None:
                options.imap_password = getpass.getpass('IMAP password: ')
            else:
                options.imap_password = options.imap_password
    except KeyboardInterrupt:
        exit(0)

    return options


if __name__ == '__main__':

    OPTS = parse_options()
    NOTIFIER = DreamcheekyNotifier()
    IMAP = Imap(OPTS.imap_host, OPTS.imap_port, OPTS.imap_ssl,
                OPTS.imap_username, OPTS.imap_password)

    main(NOTIFIER, IMAP, OPTS.poll_delay_secs, OPTS.debug)

