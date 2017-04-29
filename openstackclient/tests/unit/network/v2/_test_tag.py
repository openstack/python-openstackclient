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

from openstackclient.tests.unit import utils as tests_utils


class TestCreateTagMixin(object):
    """Test case mixin to test network tag operation for resource creation.

    * Each test class must create a mock for self.network.set_tags
    * If you test tag operation combined with other options,
      you need to write test(s) directly in individual test cases.
    * The following instance attributes must be defined:

      * _tag_test_resource: Test resource returned by mocked create_<resource>.
      * _tag_create_resource_mock: Mocked create_<resource> method of SDK.
      * _tag_create_required_arglist: List of required arguments when creating
          a resource with default options.
      * _tag_create_required_verifylist: List of expected parsed_args params
          when creating a resource with default options.
      * _tag_create_required_attrs: Expected attributes passed to a mocked
          create_resource method when creating a resource with default options.
    """

    def _test_create_with_tag(self, add_tags=True):
        arglist = self._tag_create_required_arglist[:]
        if add_tags:
            arglist += ['--tag', 'red', '--tag', 'blue']
        else:
            arglist += ['--no-tag']
        verifylist = self._tag_create_required_verifylist[:]
        if add_tags:
            verifylist.append(('tags', ['red', 'blue']))
        else:
            verifylist.append(('no_tag', True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self._tag_create_resource_mock.assert_called_once_with(
            **self._tag_create_required_attrs)
        if add_tags:
            self.network.set_tags.assert_called_once_with(
                self._tag_test_resource,
                tests_utils.CompareBySet(['red', 'blue']))
        else:
            self.assertFalse(self.network.set_tags.called)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_tags(self):
        self._test_create_with_tag(add_tags=True)

    def test_create_with_no_tag(self):
        self._test_create_with_tag(add_tags=False)


class TestListTagMixin(object):
    """Test case mixin to test network tag operation for resource listing.

    * A test resource returned by find_<resource> must contains
      "red" and "green" tags.
    * Each test class must create a mock for self.network.set_tags
    * If you test tag operation combined with other options,
      you need to write test(s) directly in individual test cases.
    * The following instance attributes must be defined:

      * _tag_create_resource_mock: Mocked list_<resource> method of SDK.
    """

    def test_list_with_tag_options(self):
        arglist = [
            '--tags', 'red,blue',
            '--any-tags', 'red,green',
            '--not-tags', 'orange,yellow',
            '--not-any-tags', 'black,white',
        ]
        verifylist = [
            ('tags', ['red', 'blue']),
            ('any_tags', ['red', 'green']),
            ('not_tags', ['orange', 'yellow']),
            ('not_any_tags', ['black', 'white']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self._tag_list_resource_mock.assert_called_once_with(
            **{'tags': 'red,blue',
               'any_tags': 'red,green',
               'not_tags': 'orange,yellow',
               'not_any_tags': 'black,white'}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetTagMixin(object):
    """Test case mixin to test network tag operation for resource update.

    * A test resource returned by find_<resource> must contains
      "red" and "green" tags.
    * Each test class must create a mock for self.network.set_tags
    * If you test tag operation combined with other options,
      you need to write test(s) directly in individual test cases.
    * The following instance attributes must be defined:

      * _tag_resource_name: positional arg name of a resource to be updated.
      * _tag_test_resource: Test resource returned by mocked update_<resource>.
      * _tag_update_resource_mock: Mocked update_<resource> method of SDK.
    """

    def _test_set_tags(self, with_tags=True):
        if with_tags:
            arglist = ['--tag', 'red', '--tag', 'blue']
            verifylist = [('tags', ['red', 'blue'])]
            expected_args = ['red', 'blue', 'green']
        else:
            arglist = ['--no-tag']
            verifylist = [('no_tag', True)]
            expected_args = []
        arglist.append(self._tag_test_resource.name)
        verifylist.append(
            (self._tag_resource_name, self._tag_test_resource.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self._tag_update_resource_mock.called)
        self.network.set_tags.assert_called_once_with(
            self._tag_test_resource,
            tests_utils.CompareBySet(expected_args))
        self.assertIsNone(result)

    def test_set_with_tags(self):
        self._test_set_tags(with_tags=True)

    def test_set_with_no_tag(self):
        self._test_set_tags(with_tags=False)


class TestUnsetTagMixin(object):
    """Test case mixin to test network tag operation for resource update.

    * Each test class must create a mock for self.network.set_tags
    * If you test tag operation combined with other options,
      you need to write test(s) directly in individual test cases.
    * The following instance attributes must be defined:

      * _tag_resource_name: positional arg name of a resource to be updated.
      * _tag_test_resource: Test resource returned by mocked update_<resource>.
      * _tag_update_resource_mock: Mocked update_<resource> method of SDK.
    """

    def _test_unset_tags(self, with_tags=True):
        if with_tags:
            arglist = ['--tag', 'red', '--tag', 'blue']
            verifylist = [('tags', ['red', 'blue'])]
            expected_args = ['green']
        else:
            arglist = ['--all-tag']
            verifylist = [('all_tag', True)]
            expected_args = []
        arglist.append(self._tag_test_resource.name)
        verifylist.append(
            (self._tag_resource_name, self._tag_test_resource.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self._tag_update_resource_mock.called)
        self.network.set_tags.assert_called_once_with(
            self._tag_test_resource,
            tests_utils.CompareBySet(expected_args))
        self.assertIsNone(result)

    def test_unset_with_tags(self):
        self._test_unset_tags(with_tags=True)

    def test_unset_with_all_tag(self):
        self._test_unset_tags(with_tags=False)
