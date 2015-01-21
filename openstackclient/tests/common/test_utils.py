#   Copyright 2012-2013 OpenStack, LLC.
#
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

import mock

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.tests import utils as test_utils

PASSWORD = "Pa$$w0rd"
WASSPORD = "Wa$$p0rd"
DROWSSAP = "dr0w$$aP"


class TestUtils(test_utils.TestCase):

    def test_get_password_good(self):
        with mock.patch("getpass.getpass", return_value=PASSWORD):
            mock_stdin = mock.Mock()
            mock_stdin.isatty = mock.Mock()
            mock_stdin.isatty.return_value = True
            self.assertEqual(PASSWORD, utils.get_password(mock_stdin))

    def test_get_password_bad_once(self):
        answers = [PASSWORD, WASSPORD, DROWSSAP, DROWSSAP]
        with mock.patch("getpass.getpass", side_effect=answers):
            mock_stdin = mock.Mock()
            mock_stdin.isatty = mock.Mock()
            mock_stdin.isatty.return_value = True
            self.assertEqual(DROWSSAP, utils.get_password(mock_stdin))

    def test_get_password_no_tty(self):
        mock_stdin = mock.Mock()
        mock_stdin.isatty = mock.Mock()
        mock_stdin.isatty.return_value = False
        self.assertRaises(exceptions.CommandError,
                          utils.get_password,
                          mock_stdin)

    def test_get_password_cntrl_d(self):
        with mock.patch("getpass.getpass", side_effect=EOFError()):
            mock_stdin = mock.Mock()
            mock_stdin.isatty = mock.Mock()
            mock_stdin.isatty.return_value = True
            self.assertRaises(exceptions.CommandError,
                              utils.get_password,
                              mock_stdin)

    def get_test_items(self):
        item1 = {'a': 1, 'b': 2}
        item2 = {'a': 1, 'b': 3}
        item3 = {'a': 2, 'b': 2}
        item4 = {'a': 2, 'b': 1}
        return [item1, item2, item3, item4]

    def test_sort_items_with_one_key(self):
        items = self.get_test_items()
        sort_str = 'b'
        expect_items = [items[3], items[0], items[2], items[1]]
        self.assertEqual(expect_items, utils.sort_items(items, sort_str))

    def test_sort_items_with_multiple_keys(self):
        items = self.get_test_items()
        sort_str = 'a,b'
        expect_items = [items[0], items[1], items[3], items[2]]
        self.assertEqual(expect_items, utils.sort_items(items, sort_str))

    def test_sort_items_all_with_direction(self):
        items = self.get_test_items()
        sort_str = 'a:desc,b:desc'
        expect_items = [items[2], items[3], items[1], items[0]]
        self.assertEqual(expect_items, utils.sort_items(items, sort_str))

    def test_sort_items_some_with_direction(self):
        items = self.get_test_items()
        sort_str = 'a,b:desc'
        expect_items = [items[1], items[0], items[2], items[3]]
        self.assertEqual(expect_items, utils.sort_items(items, sort_str))

    def test_sort_items_with_object(self):
        item1 = mock.Mock(a=1, b=2)
        item2 = mock.Mock(a=1, b=3)
        item3 = mock.Mock(a=2, b=2)
        item4 = mock.Mock(a=2, b=1)
        items = [item1, item2, item3, item4]
        sort_str = 'b,a'
        expect_items = [item4, item1, item3, item2]
        self.assertEqual(expect_items, utils.sort_items(items, sort_str))

    def test_sort_items_with_empty_key(self):
        items = self.get_test_items()
        sort_srt = ''
        self.assertEqual(items, utils.sort_items(items, sort_srt))
        sort_srt = None
        self.assertEqual(items, utils.sort_items(items, sort_srt))

    def test_sort_items_with_invalid_key(self):
        items = self.get_test_items()
        sort_str = 'c'
        self.assertRaises(exceptions.CommandError,
                          utils.sort_items,
                          items, sort_str)

    def test_sort_items_with_invalid_direction(self):
        items = self.get_test_items()
        sort_str = 'a:bad_dir'
        self.assertRaises(exceptions.CommandError,
                          utils.sort_items,
                          items, sort_str)


class NoUniqueMatch(Exception):
    pass


class TestFindResource(test_utils.TestCase):
    def setUp(self):
        super(TestFindResource, self).setUp()
        self.name = 'legos'
        self.expected = mock.Mock()
        self.manager = mock.Mock()
        self.manager.resource_class = mock.Mock()
        self.manager.resource_class.__name__ = 'lego'

    def test_find_resource_get_int(self):
        self.manager.get = mock.Mock(return_value=self.expected)
        result = utils.find_resource(self.manager, 1)
        self.assertEqual(self.expected, result)
        self.manager.get.assert_called_with(1)

    def test_find_resource_get_int_string(self):
        self.manager.get = mock.Mock(return_value=self.expected)
        result = utils.find_resource(self.manager, "2")
        self.assertEqual(self.expected, result)
        self.manager.get.assert_called_with(2)

    def test_find_resource_get_uuid(self):
        uuid = '9a0dc2a0-ad0d-11e3-a5e2-0800200c9a66'
        self.manager.get = mock.Mock(return_value=self.expected)
        result = utils.find_resource(self.manager, uuid)
        self.assertEqual(self.expected, result)
        self.manager.get.assert_called_with(uuid)

    def test_find_resource_get_whatever(self):
        self.manager.get = mock.Mock(return_value=self.expected)
        result = utils.find_resource(self.manager, 'whatever')
        self.assertEqual(self.expected, result)
        self.manager.get.assert_called_with('whatever')

    def test_find_resource_find(self):
        self.manager.get = mock.Mock(side_effect=Exception('Boom!'))
        self.manager.find = mock.Mock(return_value=self.expected)
        result = utils.find_resource(self.manager, self.name)
        self.assertEqual(self.expected, result)
        self.manager.get.assert_called_with(self.name)
        self.manager.find.assert_called_with(name=self.name)

    def test_find_resource_find_not_found(self):
        self.manager.get = mock.Mock(side_effect=Exception('Boom!'))
        self.manager.find = mock.Mock(
            side_effect=exceptions.NotFound(404, "2")
        )
        result = self.assertRaises(exceptions.CommandError,
                                   utils.find_resource,
                                   self.manager,
                                   self.name)
        self.assertEqual("No lego with a name or ID of 'legos' exists.",
                         str(result))
        self.manager.get.assert_called_with(self.name)
        self.manager.find.assert_called_with(name=self.name)

    def test_find_resource_find_no_unique(self):
        self.manager.get = mock.Mock(side_effect=Exception('Boom!'))
        self.manager.find = mock.Mock(side_effect=NoUniqueMatch())
        result = self.assertRaises(exceptions.CommandError,
                                   utils.find_resource,
                                   self.manager,
                                   self.name)
        self.assertEqual("More than one lego exists with the name 'legos'.",
                         str(result))
        self.manager.get.assert_called_with(self.name)
        self.manager.find.assert_called_with(name=self.name)

    def test_format_dict(self):
        expected = "a='b', c='d', e='f'"
        self.assertEqual(expected,
                         utils.format_dict({'a': 'b', 'c': 'd', 'e': 'f'}))
        self.assertEqual(expected,
                         utils.format_dict({'e': 'f', 'c': 'd', 'a': 'b'}))

    def test_format_list(self):
        expected = 'a, b, c'
        self.assertEqual(expected, utils.format_list(['a', 'b', 'c']))
        self.assertEqual(expected, utils.format_list(['c', 'b', 'a']))
