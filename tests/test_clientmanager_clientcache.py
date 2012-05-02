
from openstackclient.common import clientmanager


def factory(inst):
    return object()


class Container(object):

    attr = clientmanager.ClientCache(factory)

    def init_token(self):
        return


def test_singleton():
    # Verify that the ClientCache descriptor only
    # invokes the factory one time and always
    # returns the same value after that.
    c = Container()
    assert c.attr is c.attr
