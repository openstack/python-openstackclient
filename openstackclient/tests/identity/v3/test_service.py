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

import copy

from openstackclient.identity.v3 import service
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes


class TestService(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestService, self).setUp()

        # Get a shortcut to the ServiceManager Mock
        self.services_mock = self.app.client_manager.identity.services
        self.services_mock.reset_mock()


class TestServiceCreate(TestService):

    def setUp(self):
        super(TestServiceCreate, self).setUp()

        self.services_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = service.CreateService(self.app, None)

    def test_service_create_name(self):
        arglist = [
            '--name', identity_fakes.service_name,
            identity_fakes.service_type,
        ]
        verifylist = [
            ('name', identity_fakes.service_name),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('type', identity_fakes.service_type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name=, type=, enabled=, **kwargs)
        self.services_mock.create.assert_called_with(
            name=identity_fakes.service_name,
            type=identity_fakes.service_type,
            description=None,
            enabled=True,
        )

        collist = ('description', 'enabled', 'id', 'name', 'type')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.service_description,
            True,
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
        )
        self.assertEqual(datalist, data)

    def test_service_create_description(self):
        arglist = [
            '--description', identity_fakes.service_description,
            identity_fakes.service_type,
        ]
        verifylist = [
            ('name', None),
            ('description', identity_fakes.service_description),
            ('enable', False),
            ('disable', False),
            ('type', identity_fakes.service_type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name=, type=, enabled=, **kwargs)
        self.services_mock.create.assert_called_with(
            name=None,
            type=identity_fakes.service_type,
            description=identity_fakes.service_description,
            enabled=True,
        )

        collist = ('description', 'enabled', 'id', 'name', 'type')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.service_description,
            True,
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
        )
        self.assertEqual(datalist, data)

    def test_service_create_enable(self):
        arglist = [
            '--enable',
            identity_fakes.service_type,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('enable', True),
            ('disable', False),
            ('type', identity_fakes.service_type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name=, type=, enabled=, **kwargs)
        self.services_mock.create.assert_called_with(
            name=None,
            type=identity_fakes.service_type,
            description=None,
            enabled=True,
        )

        collist = ('description', 'enabled', 'id', 'name', 'type')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.service_description,
            True,
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
        )
        self.assertEqual(datalist, data)

    def test_service_create_disable(self):
        arglist = [
            '--disable',
            identity_fakes.service_type,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('enable', False),
            ('disable', True),
            ('type', identity_fakes.service_type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name=, type=, enabled=, **kwargs)
        self.services_mock.create.assert_called_with(
            name=None,
            type=identity_fakes.service_type,
            description=None,
            enabled=False,
        )

        collist = ('description', 'enabled', 'id', 'name', 'type')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.service_description,
            True,
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
        )
        self.assertEqual(datalist, data)


class TestServiceDelete(TestService):

    def setUp(self):
        super(TestServiceDelete, self).setUp()

        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )
        self.services_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = service.DeleteService(self.app, None)

    def test_service_delete_no_options(self):
        arglist = [
            identity_fakes.service_name,
        ]
        verifylist = [
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        self.services_mock.delete.assert_called_with(
            identity_fakes.service_id,
        )


class TestServiceList(TestService):

    def setUp(self):
        super(TestServiceList, self).setUp()

        self.services_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.SERVICE),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = service.ListService(self.app, None)

    def test_service_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.services_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Type')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_service_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.services_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Type', 'Description', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
            identity_fakes.service_description,
            True,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestServiceSet(TestService):

    def setUp(self):
        super(TestServiceSet, self).setUp()

        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )
        self.services_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = service.SetService(self.app, None)

    def test_service_set_no_options(self):
        arglist = [
            identity_fakes.service_name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

    def test_service_set_type(self):
        arglist = [
            '--type', identity_fakes.service_type,
            identity_fakes.service_name,
        ]
        verifylist = [
            ('type', identity_fakes.service_type),
            ('name', None),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'type': identity_fakes.service_type,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            identity_fakes.service_id,
            **kwargs
        )

    def test_service_set_name(self):
        arglist = [
            '--name', identity_fakes.service_name,
            identity_fakes.service_name,
        ]
        verifylist = [
            ('type', None),
            ('name', identity_fakes.service_name),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'name': identity_fakes.service_name,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            identity_fakes.service_id,
            **kwargs
        )

    def test_service_set_description(self):
        arglist = [
            '--description', identity_fakes.service_description,
            identity_fakes.service_name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', identity_fakes.service_description),
            ('enable', False),
            ('disable', False),
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'description': identity_fakes.service_description,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            identity_fakes.service_id,
            **kwargs
        )

    def test_service_set_enable(self):
        arglist = [
            '--enable',
            identity_fakes.service_name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', None),
            ('enable', True),
            ('disable', False),
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            identity_fakes.service_id,
            **kwargs
        )

    def test_service_set_disable(self):
        arglist = [
            '--disable',
            identity_fakes.service_name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', None),
            ('enable', False),
            ('disable', True),
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            identity_fakes.service_id,
            **kwargs
        )


class TestServiceShow(TestService):

    def setUp(self):
        super(TestServiceShow, self).setUp()

        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = service.ShowService(self.app, None)

    def test_service_show(self):
        arglist = [
            identity_fakes.service_name,
        ]
        verifylist = [
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.get(id)
        self.services_mock.get.assert_called_with(
            identity_fakes.service_name,
        )

        collist = ('description', 'enabled', 'id', 'name', 'type')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.service_description,
            True,
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
        )
        self.assertEqual(datalist, data)
