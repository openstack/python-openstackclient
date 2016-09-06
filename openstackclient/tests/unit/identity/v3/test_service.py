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

from keystoneclient import exceptions as identity_exc
from osc_lib import exceptions

from openstackclient.identity.v3 import service
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestService(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestService, self).setUp()

        # Get a shortcut to the ServiceManager Mock
        self.services_mock = self.app.client_manager.identity.services
        self.services_mock.reset_mock()


class TestServiceCreate(TestService):

    columns = (
        'description',
        'enabled',
        'id',
        'name',
        'type',
    )

    def setUp(self):
        super(TestServiceCreate, self).setUp()

        self.service = identity_fakes.FakeService.create_one_service()
        self.datalist = (
            self.service.description,
            True,
            self.service.id,
            self.service.name,
            self.service.type,
        )
        self.services_mock.create.return_value = self.service

        # Get the command object to test
        self.cmd = service.CreateService(self.app, None)

    def test_service_create_name(self):
        arglist = [
            '--name', self.service.name,
            self.service.type,
        ]
        verifylist = [
            ('name', self.service.name),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('type', self.service.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name=, type=, enabled=, **kwargs)
        self.services_mock.create.assert_called_with(
            name=self.service.name,
            type=self.service.type,
            description=None,
            enabled=True,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_service_create_description(self):
        arglist = [
            '--description', self.service.description,
            self.service.type,
        ]
        verifylist = [
            ('name', None),
            ('description', self.service.description),
            ('enable', False),
            ('disable', False),
            ('type', self.service.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name=, type=, enabled=, **kwargs)
        self.services_mock.create.assert_called_with(
            name=None,
            type=self.service.type,
            description=self.service.description,
            enabled=True,
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
            ('enable', True),
            ('disable', False),
            ('type', self.service.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name=, type=, enabled=, **kwargs)
        self.services_mock.create.assert_called_with(
            name=None,
            type=self.service.type,
            description=None,
            enabled=True,
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
            ('enable', False),
            ('disable', True),
            ('type', self.service.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name=, type=, enabled=, **kwargs)
        self.services_mock.create.assert_called_with(
            name=None,
            type=self.service.type,
            description=None,
            enabled=False,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestServiceDelete(TestService):

    service = identity_fakes.FakeService.create_one_service()

    def setUp(self):
        super(TestServiceDelete, self).setUp()

        self.services_mock.get.side_effect = identity_exc.NotFound(None)
        self.services_mock.find.return_value = self.service
        self.services_mock.delete.return_value = None

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

        self.services_mock.delete.assert_called_with(
            self.service.id,
        )
        self.assertIsNone(result)


class TestServiceList(TestService):

    service = identity_fakes.FakeService.create_one_service()

    def setUp(self):
        super(TestServiceList, self).setUp()

        self.services_mock.list.return_value = [self.service]

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

        self.services_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Type')
        self.assertEqual(collist, columns)
        datalist = ((
            self.service.id,
            self.service.name,
            self.service.type,
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.services_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Type', 'Description', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = ((
            self.service.id,
            self.service.name,
            self.service.type,
            self.service.description,
            True,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestServiceSet(TestService):

    service = identity_fakes.FakeService.create_one_service()

    def setUp(self):
        super(TestServiceSet, self).setUp()

        self.services_mock.get.side_effect = identity_exc.NotFound(None)
        self.services_mock.find.return_value = self.service
        self.services_mock.update.return_value = self.service

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
            ('enable', False),
            ('disable', False),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_service_set_type(self):
        arglist = [
            '--type', self.service.type,
            self.service.name,
        ]
        verifylist = [
            ('type', self.service.type),
            ('name', None),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'type': self.service.type,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            self.service.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_service_set_name(self):
        arglist = [
            '--name', self.service.name,
            self.service.name,
        ]
        verifylist = [
            ('type', None),
            ('name', self.service.name),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.service.name,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            self.service.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_service_set_description(self):
        arglist = [
            '--description', self.service.description,
            self.service.name,
        ]
        verifylist = [
            ('type', None),
            ('name', None),
            ('description', self.service.description),
            ('enable', False),
            ('disable', False),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.service.description,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            self.service.id,
            **kwargs
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
            ('enable', True),
            ('disable', False),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            self.service.id,
            **kwargs
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
            ('enable', False),
            ('disable', True),
            ('service', self.service.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        # ServiceManager.update(service, name=, type=, enabled=, **kwargs)
        self.services_mock.update.assert_called_with(
            self.service.id,
            **kwargs
        )
        self.assertIsNone(result)


class TestServiceShow(TestService):

    service = identity_fakes.FakeService.create_one_service()

    def setUp(self):
        super(TestServiceShow, self).setUp()

        self.services_mock.get.side_effect = identity_exc.NotFound(None)
        self.services_mock.find.return_value = self.service

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

        # ServiceManager.get(id)
        self.services_mock.find.assert_called_with(
            name=self.service.name
        )

        collist = ('description', 'enabled', 'id', 'name', 'type')
        self.assertEqual(collist, columns)
        datalist = (
            self.service.description,
            True,
            self.service.id,
            self.service.name,
            self.service.type,
        )
        self.assertEqual(datalist, data)

    def test_service_show_nounique(self):
        self.services_mock.find.side_effect = identity_exc.NoUniqueMatch(None)
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
                "Multiple service matches found for 'nounique_service',"
                " use an ID to be more specific.", str(e))
