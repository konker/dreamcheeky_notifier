DreamCheeky USB webmail notifier Python script
==============================================

###Python script to power the Dreamcheeky USB webmail notifier gadget.
####This is shipped with windows only software.

Monitor an IMAP mailbox and/or a twitter account.
New email flashes blue, new tweets flash yellow

Requires PyUSB:
<http://pyusb.berlios.de/>

Twitter support requires Python Twitter Tools:
<http://mike.verdone.ca/twitter/>

Usage: dreamcheeky_notifier.py \[options\]

Options:
    -h, --help                          - show this help message and exit
    --imap-server=IMAP_SERVER           - IMAP server (default is imap.gmail.com)
    --imap-port=IMAP_PORT               - IMAP port (default is 993)
    --imap-ssl                          - Use secure imap connection
    --imap-username=IMAP_USERNAME       - IMAP username
    --imap-password=IMAP_PASSWORD       - IMAP password
    --twitter-username=TWITTER_USERNAME - Twitter username
    --twitter-password=TWITTER_PASSWORD - Twitter password
    --poll-delay-secs=POLL_DELAY_SECS   - Interval in seconds between server checks (default is 30)
    --twitter-skips=TWITTER_SKIPS       - How many times to skip the twitter check.
                                          Use this to manage rate limits. (default is 3)
    --debug                             - Debug mode

NOTE: if a password is omitted from the command line it will be prompted for.
