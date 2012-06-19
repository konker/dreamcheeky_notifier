
# pylint: disable-msg=R0903, R0201

class BaseNotifier(object):
    """ Base class for notifier classes. """

    def welcome(self):
        """ Optional welcome notification. """
        pass

    def error(self):
        """ Optional error notification. """
        pass

    def notify(self):
        """ Optional positive notification. """
        pass

    def off(self):
        """ Optionally switch off. """
        pass
