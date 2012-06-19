# pylint: disable-msg=R0903, R0913

import sys
import imaplib
from checker import BaseChecker

class Imap(BaseChecker):
    def __init__(self, imap_host, imap_port, imap_ssl,
                 imap_username, imap_password):
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.imap_ssl = imap_ssl
        self.imap_username = imap_username
        self.imap_password = imap_password
        self.server = None


    def check(self):
        """ Log-in to the given imap account and retreive
            the number of unread messages.
            Returns None if there is a failure. """

        if self.imap_ssl:
            self.server = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
        else:
            self.server = imaplib.IMAP4(self.imap_host, self.imap_port)
            
        self.server.login(self.imap_username, self.imap_password)

        result, _ = self.server.select('INBOX', readonly=1)

        if result != 'OK':
            # TODO: logging
            sys.stderr.write("Could not select INBOX")
            return None

        _, msgnums = self.server.search(None, '(UNSEEN)')

        self.server.close()
        self.server.logout()

        msgnums = msgnums[0].split(' ')
        return len(msgnums)


    def stop(self):
        """ Clean up connections to the IMAP server. """

        if self.server:
            pass
            #self.server.close()
            #self.server.logout()

