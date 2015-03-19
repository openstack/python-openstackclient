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

import copy

from openstackclient.identity.v3 import service_provider
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as service_fakes


class TestServiceProvider(service_fakes.TestFederatedIdentity):

    def setUp(self):
        super(TestServiceProvider, self).setUp()

        federation_lib = self.app.client_manager.identity.federation
        self.service_providers_mock = federation_lib.service_providers
        self.service_providers_mock.reset_mock()


class TestServiceProviderCreate(TestServiceProvider):

    def setUp(self):
        super(TestServiceProviderCreate, self).setUp()

        copied_sp = copy.deepcopy(service_fakes.SERVICE_PROVIDER)
        resource = fakes.FakeResource(None, copied_sp, loaded=True)
        self.service_providers_mock.create.return_value = resource
        self.cmd = service_provider.CreateServiceProvider(self.app, None)

    def test_create_service_provider_required_options_only(self):
        arglist = [
            '--auth-url', service_fakes.sp_auth_url,
            '--service-provider-url', service_fakes.service_provider_url,
            service_fakes.sp_id,
        ]
        verifylist = [
            ('auth_url', service_fakes.sp_auth_url),
            ('service_provider_url', service_fakes.service_provider_url),
            ('service_provider_id', service_fakes.sp_id),

        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'description': None,
            'auth_url': service_fakes.sp_auth_url,
            'sp_url': service_fakes.service_provider_url
        }

        self.service_providers_mock.create.assert_called_with(
            id=service_fakes.sp_id,
            **kwargs
        )

        collist = ('auth_url', 'description', 'enabled', 'id', 'sp_url')
        self.assertEqual(collist, columns)
        datalist = (
            service_fakes.sp_auth_url,
            service_fakes.sp_description,
            True,
            service_fakes.sp_id,
            service_fakes.service_provider_url
        )
        self.assertEqual(data, datalist)

    def test_create_service_provider_description(self):

        arglist = [
            '--description', service_fakes.sp_description,
            '--auth-url', service_fakes.sp_auth_url,
            '--service-provider-url', service_fakes.service_provider_url,
            service_fakes.sp_id,
        ]
        verifylist = [
            ('description', service_fakes.sp_description),
            ('auth_url', service_fakes.sp_auth_url),
            ('service_provider_url', service_fakes.service_provider_url),
            ('service_provider_id', service_fakes.sp_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': service_fakes.sp_description,
            'auth_url': service_fakes.sp_auth_url,
            'sp_url': service_fakes.service_provider_url,
            'enabled': True,
        }

        self.service_providers_mock.create.assert_called_with(
            id=service_fakes.sp_id,
            **kwargs
        )

        collist = ('auth_url', 'description', 'enabled', 'id', 'sp_url')
        self.assertEqual(columns, collist)
        datalist = (
            service_fakes.sp_auth_url,
            service_fakes.sp_description,
            True,
            service_fakes.sp_id,
            service_fakes.service_provider_url
        )
        self.assertEqual(datalist, data)

    def test_create_service_provider_disabled(self):

        # Prepare FakeResource object
        service_provider = copy.deepcopy(service_fakes.SERVICE_PROVIDER)
        service_provider['enabled'] = False
        service_provider['description'] = None

        resource = fakes.FakeResource(None, service_provider, loaded=True)
        self.service_providers_mock.create.return_value = resource

        arglist = [
            '--auth-url', service_fakes.sp_auth_url,
            '--service-provider-url', service_fakes.service_provider_url,
            '--disable',
            service_fakes.sp_id,
        ]
        verifylist = [
            ('auth_url', service_fakes.sp_auth_url),
            ('service_provider_url', service_fakes.service_provider_url),
            ('service_provider_id', service_fakes.sp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'auth_url': service_fakes.sp_auth_url,
            'sp_url': service_fakes.service_provider_url,
            'enabled': False,
            'description': None,
        }

        self.service_providers_mock.create.assert_called_with(
            id=service_fakes.sp_id,
            **kwargs
        )

        collist = ('auth_url', 'description', 'enabled', 'id', 'sp_url')
        self.assertEqual(collist, collist)
        datalist = (
            service_fakes.sp_auth_url,
            None,
            False,
            service_fakes.sp_id,
            service_fakes.service_provider_url
        )
        self.assertEqual(datalist, data)


class TestServiceProviderDelete(TestServiceProvider):

    def setUp(self):
        super(TestServiceProviderDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.service_providers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(service_fakes.SERVICE_PROVIDER),
            loaded=True,
        )

        self.service_providers_mock.delete.return_value = None
        self.cmd = service_provider.DeleteServiceProvider(self.app, None)

    def test_delete_service_provider(self):
        arglist = [
            service_fakes.sp_id,
        ]
        verifylist = [
            ('service_provider', service_fakes.sp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.service_providers_mock.delete.assert_called_with(
            service_fakes.sp_id,
        )


class TestServiceProviderList(TestServiceProvider):

    def setUp(self):
        super(TestServiceProviderList, self).setUp()

        self.service_providers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(service_fakes.SERVICE_PROVIDER),
            loaded=True,
        )
        self.service_providers_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(service_fakes.SERVICE_PROVIDER),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = service_provider.ListServiceProvider(self.app, None)

    def test_service_provider_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.service_providers_mock.list.assert_called_with()

        collist = ('ID', 'Enabled', 'Description', 'Auth URL')
        self.assertEqual(collist, columns)
        datalist = ((
            service_fakes.sp_id,
            True,
            service_fakes.sp_description,
            service_fakes.sp_auth_url
        ), )
        self.assertEqual(tuple(data), datalist)


class TestServiceProviderShow(TestServiceProvider):

    def setUp(self):
        super(TestServiceProviderShow, self).setUp()

        ret = fakes.FakeResource(
            None,
            copy.deepcopy(service_fakes.SERVICE_PROVIDER),
            loaded=True,
        )
        self.service_providers_mock.get.return_value = ret
        # Get the command object to test
        self.cmd = service_provider.ShowServiceProvider(self.app, None)

    def test_service_provider_show(self):
        arglist = [
            service_fakes.sp_id,
        ]
        verifylist = [
            ('service_provider', service_fakes.sp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.service_providers_mock.get.assert_called_with(
            service_fakes.sp_id,
        )

        collist = ('auth_url', 'description', 'enabled', 'id', 'sp_url')
        self.assertEqual(collist, columns)
        datalist = (
            service_fakes.sp_auth_url,
            service_fakes.sp_description,
            True,
            service_fakes.sp_id,
            service_fakes.service_provider_url
        )
        self.assertEqual(data, datalist)


class TestServiceProviderSet(TestServiceProvider):

    def setUp(self):
        super(TestServiceProviderSet, self).setUp()
        self.cmd = service_provider.SetServiceProvider(self.app, None)

    def test_service_provider_disable(self):
        """Disable Service Provider

        Set Service Provider's ``enabled`` attribute to False.
        """
        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            updated_sp = copy.deepcopy(service_fakes.SERVICE_PROVIDER)
            updated_sp['enabled'] = False
            resources = fakes.FakeResource(
                None,
                updated_sp,
                loaded=True
            )
            self.service_providers_mock.update.return_value = resources

        prepare(self)
        arglist = [
            '--disable', service_fakes.sp_id,
        ]
        verifylist = [
            ('service_provider', service_fakes.sp_id),
            ('enable', False),
            ('disable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.service_providers_mock.update.assert_called_with(
            service_fakes.sp_id,
            enabled=False,
            description=None,
            auth_url=None,
            sp_url=None
        )

        collist = ('auth_url', 'description', 'enabled', 'id', 'sp_url')
        self.assertEqual(collist, columns)
        datalist = (
            service_fakes.sp_auth_url,
            service_fakes.sp_description,
            False,
            service_fakes.sp_id,
            service_fakes.service_provider_url
        )
        self.assertEqual(datalist, data)

    def test_service_provider_enable(self):
        """Enable Service Provider.

        Set Service Provider's ``enabled`` attribute to True.
        """
        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            resources = fakes.FakeResource(
                None,
                copy.deepcopy(service_fakes.SERVICE_PROVIDER),
                loaded=True
            )
            self.service_providers_mock.update.return_value = resources

        prepare(self)
        arglist = [
            '--enable', service_fakes.sp_id,
        ]
        verifylist = [
            ('service_provider', service_fakes.sp_id),
            ('enable', True),
            ('disable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.service_providers_mock.update.assert_called_with(
            service_fakes.sp_id, enabled=True, description=None,
            auth_url=None, sp_url=None)
        collist = ('auth_url', 'description', 'enabled', 'id', 'sp_url')
        self.assertEqual(collist, columns)
        datalist = (
            service_fakes.sp_auth_url,
            service_fakes.sp_description,
            True,
            service_fakes.sp_id,
            service_fakes.service_provider_url
        )
        self.assertEqual(data, datalist)

    def test_service_provider_no_options(self):
        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            resources = fakes.FakeResource(
                None,
                copy.deepcopy(service_fakes.SERVICE_PROVIDER),
                loaded=True
            )
            self.service_providers_mock.get.return_value = resources

            resources = fakes.FakeResource(
                None,
                copy.deepcopy(service_fakes.SERVICE_PROVIDER),
                loaded=True,
            )
            self.service_providers_mock.update.return_value = resources

        prepare(self)
        arglist = [
            service_fakes.sp_id,
        ]
        verifylist = [
            ('service_provider', service_fakes.sp_id),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('auth_url', None),
            ('service_provider_url', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # expect take_action() to return (None, None) as none of --disabled,
        # --enabled, --description, --service-provider-url, --auth_url option
        # was set.
        self.assertEqual(columns, None)
        self.assertEqual(data, None)
