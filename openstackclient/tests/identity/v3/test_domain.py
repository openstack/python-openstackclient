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

import copy

from openstackclient.identity.v3 import domain
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes


class TestDomain(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestDomain, self).setUp()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains
        self.domains_mock.reset_mock()


class TestDomainCreate(TestDomain):

    def setUp(self):
        super(TestDomainCreate, self).setUp()

        self.domains_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = domain.CreateDomain(self.app, None)

    def test_domain_create_no_options(self):
        arglist = [
            identity_fakes.domain_name,
        ]
        verifylist = [
            ('name', identity_fakes.domain_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': identity_fakes.domain_name,
            'description': None,
            'enabled': True,
        }
        self.domains_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.domain_description,
            True,
            identity_fakes.domain_id,
            identity_fakes.domain_name,
        )
        self.assertEqual(datalist, data)

    def test_domain_create_description(self):
        arglist = [
            '--description', 'new desc',
            identity_fakes.domain_name,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('name', identity_fakes.domain_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': identity_fakes.domain_name,
            'description': 'new desc',
            'enabled': True,
        }
        self.domains_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.domain_description,
            True,
            identity_fakes.domain_id,
            identity_fakes.domain_name,
        )
        self.assertEqual(datalist, data)

    def test_domain_create_enable(self):
        arglist = [
            '--enable',
            identity_fakes.domain_name,
        ]
        verifylist = [
            ('enable', True),
            ('name', identity_fakes.domain_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': identity_fakes.domain_name,
            'description': None,
            'enabled': True,
        }
        self.domains_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.domain_description,
            True,
            identity_fakes.domain_id,
            identity_fakes.domain_name,
        )
        self.assertEqual(datalist, data)

    def test_domain_create_disable(self):
        arglist = [
            '--disable',
            identity_fakes.domain_name,
        ]
        verifylist = [
            ('disable', True),
            ('name', identity_fakes.domain_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': identity_fakes.domain_name,
            'description': None,
            'enabled': False,
        }
        self.domains_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.domain_description,
            True,
            identity_fakes.domain_id,
            identity_fakes.domain_name,
        )
        self.assertEqual(datalist, data)


class TestDomainDelete(TestDomain):

    def setUp(self):
        super(TestDomainDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )
        self.domains_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = domain.DeleteDomain(self.app, None)

    def test_domain_delete(self):
        arglist = [
            identity_fakes.domain_id,
        ]
        verifylist = [
            ('domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        self.domains_mock.delete.assert_called_with(
            identity_fakes.domain_id,
        )


class TestDomainList(TestDomain):

    def setUp(self):
        super(TestDomainList, self).setUp()

        self.domains_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.DOMAIN),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = domain.ListDomain(self.app, None)

    def test_domain_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.domains_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Enabled', 'Description')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.domain_id,
            identity_fakes.domain_name,
            True,
            identity_fakes.domain_description,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestDomainSet(TestDomain):

    def setUp(self):
        super(TestDomainSet, self).setUp()

        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

        self.domains_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = domain.SetDomain(self.app, None)

    def test_domain_set_no_options(self):
        arglist = [
            identity_fakes.domain_name,
        ]
        verifylist = [
            ('domain', identity_fakes.domain_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        self.assertNotCalled(self.domains_mock.update)

    def test_domain_set_name(self):
        arglist = [
            '--name', 'qwerty',
            identity_fakes.domain_id,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'name': 'qwerty',
        }
        self.domains_mock.update.assert_called_with(
            identity_fakes.domain_id,
            **kwargs
        )

    def test_domain_set_description(self):
        arglist = [
            '--description', 'new desc',
            identity_fakes.domain_id,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'description': 'new desc',
        }
        self.domains_mock.update.assert_called_with(
            identity_fakes.domain_id,
            **kwargs
        )

    def test_domain_set_enable(self):
        arglist = [
            '--enable',
            identity_fakes.domain_id,
        ]
        verifylist = [
            ('enable', True),
            ('domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        self.domains_mock.update.assert_called_with(
            identity_fakes.domain_id,
            **kwargs
        )

    def test_domain_set_disable(self):
        arglist = [
            '--disable',
            identity_fakes.domain_id,
        ]
        verifylist = [
            ('disable', True),
            ('domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        self.domains_mock.update.assert_called_with(
            identity_fakes.domain_id,
            **kwargs
        )


class TestDomainShow(TestDomain):

    def setUp(self):
        super(TestDomainShow, self).setUp()

        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = domain.ShowDomain(self.app, None)

    def test_domain_show(self):
        arglist = [
            identity_fakes.domain_id,
        ]
        verifylist = [
            ('domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.domains_mock.get.assert_called_with(
            identity_fakes.domain_id,
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.domain_description,
            True,
            identity_fakes.domain_id,
            identity_fakes.domain_name,
        )
        self.assertEqual(datalist, data)
