# vim: tabstop=4 shiftwidth=4 softtabstop=4

from openstackclient import utils as os_utils
from tests import utils

OBJ_LIST = [
                {
                    'id': '123',
                    'name': 'foo',
                    'extra': {
                        'desc': 'foo fu',
                        'status': 'present',
                    }
                },
                {
                    'id': 'abc',
                    'name': 'bar',
                    'extra': {
                        'desc': 'babar',
                        'status': 'waiting',
                    }
                }
            ]


class Obj(object):

    def __init__(self):
        pass


class UtilsTest(utils.TestCase):

    def setUp(self):
        super(UtilsTest, self).setUp()
        self.objs = []
        for o in OBJ_LIST:
            obj = Obj()
            for k in o.keys():
                setattr(obj, k, o.get(k))
            self.objs.append(obj)

    def tearDown(self):
        super(UtilsTest, self).tearDown()
        self.objs = []

    def test_expand_meta(self):
        ret = os_utils.expand_meta(self.objs, 'extra')
        assert (getattr(ret[0], 'desc') == 'foo fu')
        assert (getattr(ret[0], 'status') == 'present')
        assert (getattr(ret[0], 'extra', 'qaz') == 'qaz')
