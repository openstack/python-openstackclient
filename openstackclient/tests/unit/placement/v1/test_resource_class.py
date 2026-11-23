# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.placement.v1 import resource_class as _resource_class
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.placement.v1 import resource_class
from openstackclient.tests.unit.placement.v1 import fakes as placement_fakes
from openstackclient.tests.unit import utils as test_utils


class TestListResourceClass(placement_fakes.TestPlacement):
    def setUp(self):
        super().setUp()
        self.rc = sdk_fakes.generate_fake_resource(
            _resource_class.ResourceClass,
            name='CUSTOM_BAREMETAL',
        )
        self.placement_client.resource_classes.return_value = iter([self.rc])
        self.cmd = resource_class.ListResourceClass(self.app, None)
        self.expected_columns = ('name',)

    def test_list_resource_class_v2(self):
        self.set_placement_api_version('1.2')
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)

        self.placement_client.resource_classes.assert_called_once_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual([('CUSTOM_BAREMETAL',)], list(data))

    def test_list_resource_class_pre_v2(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestCreateResourceClass(placement_fakes.TestPlacement):
    def setUp(self):
        super().setUp()
        self.rc = sdk_fakes.generate_fake_resource(
            _resource_class.ResourceClass,
            name='CUSTOM_MAGIC',
        )
        self.placement_client.create_resource_class.return_value = self.rc
        self.cmd = resource_class.CreateResourceClass(self.app, None)

    def test_create_resource_class_v2(self):
        self.set_placement_api_version('1.2')
        arglist = ['CUSTOM_MAGIC']
        verifylist = [('name', 'CUSTOM_MAGIC')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.placement_client.create_resource_class.assert_called_once_with(
            name='CUSTOM_MAGIC'
        )

    def test_create_resource_class_pre_v2(self):
        arglist = ['CUSTOM_MAGIC']
        verifylist = [
            ('name', 'CUSTOM_MAGIC'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_no_input(self):
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            [],
            [],
        )
        self.assertEqual([], self.placement_client.mock_calls)


class TestSetResourceClass(placement_fakes.TestPlacement):
    def setUp(self):
        super().setUp()
        self.rc = sdk_fakes.generate_fake_resource(
            _resource_class.ResourceClass,
            name='CUSTOM_MAGIC',
        )
        self.placement_client.update_resource_class.return_value = self.rc
        self.cmd = resource_class.SetResourceClass(self.app, None)

    def test_set_resource_class_v7(self):
        self.set_placement_api_version('1.7')
        arglist = ['CUSTOM_MAGIC']
        verifylist = [('name', 'CUSTOM_MAGIC')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.placement_client.update_resource_class.assert_called_once_with(
            'CUSTOM_MAGIC'
        )

    def test_set_resource_class_pre_v7(self):
        self.set_placement_api_version('1.6')
        arglist = ['CUSTOM_MAGIC']
        verifylist = [
            ('name', 'CUSTOM_MAGIC'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_no_input(self):
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            [],
            [],
        )
        self.assertEqual([], self.placement_client.mock_calls)


class TestShowResourceClass(placement_fakes.TestPlacement):
    def setUp(self):
        super().setUp()
        self.rc = sdk_fakes.generate_fake_resource(
            _resource_class.ResourceClass,
            name='CUSTOM_MAGIC',
        )
        self.placement_client.get_resource_class.return_value = self.rc
        self.cmd = resource_class.ShowResourceClass(self.app, None)
        self.expected_columns = ('name',)

    def test_show_resource_class_v2(self):
        self.set_placement_api_version('1.2')
        arglist = ['CUSTOM_MAGIC']
        verifylist = [('name', 'CUSTOM_MAGIC')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.placement_client.get_resource_class.assert_called_once_with(
            'CUSTOM_MAGIC'
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(('CUSTOM_MAGIC',), tuple(data))

    def test_show_resource_class_pre_v2(self):
        arglist = ['CUSTOM_MAGIC']
        verifylist = [
            ('name', 'CUSTOM_MAGIC'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_no_input(self):
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            [],
            [],
        )
        self.assertEqual([], self.placement_client.mock_calls)


class TestDeleteResourceClass(placement_fakes.TestPlacement):
    def setUp(self):
        super().setUp()
        self.placement_client.delete_resource_class.return_value = None
        self.cmd = resource_class.DeleteResourceClass(self.app, None)

    def test_delete_resource_class_v2(self):
        self.set_placement_api_version('1.2')
        arglist = ['CUSTOM_MAGIC']
        verifylist = [('name', 'CUSTOM_MAGIC')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.placement_client.delete_resource_class.assert_called_once_with(
            'CUSTOM_MAGIC', ignore_missing=False
        )

    def test_delete_resource_class_pre_v2(self):
        arglist = ['CUSTOM_MAGIC']
        verifylist = [
            ('name', 'CUSTOM_MAGIC'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_no_input(self):
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            [],
            [],
        )
        self.assertEqual([], self.placement_client.mock_calls)
