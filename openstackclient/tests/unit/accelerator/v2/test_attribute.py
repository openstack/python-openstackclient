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

from unittest.mock import call

from openstack.accelerator.v2 import attribute as _attribute
from openstack import exceptions as sdk_exceptions
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.accelerator.v2 import attribute
from openstackclient.tests.unit.accelerator.v2 import (
    fakes as accelerator_fakes,
)

SHOW_COLUMNS = (
    "created_at",
    "updated_at",
    "uuid",
    "deployable_id",
    "key",
    "value",
)

LIST_COLUMNS_SHORT = (
    "uuid",
    "deployable_id",
    "key",
    "value",
)

LIST_COLUMNS_LONG = (*LIST_COLUMNS_SHORT, "created_at", "updated_at")


class TestAttribute(accelerator_fakes.TestAccelerator):
    def setUp(self):
        super().setUp()

        self.fake_attr = sdk_fakes.generate_fake_resource(_attribute.Attribute)
        self.data = tuple(self.fake_attr[col] for col in SHOW_COLUMNS)


class TestCreateAttribute(TestAttribute):
    def setUp(self):
        super().setUp()

        self.accelerator_client.create_attribute.return_value = self.fake_attr
        self.cmd = attribute.CreateAttribute(self.app, None)

    def test_create(self):
        arglist = ['dep-id-1', 'trait:key', 'required']
        verifylist = [
            ('deployable_id', 'dep-id-1'),
            ('key', 'trait:key'),
            ('value', 'required'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.create_attribute.assert_called_once_with(
            deployable_id='dep-id-1',
            key='trait:key',
            value='required',
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)


class TestDeleteAttribute(TestAttribute):
    def setUp(self):
        super().setUp()

        self.fake_attrs = list(
            sdk_fakes.generate_fake_resources(_attribute.Attribute, 2)
        )
        self.cmd = attribute.DeleteAttribute(self.app, None)

    def test_delete(self):
        arglist = [self.fake_attrs[0].uuid]
        verifylist = [
            ('attributes', [self.fake_attrs[0].uuid]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.accelerator_client.delete_attribute.assert_called_once_with(
            self.fake_attrs[0].uuid,
            ignore_missing=False,
        )

    def test_delete_multiple(self):
        arglist = [a.uuid for a in self.fake_attrs]
        verifylist = [
            ('attributes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        calls = [call(a.uuid, ignore_missing=False) for a in self.fake_attrs]
        self.accelerator_client.delete_attribute.assert_has_calls(calls)

    def test_delete_with_error(self):
        arglist = [
            self.fake_attrs[0].uuid,
            'nonexistent',
        ]
        verifylist = [
            ('attributes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.accelerator_client.delete_attribute.side_effect = [
            None,
            sdk_exceptions.NotFoundException,
        ]

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 attributes failed to delete.',
                str(e),
            )


class TestListAttribute(TestAttribute):
    def setUp(self):
        super().setUp()

        self.accelerator_client.attributes.return_value = [self.fake_attr]
        self.cmd = attribute.ListAttribute(self.app, None)

    def test_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.attributes.assert_called_once_with()
        self.assertEqual(LIST_COLUMNS_SHORT, columns)

        expected_data = (
            tuple(self.fake_attr[col] for col in LIST_COLUMNS_SHORT),
        )
        self.assertCountEqual(expected_data, tuple(data))

    def test_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(LIST_COLUMNS_LONG, columns)

        expected_data = (
            tuple(self.fake_attr[col] for col in LIST_COLUMNS_LONG),
        )
        self.assertCountEqual(expected_data, tuple(data))


class TestShowAttribute(TestAttribute):
    def setUp(self):
        super().setUp()

        self.accelerator_client.get_attribute.return_value = self.fake_attr
        self.cmd = attribute.ShowAttribute(self.app, None)

    def test_show(self):
        arglist = [self.fake_attr.uuid]
        verifylist = [
            ('attribute', self.fake_attr.uuid),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.get_attribute.assert_called_once_with(
            self.fake_attr.uuid
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)
