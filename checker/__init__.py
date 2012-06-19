# pylint: disable-msg=R0903, R0201

class BaseChecker(object):
    """ Base class for checker classes. Must implement the check() method. """

    def check(self):
        """ Should return a positive int or None """
        raise Exception("Not implemented")
