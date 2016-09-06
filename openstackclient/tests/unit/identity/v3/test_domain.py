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

from openstackclient.identity.v3 import domain
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestDomain(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestDomain, self).setUp()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains
        self.domains_mock.reset_mock()


class TestDomainCreate(TestDomain):

    columns = (
        'description',
        'enabled',
        'id',
        'name',
    )

    def setUp(self):
        super(TestDomainCreate, self).setUp()

        self.domain = identity_fakes.FakeDomain.create_one_domain()
        self.domains_mock.create.return_value = self.domain
        self.datalist = (
            self.domain.description,
            True,
            self.domain.id,
            self.domain.name,
        )

        # Get the command object to test
        self.cmd = domain.CreateDomain(self.app, None)

    def test_domain_create_no_options(self):
        arglist = [
            self.domain.name,
        ]
        verifylist = [
            ('name', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.domain.name,
            'description': None,
            'enabled': True,
        }
        self.domains_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_domain_create_description(self):
        arglist = [
            '--description', 'new desc',
            self.domain.name,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('name', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.domain.name,
            'description': 'new desc',
            'enabled': True,
        }
        self.domains_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_domain_create_enable(self):
        arglist = [
            '--enable',
            self.domain.name,
        ]
        verifylist = [
            ('enable', True),
            ('name', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.domain.name,
            'description': None,
            'enabled': True,
        }
        self.domains_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_domain_create_disable(self):
        arglist = [
            '--disable',
            self.domain.name,
        ]
        verifylist = [
            ('disable', True),
            ('name', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.domain.name,
            'description': None,
            'enabled': False,
        }
        self.domains_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestDomainDelete(TestDomain):

    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super(TestDomainDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.domains_mock.get.return_value = self.domain
        self.domains_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = domain.DeleteDomain(self.app, None)

    def test_domain_delete(self):
        arglist = [
            self.domain.id,
        ]
        verifylist = [
            ('domain', [self.domain.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.domains_mock.delete.assert_called_with(
            self.domain.id,
        )
        self.assertIsNone(result)


class TestDomainList(TestDomain):

    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super(TestDomainList, self).setUp()

        self.domains_mock.list.return_value = [self.domain]

        # Get the command object to test
        self.cmd = domain.ListDomain(self.app, None)

    def test_domain_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.domains_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Enabled', 'Description')
        self.assertEqual(collist, columns)
        datalist = ((
            self.domain.id,
            self.domain.name,
            True,
            self.domain.description,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestDomainSet(TestDomain):

    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super(TestDomainSet, self).setUp()

        self.domains_mock.get.return_value = self.domain

        self.domains_mock.update.return_value = self.domain

        # Get the command object to test
        self.cmd = domain.SetDomain(self.app, None)

    def test_domain_set_no_options(self):
        arglist = [
            self.domain.name,
        ]
        verifylist = [
            ('domain', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {}
        self.domains_mock.update.assert_called_with(
            self.domain.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_name(self):
        arglist = [
            '--name', 'qwerty',
            self.domain.id,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'qwerty',
        }
        self.domains_mock.update.assert_called_with(
            self.domain.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_description(self):
        arglist = [
            '--description', 'new desc',
            self.domain.id,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'new desc',
        }
        self.domains_mock.update.assert_called_with(
            self.domain.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_enable(self):
        arglist = [
            '--enable',
            self.domain.id,
        ]
        verifylist = [
            ('enable', True),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        self.domains_mock.update.assert_called_with(
            self.domain.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_disable(self):
        arglist = [
            '--disable',
            self.domain.id,
        ]
        verifylist = [
            ('disable', True),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        self.domains_mock.update.assert_called_with(
            self.domain.id,
            **kwargs
        )
        self.assertIsNone(result)


class TestDomainShow(TestDomain):

    def setUp(self):
        super(TestDomainShow, self).setUp()

        self.domain = identity_fakes.FakeDomain.create_one_domain()
        self.domains_mock.get.return_value = self.domain
        # Get the command object to test
        self.cmd = domain.ShowDomain(self.app, None)

    def test_domain_show(self):
        arglist = [
            self.domain.id,
        ]
        verifylist = [
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.identity.tokens.get_token_data.return_value = \
            {'token':
             {'project':
              {'domain':
               {'id': 'd1',
                'name': 'd1'
                }
               }
              }
             }

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.domains_mock.get.assert_called_with(
            self.domain.id,
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            self.domain.description,
            True,
            self.domain.id,
            self.domain.name,
        )
        self.assertEqual(datalist, data)
