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

from openstackclient.identity.v2_0 import service
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes


class TestService(identity_fakes.TestIdentityv2):
    fake_service = identity_fakes.FakeService.create_one_service()

    def setUp(self):
        super().setUp()

        # Get a shortcut to the ServiceManager Mock
        self.services_mock = self.identity_client.services
        self.services_mock.reset_mock()


class TestServiceCreate(TestService):
    fake_service_c = identity_fakes.FakeService.create_one_service()
    columns = (
        'description',
        'id',
        'name',
        'type',
    )
    datalist = (
        fake_service_c.description,
        fake_service_c.id,
        fake_service_c.name,
        fake_service_c.type,
    )

    def setUp(self):
        super().setUp()

        self.services_mock.create.return_value = self.fake_service_c

        # Get the command object to test
        self.cmd = service.CreateService(self.app, None)

    def test_service_create(self):
        arglist = [
            self.fake_service_c.type,
        ]
        verifylist = [
            ('type', self.fake_service_c.type),
            ('name', None),
            ('description', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name, service_type, description)
        self.services_mock.create.assert_called_with(
            None,
            self.fake_service_c.type,
            None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_service_create_with_name_option(self):
        arglist = [
            '--name',
            self.fake_service_c.name,
            self.fake_service_c.type,
        ]
        verifylist = [
            ('type', self.fake_service_c.type),
            ('name', self.fake_service_c.name),
            ('description', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name, service_type, description)
        self.services_mock.create.assert_called_with(
            self.fake_service_c.name,
            self.fake_service_c.type,
            None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_service_create_description(self):
        arglist = [
            '--name',
            self.fake_service_c.name,
            '--description',
            self.fake_service_c.description,
            self.fake_service_c.type,
        ]
        verifylist = [
            ('type', self.fake_service_c.type),
            ('name', self.fake_service_c.name),
            ('description', self.fake_service_c.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.create(name, service_type, description)
        self.services_mock.create.assert_called_with(
            self.fake_service_c.name,
            self.fake_service_c.type,
            self.fake_service_c.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestServiceDelete(TestService):
    def setUp(self):
        super().setUp()

        self.services_mock.get.side_effect = identity_exc.NotFound(None)
        self.services_mock.find.return_value = self.fake_service
        self.services_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = service.DeleteService(self.app, None)

    def test_service_delete_no_options(self):
        arglist = [
            self.fake_service.name,
        ]
        verifylist = [
            ('services', [self.fake_service.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.services_mock.delete.assert_called_with(
            self.fake_service.id,
        )
        self.assertIsNone(result)


class TestServiceList(TestService):
    def setUp(self):
        super().setUp()

        self.services_mock.list.return_value = [self.fake_service]

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
        datalist = (
            (
                self.fake_service.id,
                self.fake_service.name,
                self.fake_service.type,
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

        self.services_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Type', 'Description')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.fake_service.id,
                self.fake_service.name,
                self.fake_service.type,
                self.fake_service.description,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestServiceShow(TestService):
    fake_service_s = identity_fakes.FakeService.create_one_service()

    def setUp(self):
        super().setUp()

        self.services_mock.get.side_effect = identity_exc.NotFound(None)
        self.services_mock.find.return_value = self.fake_service_s

        # Get the command object to test
        self.cmd = service.ShowService(self.app, None)

    def test_service_show(self):
        arglist = [
            self.fake_service_s.name,
        ]
        verifylist = [
            ('service', self.fake_service_s.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServiceManager.find(id)
        self.services_mock.find.assert_called_with(
            name=self.fake_service_s.name,
        )

        collist = ('description', 'id', 'name', 'type')
        self.assertEqual(collist, columns)
        datalist = (
            self.fake_service_s.description,
            self.fake_service_s.id,
            self.fake_service_s.name,
            self.fake_service_s.type,
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
                " use an ID to be more specific.",
                str(e),
            )
