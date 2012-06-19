##DreamCheeky USB webmail notifier Python script

Python script to power the Dreamcheeky USB webmail notifier gadget which is shipped with windows only software.

- - -

Requires PyUSB:  
<https://github.com/walac/pyusb>
Note: Requires pyusb 1.0. Ubuntu/Debian package installs pyusb 0.4.

- - -
Monitor an IMAP mailbox, new email flashes blue.

````
Usage: dreamcheeky_notifier.py [options]

Options:
    -h, --help                          - show this help message and exit
    --imap-host=IMAP_HOST               - IMAP server host (default is imap.gmail.com)
    --imap-port=IMAP_PORT               - IMAP port (default is 993)
    --imap-ssl                          - Use secure imap connection
    --imap-username=IMAP_USERNAME       - IMAP username
    --imap-password=IMAP_PASSWORD       - IMAP password
    --poll-delay-secs=POLL_DELAY_SECS   - Interval in seconds between server checks (default is 30)
                                          Use this to manage rate limits. (default is 3)
    --debug                             - Debug mode
````

NOTE: if a password is omitted from the command line it will be prompted for.

NOTE: should be run as root unless the necessary udev rules are set.

