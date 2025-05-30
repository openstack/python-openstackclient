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

from openstack.identity.v3 import domain as _domain
from openstack.test import fakes as sdk_fakes
from openstackclient.identity.v3 import domain
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestDomainCreate(identity_fakes.TestIdentityv3):
    columns = (
        'id',
        'name',
        'enabled',
        'description',
        'options',
    )

    def setUp(self):
        super().setUp()

        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.identity_sdk_client.create_domain.return_value = self.domain
        self.datalist = (
            self.domain.id,
            self.domain.name,
            self.domain.is_enabled,
            self.domain.description,
            self.domain.options,
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
            'options': {},
            'is_enabled': True,
        }
        self.identity_sdk_client.create_domain.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_domain_create_description(self):
        arglist = [
            '--description',
            'new desc',
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
            'options': {},
            'is_enabled': True,
        }
        self.identity_sdk_client.create_domain.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_domain_create_enable(self):
        arglist = [
            '--enable',
            self.domain.name,
        ]
        verifylist = [
            ('is_enabled', True),
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
            'options': {},
            'is_enabled': True,
        }
        self.identity_sdk_client.create_domain.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_domain_create_disable(self):
        arglist = [
            '--disable',
            self.domain.name,
        ]
        verifylist = [
            ('is_enabled', False),
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
            'options': {},
            'is_enabled': False,
        }
        self.identity_sdk_client.create_domain.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_domain_create_with_immutable(self):
        arglist = [
            '--immutable',
            self.domain.name,
        ]
        verifylist = [
            ('immutable', True),
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
            'options': {'immutable': True},
            'is_enabled': True,
        }
        self.identity_sdk_client.create_domain.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_domain_create_with_no_immutable(self):
        arglist = [
            '--no-immutable',
            self.domain.name,
        ]
        verifylist = [
            ('immutable', False),
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
            'options': {'immutable': False},
            'is_enabled': True,
        }
        self.identity_sdk_client.create_domain.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestDomainDelete(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.delete_domain.return_value = None

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

        self.identity_sdk_client.delete_domain.assert_called_with(
            self.domain.id,
        )
        self.assertIsNone(result)


class TestDomainList(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(
        resource_type=_domain.Domain, is_enabled=True
    )
    columns = (
        'ID',
        'Name',
        'Enabled',
        'Description',
    )

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.domains.return_value = [self.domain]
        self.datalist = (
            (
                self.domain.id,
                self.domain.name,
                self.domain.is_enabled,
                self.domain.description,
            ),
        )

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
        self.identity_sdk_client.domains.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_domain_list_with_option_name(self):
        arglist = ['--name', self.domain.name]
        verifylist = [('name', self.domain.name)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'name': self.domain.name}
        self.identity_sdk_client.domains.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_domain_list_with_option_enabled(self):
        arglist = ['--enabled']
        verifylist = [('is_enabled', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'is_enabled': True}
        self.identity_sdk_client.domains.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestDomainSet(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_domain.return_value = self.domain

        self.identity_sdk_client.update_domain.return_value = self.domain

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
        self.identity_sdk_client.update_domain.assert_called_with(
            self.domain.id, **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_name(self):
        arglist = [
            '--name',
            'qwerty',
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
        self.identity_sdk_client.update_domain.assert_called_with(
            self.domain.id, **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_description(self):
        arglist = [
            '--description',
            'new desc',
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
        self.identity_sdk_client.update_domain.assert_called_with(
            self.domain.id, **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_enable(self):
        arglist = [
            '--enable',
            self.domain.id,
        ]
        verifylist = [
            ('is_enabled', True),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': True,
        }
        self.identity_sdk_client.update_domain.assert_called_with(
            self.domain.id, **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_disable(self):
        arglist = [
            '--disable',
            self.domain.id,
        ]
        verifylist = [
            ('is_enabled', False),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': False,
        }
        self.identity_sdk_client.update_domain.assert_called_with(
            self.domain.id, **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_immutable_option(self):
        arglist = [
            '--immutable',
            self.domain.id,
        ]
        verifylist = [
            ('immutable', True),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'options': {'immutable': True},
        }
        self.identity_sdk_client.update_domain.assert_called_with(
            self.domain.id, **kwargs
        )
        self.assertIsNone(result)

    def test_domain_set_no_immutable_option(self):
        arglist = [
            '--no-immutable',
            self.domain.id,
        ]
        verifylist = [
            ('immutable', False),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'options': {'immutable': False},
        }
        self.identity_sdk_client.update_domain.assert_called_with(
            self.domain.id, **kwargs
        )
        self.assertIsNone(result)


class TestDomainShow(identity_fakes.TestIdentityv3):
    columns = (
        'id',
        'name',
        'enabled',
        'description',
        'options',
    )

    def setUp(self):
        super().setUp()

        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.datalist = (
            self.domain.id,
            self.domain.name,
            self.domain.is_enabled,
            self.domain.description,
            self.domain.options,
        )

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
        self.identity_client.tokens.get_token_data.return_value = {
            'token': {'project': {'domain': {'id': 'd1', 'name': 'd1'}}}
        }

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_domain.assert_called_with(
            self.domain.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)
