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

LOCK = False


def init_device(device):
    """ Initialize the device before usage. """

    if device.is_kernel_driver_active(0) is True:
        device.detach_kernel_driver(0)

    device.set_configuration()

    device.ctrl_transfer(0x21, 0x09, 0x81, 0, INIT_PACKET1, 100)
    device.ctrl_transfer(0x21, 0x09, 0x81, 0, INIT_PACKET2, 100) 

    return device


def set_rgb(device, red, green, blue):
    """ Set the device to the give (red,green,blue) colour.
        Each component is an int 0x00 - 0x40 """

    color_packet = (red, green, blue, 0x00, 0x00, 0x54, 0x2C, 0x05)
    device.ctrl_transfer(0x21, 0x09, 0x81, 0, color_packet, 100)


def check_unread_imap(imap_server, imap_port, imap_ssl,
                      imap_username, imap_password):
    """ Log-in to the given imap account and retreive
        the number of unread messages.
        Returns -1 if there is a failure. """

    global LOCK

    LOCK = True
    if imap_ssl:
        server = imaplib.IMAP4_SSL(imap_server, imap_port)
    else:
        server = imaplib.IMAP4(imap_server, imap_port)
        
    try:
        server.login(imap_username, imap_password)
    except Exception as ex:
        sys.stderr.write("imap:server.login: %s\n" % ex)
        exit(4)

    result, _ = server.select('INBOX', readonly=1)

    if result != 'OK':
        sys.stderr.write("Could not select INBOX")
        #exit(2)
        return -1

    _, msgnums = server.search(None, '(UNSEEN)')

    server.close()
    server.logout()
    LOCK = False

    msgnums = msgnums[0].split(' ')
    return len(msgnums)


def main(imap_server, imap_port, imap_ssl, imap_username, imap_password,
         twitter_username, twitter_password, poll_delay_secs, twitter_skips,
         debug=False):
    """ main loop """

    device = usb.core.find(idVendor=DREAMCHEEKY_VENDOR_ID,
                           idProduct=DREAMCHEEKY_PRODUCT_ID)

    if device is None:
        sys.stderr.write("Device not found")
        exit(3)

    try:
        init_device(device)
    except Exception as ex:
        sys.stderr.write("init_device: %s\n" % ex)
        exit(2)

    # welcome pulse
    set_rgb(device, 0x00, 0x00, 0x40)
    time.sleep(0.5)
    set_rgb(device, 0x00, 0x00, 0x00)
    time.sleep(0.2)
    set_rgb(device, 0x00, 0x40, 0x00)
    time.sleep(0.5)
    set_rgb(device, 0x00, 0x00, 0x00)
    time.sleep(0.2)
    set_rgb(device, 0x40, 0x00, 0x00)
    time.sleep(0.5)
    set_rgb(device, 0x00, 0x00, 0x00)

    if twitter_username is None and imap_username is None:
        exit(0)

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
                imap_unread[0] = check_unread_imap(imap_server, imap_port,
                                                   imap_ssl,
                                                   imap_username, imap_password)
                if imap_unread[0] == 1:
                    imap_unread[0] = imap_unread[1]

                if imap_unread[0] < imap_unread[1]:
                    # user has done something, switch off
                    set_rgb(device, 0x00, 0x00, 0x00)
                    last_color = (0x00, 0x00, 0x00)
                    imap_unread[1] = imap_unread[0]

                elif imap_unread[0] > imap_unread[1]:
                    # have new messages
                    set_rgb(device, 0x00, 0x00, 0x40)
                    time.sleep(0.4)
                    set_rgb(device, 0x00, 0x00, 0x00)
                    time.sleep(0.2)
                    set_rgb(device, 0x00, 0x00, 0x40)
                    time.sleep(0.4)
                    set_rgb(device, 0x00, 0x00, 0x00)
                    time.sleep(0.2)
                    set_rgb(device, 0x00, 0x00, 0x40)
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
                                for tweet in twitter_unread[0]:
                                    if tweet['id'] == twitter_unread[1]:
                                        twitter_unread[1] = twitter_unread[0][0]['id']
                                        time.sleep(0.75)
                                        set_rgb(device, last_color[0], last_color[1], last_color[2])
                                        time.sleep(0.2)
                        else:
                            set_rgb(device, 0x40, 0x40, 0x00)
                            time.sleep(0.5)
                            set_rgb(device, last_color[0], last_color[1], last_color[2])
                            twitter_unread[1] = twitter_unread[0][0]['id']
                    except TwitterError:
                        # something has gone wrong. abandon
                        abandon_twitter = True
                else:
                    cur_twitter_skips += 1

            time.sleep(poll_delay_secs)

    except KeyboardInterrupt:
        while (LOCK):
            time.sleep(0.2)

        set_rgb(device, 0x00, 0x00, 0x00)
        exit(0)

    except:
        while (LOCK):
            time.sleep(0.2)

        set_rgb(device, 0x00, 0x00, 0x00)

        if debug:
            raise

        while (LOCK):
            time.sleep(0.2)

        set_rgb(device, 0x40, 0x00, 0x00)
        time.sleep(0.4)
        set_rgb(device, 0x00, 0x00, 0x00)
        time.sleep(0.2)
        set_rgb(device, 0x40, 0x00, 0x00)
        time.sleep(0.4)
        set_rgb(device, 0x00, 0x00, 0x00)
        time.sleep(0.2)
        exit(0)


def parse_options():
    """ Read in command line options. """

    parser = OptionParser()

    parser.add_option('--imap-server', dest='imap_server',
                      default='imap.gmail.com',
                      help='IMAP server (default is %default)')
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
    parser.add_option('--twitter-username', dest='twitter_username',
                      default=None, 
                      help='Twitter username')
    parser.add_option('--twitter-password', dest='twitter_password',
                      default=None,
                      help='Twitter password')
    parser.add_option('--poll-delay-secs', type='int', dest='poll_delay_secs',
                      default=30,
                      help='Interval in seconds between server checks (default is %default)')
    parser.add_option('--twitter-skips', type='int', dest='twitter_skips',
                      default=3,
                      help='How many times to skip the twitter check. Use this to manage rate limits. (default is %default)')
    parser.add_option('--debug', dest='debug', action='store_true',
                      default=False,
                      help='Debug mode')

    options, _ = parser.parse_args()

    try:
        if options.imap_username != None:
            if options.imap_password == None:
                options.imap_password = getpass.getpass('IMAP password: ')
            else:
                options.imap_password = options.imap_password

        if options.twitter_username != None:
            if options.twitter_password == None:
                options.twitter_password = getpass.getpass('Twitter password: ')
            else:
                options.twitter_password = options.twitter_password
    except KeyboardInterrupt:
        exit(0)

    return options

if __name__ == '__main__':
    from optparse import OptionParser

    OPTS = parse_options()

    main(OPTS.imap_server, OPTS.imap_port, OPTS.imap_ssl,
         OPTS.imap_username, OPTS.imap_password,
         OPTS.twitter_username, OPTS.twitter_password,
         OPTS.poll_delay_secs, OPTS.twitter_skips, OPTS.debug)

