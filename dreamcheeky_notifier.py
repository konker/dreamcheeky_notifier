#!/usr/bin/python
#
# dreamcheeky_notifier.py
#
# Copyright 2010 Konrad Markus
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
import usb
import getpass
import imaplib

 
DREAMCHEEKY_VENDOR_ID = 0x1d34
DREAMCHEEKY_PRODUCT_ID = 0x0004
INIT_PACKET1 = (0x1F, 0x01, 0x29, 0x00, 0xB8, 0x54, 0x2C, 0x03)
INIT_PACKET2 = (0x00, 0x01, 0x29, 0x00, 0xB8, 0x54, 0x2C, 0x04)

_LOCK_ = False

# search for vendor device
def find_device(vendor_id, product_id):
    busses = usb.busses()
    for bus in busses:
        for device in bus.devices:
            if device.idVendor == vendor_id and device.idProduct == product_id:
                return device

    return None

def init_device(device):
    configuration = device.configurations[0]
    interface = configuration.interfaces[0][0]
    endpoint = interface.endpoints[0]

    handle = device.open()
    handle.controlMsg(requestType = 0x21,
                      request = 0x09,
                      value = 0x81,
                      index = interface.interfaceNumber,
                      buffer = INIT_PACKET1,
                      timeout = 100)
    handle.controlMsg(requestType = 0x21,
                      request = 0x09,
                      value = 0x81,
                      index = interface.interfaceNumber,
                      buffer = INIT_PACKET2,
                      timeout = 100)

    return (handle, interface.interfaceNumber)

def setRGB(handle, interfaceNumber, r, g, b):
    color_packet = (r, g, b, 0x00, 0x00, 0x54, 0x2C, 0x05)
    handle.controlMsg(requestType = 0x21,
                      request = 0x09,
                      value = 0x81,
                      index = interfaceNumber,
                      buffer = color_packet,
                      timeout = 100)

def check_unread_imap(imap_server, imap_port, imap_ssl, imap_username, imap_password):
    _LOCK_ = True
    if imap_ssl:
        server = imaplib.IMAP4_SSL(imap_server, imap_port)
    else:
        server = imaplib.IMAP4(imap_server, imap_port)
        
    server.login(imap_username, imap_password)
    result, message = server.select('INBOX', readonly=1)

    if result != 'OK':
        sys.stderr.write("Could not select INBOX")
        exit(2)

    typ, msgnums = server.search(None, '(UNSEEN)')

    server.close()
    server.logout()
    _LOCK_ = False

    msgnums = msgnums[0].split(' ')
    return len(msgnums)


