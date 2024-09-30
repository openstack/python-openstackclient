#   Copyright 2013 Nebula Inc.
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

from openstack import exceptions as sdk_exceptions
from openstack.identity.v3 import service as _service
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.identity.v3 import service
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestServiceCreate(identity_fakes.TestIdentityv3):
    columns = (
        'id',
        'name',
        'type',
        'enabled',
        'description',
    )

    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)

        self.datalist = (
            self.service.id,
            self.service.name,
            self.service.type,
            True,
            self.service.description,
        )
        self.identity_sdk_client.create_service.return_value = self.service

        # Get the command object to test
        self.cmd = service.CreateService(self.app, None)

    def test_service_create_name(self):
        arglist = [
            '--name',
            self.service.name,
            self.service.type,
        ]
        verifylist = [
            ('name', self.service.name),
            ('description', None),
            ('is_enabled', True),
            ('type', self.service.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.create_service.assert_called_with(
            name=self.service.name,
            type=self.service.type,
            description=None,
            is_enabled=True,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_service_create_description(self):
        arglist = [
            '--description',
            self.service.description,
            self.service.type,
        ]
        verifylist = [
            ('name', None),
            ('description', self.service.description),
            ('is_enabled', True),
            ('type', self.service.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.create_service.assert_called_with(
            name=None,
            type=self.service.type,
            description=self.service.description,
            is_enabled=True,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_service_create_enable(self):
        arglist = [
            '--enable',
            self.service.type,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('is_enabled', True),
            ('type', self.service.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.create_service.assert_called_with(
            name=None,
            type=self.service.type,
            description=None,
            is_enabled=True,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_service_create_disable(self):
        arglist = [
            '--disable',
            self.service.type,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('is_enabled', False),
            ('type', self.service.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.create_service.assert_called_with(
            name=None,
            type=self.service.type,
            description=None,
            is_enabled=False,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestServiceDelete(identity_fakes.TestIdentityv3):
    service = sdk_fakes.generate_fake_resource(_service.Service)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.get_service.side_effect = (
            sdk_exceptions.ResourceNotFound
        )
        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.delete_service.return_value = None

        # Get the command object to test
        self.cmd = service.DeleteService(self.app, None)

    def test_service_delete_no_options(self):
        arglist = [
            self.service.name,
        ]
        verifylist = [
            ('service', [self.service.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_service.assert_called_with(
            self.service.id,
        )
        self.assertIsNone(result)


class TestServiceList(identity_fakes.TestIdentityv3):
    service = sdk_fakes.generate_fake_resource(_service.Service)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.services.return_value = [self.service]

        # Get the command object to test
        self.cmd = service.ListService(self.app, None)

    def test_service_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.services.assert_called_with()

        collist = ('ID', 'Name', 'Type')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.service.id,
                self.service.name,
                self.service.type,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_service_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.services.assert_called_with()

        collist = ('ID', 'Name', 'Type', 'Description', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.service.id,
                self.service.name,
                self.service.type,
                self.service.description,
                True,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestServiceSet(identity_fakes.TestIdentityv3):
    service = sdk_fakes.generate_fake_resource(_service.Service)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.get_service.side_effect = (
            sdk_exceptions.ResourceNotFound
        )
        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.update_service.return_value = self.service

        # Get the command object to test
        self.cmd = service.SetService(self.app, None)

    def test_service_set_no_options(self):
        arglist = [
            self.service.name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', None),
            ('is_enabled', None),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_service_set_type(self):
        arglist = [
            '--type',
            self.service.type,
            self.service.name,
        ]
        verifylist = [
            ('type', self.service.type),
            ('name', None),
            ('description', None),
            ('is_enabled', None),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'type': self.service.type,
        }
        self.identity_sdk_client.update_service.assert_called_with(
            self.service.id, **kwargs
        )
        self.assertIsNone(result)

    def test_service_set_name(self):
        arglist = [
            '--name',
            self.service.name,
            self.service.name,
        ]
        verifylist = [
            ('type', None),
            ('name', self.service.name),
            ('description', None),
            ('is_enabled', None),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.service.name,
        }
        self.identity_sdk_client.update_service.assert_called_with(
            self.service.id, **kwargs
        )
        self.assertIsNone(result)

    def test_service_set_description(self):
        arglist = [
            '--description',
            self.service.description,
            self.service.name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', self.service.description),
            ('is_enabled', None),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.service.description,
        }
        self.identity_sdk_client.update_service.assert_called_with(
            self.service.id, **kwargs
        )
        self.assertIsNone(result)

    def test_service_set_enable(self):
        arglist = [
            '--enable',
            self.service.name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', None),
            ('is_enabled', True),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': True,
        }
        self.identity_sdk_client.update_service.assert_called_with(
            self.service.id, **kwargs
        )
        self.assertIsNone(result)

    def test_service_set_disable(self):
        arglist = [
            '--disable',
            self.service.name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', None),
            ('is_enabled', False),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': False,
        }
        self.identity_sdk_client.update_service.assert_called_with(
            self.service.id, **kwargs
        )
        self.assertIsNone(result)


class TestServiceShow(identity_fakes.TestIdentityv3):
    service = sdk_fakes.generate_fake_resource(_service.Service)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.get_service.side_effect = (
            sdk_exceptions.ResourceNotFound
        )
        self.identity_sdk_client.find_service.return_value = self.service

        # Get the command object to test
        self.cmd = service.ShowService(self.app, None)

    def test_service_show(self):
        arglist = [
            self.service.name,
        ]
        verifylist = [
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_service.assert_called_with(
            self.service.name, ignore_missing=False
        )

        collist = ('id', 'name', 'type', 'enabled', 'description')
        self.assertEqual(collist, columns)
        datalist = (
            self.service.id,
            self.service.name,
            self.service.type,
            True,
            self.service.description,
        )
        self.assertEqual(datalist, data)

    def test_service_show_nounique(self):
        self.identity_sdk_client.find_service.side_effect = (
            sdk_exceptions.DuplicateResource(None)
        )
        arglist = [
            'nounique_service',
        ]
        verifylist = [
            ('service', 'nounique_service'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                "DuplicateResource",
                str(e),
            )
