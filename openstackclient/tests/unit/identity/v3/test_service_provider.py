#   Copyright 2014 CERN.
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


from openstack.identity.v3 import service_provider as _service_provider
from openstack.test import fakes as sdk_fakes

from openstackclient.identity.v3 import service_provider
from openstackclient.tests.unit.identity.v3 import fakes as service_fakes


class TestServiceProviderCreate(service_fakes.TestFederatedIdentity):
    columns = (
        'id',
        'enabled',
        'description',
        'auth_url',
        'sp_url',
        'relay_state_prefix',
    )

    def setUp(self):
        super().setUp()

        self.service_provider = sdk_fakes.generate_fake_resource(
            _service_provider.ServiceProvider
        )
        self.identity_sdk_client.create_service_provider.return_value = (
            self.service_provider
        )
        self.data = (
            self.service_provider.id,
            self.service_provider.is_enabled,
            self.service_provider.description,
            self.service_provider.auth_url,
            self.service_provider.sp_url,
            self.service_provider.relay_state_prefix,
        )
        self.cmd = service_provider.CreateServiceProvider(self.app, None)

    def test_create_service_provider_required_options_only(self):
        arglist = [
            '--auth-url',
            self.service_provider.auth_url,
            '--service-provider-url',
            self.service_provider.sp_url,
            self.service_provider.id,
        ]
        verifylist = [
            ('auth_url', self.service_provider.auth_url),
            ('service_provider_url', self.service_provider.sp_url),
            ('service_provider_id', self.service_provider.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': True,
            'auth_url': self.service_provider.auth_url,
            'sp_url': self.service_provider.sp_url,
        }

        self.identity_sdk_client.create_service_provider.assert_called_with(
            id=self.service_provider.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_service_provider_description(self):
        arglist = [
            '--description',
            self.service_provider.description,
            '--auth-url',
            self.service_provider.auth_url,
            '--service-provider-url',
            self.service_provider.sp_url,
            self.service_provider.id,
        ]
        verifylist = [
            ('description', self.service_provider.description),
            ('auth_url', self.service_provider.auth_url),
            ('service_provider_url', self.service_provider.sp_url),
            ('service_provider_id', self.service_provider.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.service_provider.description,
            'auth_url': self.service_provider.auth_url,
            'sp_url': self.service_provider.sp_url,
            'is_enabled': self.service_provider.is_enabled,
        }

        self.identity_sdk_client.create_service_provider.assert_called_with(
            id=self.service_provider.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_service_provider_disabled(self):
        arglist = [
            '--auth-url',
            self.service_provider.auth_url,
            '--service-provider-url',
            self.service_provider.sp_url,
            '--disable',
            self.service_provider.id,
        ]
        verifylist = [
            ('auth_url', self.service_provider.auth_url),
            ('service_provider_url', self.service_provider.sp_url),
            ('service_provider_id', self.service_provider.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'auth_url': self.service_provider.auth_url,
            'sp_url': self.service_provider.sp_url,
            'is_enabled': False,
        }

        self.identity_sdk_client.create_service_provider.assert_called_with(
            id=self.service_provider.id, **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestServiceProviderDelete(service_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.service_provider = sdk_fakes.generate_fake_resource(
            _service_provider.ServiceProvider
        )
        self.identity_sdk_client.delete_service_provider.return_value = None
        self.cmd = service_provider.DeleteServiceProvider(self.app, None)

    def test_delete_service_provider(self):
        arglist = [
            self.service_provider.id,
        ]
        verifylist = [
            ('service_provider', [self.service_provider.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_service_provider.assert_called_with(
            self.service_provider.id,
        )
        self.assertIsNone(result)


class TestServiceProviderList(service_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.service_provider = sdk_fakes.generate_fake_resource(
            _service_provider.ServiceProvider
        )
        self.identity_sdk_client.service_providers.return_value = [
            self.service_provider
        ]

        # Get the command object to test
        self.cmd = service_provider.ListServiceProvider(self.app, None)

    def test_service_provider_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.service_providers.assert_called_with()

        collist = (
            'ID',
            'Enabled',
            'Description',
            'Auth URL',
            'Service Provider URL',
            'Relay State Prefix',
        )
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.service_provider.id,
                True,
                self.service_provider.description,
                self.service_provider.auth_url,
                self.service_provider.sp_url,
                self.service_provider.relay_state_prefix,
            ),
        )
        self.assertEqual(tuple(data), datalist)


class TestServiceProviderSet(service_fakes.TestFederatedIdentity):
    columns = (
        'id',
        'enabled',
        'description',
        'auth_url',
        'sp_url',
        'relay_state_prefix',
    )

    def setUp(self):
        super().setUp()
        self.service_provider = sdk_fakes.generate_fake_resource(
            _service_provider.ServiceProvider
        )
        self.identity_sdk_client.update_service_provider.return_value = (
            self.service_provider
        )
        self.data = (
            self.service_provider.id,
            self.service_provider.is_enabled,
            self.service_provider.description,
            self.service_provider.auth_url,
            self.service_provider.sp_url,
            self.service_provider.relay_state_prefix,
        )
        self.cmd = service_provider.SetServiceProvider(self.app, None)

    def test_service_provider_disable(self):
        """Disable Service Provider

        Set Service Provider's ``enabled`` attribute to False.
        """
        arglist = [
            '--disable',
            self.service_provider.id,
        ]
        verifylist = [
            ('service_provider', self.service_provider.id),
            ('is_enabled', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_service_provider.assert_called_with(
            self.service_provider.id,
            is_enabled=False,
        )
        self.assertEqual(columns, self.columns)
        self.assertEqual(data, self.data)

    def test_service_provider_enable(self):
        """Enable Service Provider.

        Set Service Provider's ``enabled`` attribute to True.
        """
        arglist = [
            '--enable',
            self.service_provider.id,
        ]
        verifylist = [
            ('service_provider', self.service_provider.id),
            ('is_enabled', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_service_provider.assert_called_with(
            self.service_provider.id,
            is_enabled=True,
        )
        self.assertEqual(columns, self.columns)
        self.assertEqual(data, self.data)

    def test_service_provider_no_options(self):
        arglist = [
            self.service_provider.id,
        ]
        verifylist = [
            ('service_provider', self.service_provider.id),
            ('description', None),
            ('is_enabled', None),
            ('auth_url', None),
            ('service_provider_url', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(columns, self.columns)
        self.assertEqual(data, self.data)


class TestServiceProviderShow(service_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.service_provider = sdk_fakes.generate_fake_resource(
            _service_provider.ServiceProvider
        )
        self.identity_sdk_client.find_service_provider.return_value = (
            self.service_provider
        )
        self.data = (
            self.service_provider.id,
            self.service_provider.is_enabled,
            self.service_provider.description,
            self.service_provider.auth_url,
            self.service_provider.sp_url,
            self.service_provider.relay_state_prefix,
        )

        # Get the command object to test
        self.cmd = service_provider.ShowServiceProvider(self.app, None)

    def test_service_provider_show(self):
        arglist = [
            self.service_provider.id,
        ]
        verifylist = [
            ('service_provider', self.service_provider.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_service_provider.assert_called_with(
            self.service_provider.id,
            ignore_missing=False,
        )

        collist = (
            'id',
            'enabled',
            'description',
            'auth_url',
            'sp_url',
            'relay_state_prefix',
        )
        self.assertEqual(collist, columns)
        self.assertEqual(data, self.data)
