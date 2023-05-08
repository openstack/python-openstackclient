#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from osc_lib import exceptions

from openstackclient.network import utils
from openstackclient.tests.unit import utils as tests_utils


class TestUtils(tests_utils.TestCase):
    def test_str2bool(self):
        self.assertTrue(utils.str2bool("true"))
        self.assertTrue(utils.str2bool("True"))
        self.assertTrue(utils.str2bool("TRUE"))
        self.assertTrue(utils.str2bool("TrUe"))

        self.assertFalse(utils.str2bool("false"))
        self.assertFalse(utils.str2bool("False"))
        self.assertFalse(utils.str2bool("FALSE"))
        self.assertFalse(utils.str2bool("FaLsE"))
        self.assertFalse(utils.str2bool("Something else"))
        self.assertFalse(utils.str2bool(""))

        self.assertIsNone(utils.str2bool(None))

    def test_str2list(self):
        self.assertEqual(['a', 'b', 'c'], utils.str2list("a;b;c"))
        self.assertEqual(['abc'], utils.str2list("abc"))

        self.assertEqual([], utils.str2list(""))
        self.assertEqual([], utils.str2list(None))

    def test_str2dict(self):
        self.assertEqual({'a': 'aaa', 'b': '2'}, utils.str2dict('a:aaa;b:2'))
        self.assertEqual(
            {'a': 'aaa;b;c', 'd': 'ddd'}, utils.str2dict('a:aaa;b;c;d:ddd')
        )

        self.assertEqual({}, utils.str2dict(""))
        self.assertEqual({}, utils.str2dict(None))

        self.assertRaises(exceptions.CommandError, utils.str2dict, "aaa;b:2")