def main(imap_server, imap_port, imap_ssl, imap_username, imap_password, twitter_username, twitter_password, poll_delay_secs, twitter_skips, debug=False):
    device = find_device(DREAMCHEEKY_VENDOR_ID, DREAMCHEEKY_PRODUCT_ID)

    if device == None:
        sys.stderr.write("No device found\n")
        exit(1)
        
    (h, i) = init_device(device)
    setRGB(h, i, 0x00, 0x00, 0x00)

    imap_unread = [-1, -1]
    twitter_unread = [-1, None]

    if twitter_username:
        from twitter import Twitter, TwitterError
        twitter = Twitter(twitter_username, twitter_password)        

    try:
        last_color = (0x00, 0x00, 0x00)
        first_loop = True
        cur_twitter_skips = 0
        abandon_twitter = False
        while(1):
            # Check IMAP
            if imap_username:
                imap_unread[0] = check_unread_imap(imap_server, imap_port, imap_ssl, imap_username, imap_password)
                if imap_unread[0] < imap_unread[1]:
                    # user has done something, switch off
                    setRGB(h, i, 0x00, 0x00, 0x00)
                    last_color = (0x00, 0x00, 0x00)
                    imap_unread[1] = imap_unread[0]

                elif imap_unread[0] > imap_unread[1]:
                    # have new messages
                    setRGB(h, i, 0x00, 0x00, 0x40)
                    time.sleep(0.4)
                    setRGB(h, i, 0x00, 0x00, 0x00)
                    time.sleep(0.2)
                    setRGB(h, i, 0x00, 0x00, 0x40)
                    time.sleep(0.4)
                    setRGB(h, i, 0x00, 0x00, 0x00)
                    time.sleep(0.2)
                    setRGB(h, i, 0x00, 0x00, 0x40)
                    last_color = (0x00, 0x00, 0x40)
                    imap_unread[1] = imap_unread[0]

            # Check Twitter
            if twitter_username and not abandon_twitter:
                if first_loop or cur_twitter_skips == twitter_skips:
                    first_loop = False
                    cur_twitter_skips = 0
                    try:
                        twitter_unread[0] = twitter.statuses.home_timeline()
                        if twitter_unread[1] != None:
                            if twitter_unread[0][0]['id'] != twitter_unread[1]:
                                for t in twitter_unread[0]:
                                    if t['id'] == twitter_unread[1]:
                                        twitter_unread[1] = twitter_unread[0][0]['id']
                                        break
                                    else:
                                        setRGB(h, i, 0x40, 0x40, 0x00)
                                        time.sleep(0.75)
                                        setRGB(h, i, last_color[0], last_color[1], last_color[2])
                                        time.sleep(0.2)
                        else:
                            setRGB(h, i, 0x40, 0x40, 0x00)
                            time.sleep(0.5)
                            setRGB(h, i, last_color[0], last_color[1], last_color[2])
                            twitter_unread[1] = twitter_unread[0][0]['id']
                    except TwitterError:
                        # something has gone wrong. abandon
                        abandon_twitter = True
                else:
                    cur_twitter_skips += 1

            time.sleep(poll_delay_secs)

    except KeyboardInterrupt:
        while (_LOCK_):
            time.sleep(0.2)

        setRGB(h, i, 0x00, 0x00, 0x00)
        exit(0)

    except:
        while (_LOCK_):
            time.sleep(0.2)

        setRGB(h, i, 0x00, 0x00, 0x00)

        if debug:
            raise

        while (_LOCK_):
            time.sleep(0.2)

        setRGB(h, i, 0x40, 0x00, 0x00)
        time.sleep(0.4)
        setRGB(h, i, 0x00, 0x00, 0x00)
        time.sleep(0.2)
        setRGB(h, i, 0x40, 0x00, 0x00)
        time.sleep(0.4)
        setRGB(h, i, 0x00, 0x00, 0x00)
        time.sleep(0.2)
        exit(0)

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('--imap-server', dest='imap_server', default='imap.gmail.com',
                      help='IMAP server (default is %default)')
    parser.add_option('--imap-port', type='int', dest='imap_port', default=993,
                      help='IMAP port (default is %default)')
    parser.add_option('--imap-ssl', dest='imap_ssl', action='store_true', default=False,
                      help='Use secure imap connection')
    parser.add_option('--imap-username', dest='imap_username', default=None,
                      help='IMAP username')
    parser.add_option('--imap-password', dest='imap_password', default=None,
                      help='IMAP password')
    parser.add_option('--twitter-username', dest='twitter_username', default=None, 
                      help='Twitter username')
    parser.add_option('--twitter-password', dest='twitter_password', default=None,
                      help='Twitter password')
    parser.add_option('--poll-delay-secs', type='int', dest='poll_delay_secs', default=30,
                      help='Interval in seconds between server checks (default is %default)')
    parser.add_option('--twitter-skips', type='int', dest='twitter_skips', default=3,
                      help='How many times to skip the twitter check. Use this to manage rate limits. (default is %default)')
    parser.add_option('--debug', dest='debug', action='store_true', default=False,
                      help='Debug mode')

    options, args = parser.parse_args()

    imap_password, twitter_password = '',''
    try:
        if options.imap_username != None:
            if options.imap_password == None:
                imap_password = getpass.getpass('IMAP password: ')
            else:
                imap_password = options.imap_password

        if options.twitter_username != None:
            if options.twitter_password == None:
                twitter_password = getpass.getpass('Twitter password: ')
            else:
                twitter_password = options.twitter_password
    except KeyboardInterrupt:
        exit(0)

    main(options.imap_server, options.imap_port, options.imap_ssl, options.imap_username, imap_password, options.twitter_username, twitter_password, options.poll_delay_secs, options.twitter_skips, options.debug)

