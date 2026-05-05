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

from unittest import mock

from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import identity_provider as _identity_provider
from openstack.test import fakes as sdk_fakes
from openstackclient.identity.v3 import identity_provider
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as test_utils


class TestIdentityProviderCreate(identity_fakes.TestFederatedIdentity):
    columns = (
        'authorization_ttl',
        'description',
        'domain_id',
        'enabled',
        'id',
        'remote_ids',
    )

    def setUp(self):
        super().setUp()

        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.idp = sdk_fakes.generate_fake_resource(
            _identity_provider.IdentityProvider,
            domain_id=self.domain.id,
            remote_ids=['entity1', 'entity2'],
        )

        self.identity_sdk_client.create_identity_provider.return_value = (
            self.idp
        )
        self.identity_sdk_client.find_domain.return_value = self.domain

        self.datalist = (
            self.idp.authorization_ttl,
            self.idp.description,
            self.domain.id,
            self.idp.is_enabled,
            self.idp.id,
            format_columns.ListColumn(self.idp.remote_ids),
        )
        self.cmd = identity_provider.CreateIdentityProvider(self.app, None)

    def test_create_identity_provider_no_options(self):
        arglist = [
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': True,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)

        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_description(self):
        arglist = [
            '--description',
            self.idp.description,
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('description', self.idp.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.idp.description,
            'is_enabled': True,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_remote_id(self):
        arglist = [
            self.idp.id,
            '--remote-id',
            self.idp.remote_ids[0],
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('remote_ids', self.idp.remote_ids[:1]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': self.idp.remote_ids[:1],
            'is_enabled': True,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_remote_ids_multiple(self):
        arglist = [
            '--remote-id',
            self.idp.remote_ids[0],
            '--remote-id',
            self.idp.remote_ids[1],
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('remote_ids', self.idp.remote_ids),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': self.idp.remote_ids,
            'is_enabled': True,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_remote_ids_file(self):
        arglist = [
            '--remote-id-file',
            '/tmp/file_name',
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('remote_id_file', '/tmp/file_name'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = "\n".join(self.idp.remote_ids)
        with mock.patch(
            "openstackclient.identity.v3.identity_provider."
            "utils.read_blob_file_contents",
            mocker,
        ):
            columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': self.idp.remote_ids,
            'is_enabled': True,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_disabled(self):
        idp_disabled = sdk_fakes.generate_fake_resource(
            _identity_provider.IdentityProvider,
            domain_id=self.domain.id,
            remote_ids=['entity1', 'entity2'],
            is_enabled=False,
        )
        self.identity_sdk_client.create_identity_provider.return_value = (
            idp_disabled
        )
        self.cmd = identity_provider.CreateIdentityProvider(self.app, None)

        arglist = [
            '--disable',
            idp_disabled.id,
        ]
        verifylist = [
            ('identity_provider_id', idp_disabled.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': False,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=idp_disabled.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            idp_disabled.authorization_ttl,
            idp_disabled.description,
            self.domain.id,
            False,
            idp_disabled.id,
            format_columns.ListColumn(self.idp.remote_ids),
        )
        self.assertCountEqual(datalist, data)

    def test_create_identity_provider_domain_name(self):
        arglist = [
            '--domain',
            self.domain.name,
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('domain', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain_id': self.domain.id,
            'is_enabled': True,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_domain_id(self):
        arglist = [
            '--domain',
            self.domain.id,
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain_id': self.domain.id,
            'is_enabled': True,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_authttl_positive(self):
        arglist = [
            '--authorization-ttl',
            '60',
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('authorization_ttl', 60),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': True,
            'authorization_ttl': 60,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_authttl_zero(self):
        arglist = [
            '--authorization-ttl',
            '0',
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('authorization_ttl', 0),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': True,
            'authorization_ttl': 0,
        }

        self.identity_sdk_client.create_identity_provider.assert_called_with(
            id=self.idp.id, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_create_identity_provider_authttl_negative(self):
        arglist = [
            '--authorization-ttl',
            '-60',
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider_id', self.idp.id),
            ('authorization_ttl', -60),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_create_identity_provider_authttl_not_int(self):
        arglist = [
            '--authorization-ttl',
            'spam',
            self.idp.id,
        ]
        verifylist = []
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestIdentityProviderDelete(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.idp = sdk_fakes.generate_fake_resource(
            _identity_provider.IdentityProvider
        )

        self.identity_sdk_client.delete_identity_provider.return_value = None
        self.cmd = identity_provider.DeleteIdentityProvider(self.app, None)

    def test_delete_identity_provider(self):
        arglist = [
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider', [self.idp.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_identity_provider.assert_called_with(
            self.idp.id,
        )
        self.assertIsNone(result)


class TestIdentityProviderList(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.idp = sdk_fakes.generate_fake_resource(
            _identity_provider.IdentityProvider,
            domain_id=self.domain.id,
            remote_ids=['entity1', 'entity2'],
        )

        self.identity_sdk_client.identity_providers.return_value = [self.idp]

        # Get the command object to test
        self.cmd = identity_provider.ListIdentityProvider(self.app, None)

    def test_identity_provider_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.identity_providers.assert_called_with()

        collist = ('ID', 'Enabled', 'Domain ID', 'Description')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.idp.id,
                True,
                self.domain.id,
                self.idp.description,
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_identity_provider_list_ID_option(self):
        arglist = ['--id', self.idp.id]
        verifylist = [('id', self.idp.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'id': self.idp.id}
        self.identity_sdk_client.identity_providers.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Enabled', 'Domain ID', 'Description')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.idp.id,
                True,
                self.domain.id,
                self.idp.description,
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_identity_provider_list_enabled_option(self):
        arglist = ['--enabled']
        verifylist = [('enabled', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'is_enabled': True}
        self.identity_sdk_client.identity_providers.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Enabled', 'Domain ID', 'Description')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.idp.id,
                True,
                self.domain.id,
                self.idp.description,
            ),
        )
        self.assertCountEqual(datalist, tuple(data))


class TestIdentityProviderSet(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.idp = sdk_fakes.generate_fake_resource(
            _identity_provider.IdentityProvider,
            domain_id=self.domain.id,
            remote_ids=['entity1', 'entity2'],
        )

        self.cmd = identity_provider.SetIdentityProvider(self.app, None)

    def test_identity_provider_set_description(self):
        """Set Identity Provider's description."""

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            new_description = 'new desc'

            self.updated_idp = sdk_fakes.generate_fake_resource(
                _identity_provider.IdentityProvider,
                id=self.idp.id,
                description=new_description,
                domain_id=self.domain.id,
                remote_ids=self.idp.remote_ids,
            )
            self.identity_sdk_client.update_identity_provider.return_value = (
                self.updated_idp
            )

        prepare(self)
        arglist = ['--description', self.updated_idp.description, self.idp.id]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('description', self.updated_idp.description),
            ('enable', False),
            ('disable', False),
            ('remote_ids', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_identity_provider.assert_called_with(
            self.idp.id,
            description=self.updated_idp.description,
        )

    def test_identity_provider_disable(self):
        """Disable Identity Provider

        Set Identity Provider's ``enabled`` attribute to False.
        """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.updated_idp = sdk_fakes.generate_fake_resource(
                _identity_provider.IdentityProvider,
                id=self.idp.id,
                enabled=False,
                domain_id=self.domain.id,
                remote_ids=self.idp.remote_ids,
            )
            self.identity_sdk_client.update_identity_provider.return_value = (
                self.updated_idp
            )

        prepare(self)
        arglist = [
            '--disable',
            self.idp.id,
            '--remote-id',
            self.idp.remote_ids[0],
            '--remote-id',
            self.idp.remote_ids[1],
        ]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('description', None),
            ('enable', False),
            ('disable', True),
            ('remote_ids', self.idp.remote_ids),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_identity_provider.assert_called_with(
            self.idp.id,
            is_enabled=False,
            remote_ids=self.idp.remote_ids,
        )

    def test_identity_provider_enable(self):
        """Enable Identity Provider.

        Set Identity Provider's ``enabled`` attribute to True.
        """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.updated_idp = sdk_fakes.generate_fake_resource(
                _identity_provider.IdentityProvider,
                id=self.idp.id,
                is_enabled=True,
                domain_id=self.domain.id,
                remote_ids=self.idp.remote_ids,
            )
            self.identity_sdk_client.update_identity_provider.return_value = (
                self.updated_idp
            )

        prepare(self)
        arglist = [
            '--enable',
            self.idp.id,
            '--remote-id',
            self.idp.remote_ids[0],
            '--remote-id',
            self.idp.remote_ids[1],
        ]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('description', None),
            ('enable', True),
            ('disable', False),
            ('remote_ids', self.idp.remote_ids),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_identity_provider.assert_called_with(
            self.idp.id,
            is_enabled=True,
            remote_ids=self.idp.remote_ids,
        )

    def test_identity_provider_replace_remote_ids(self):
        """Enable Identity Provider.

        Set Identity Provider's ``enabled`` attribute to True.
        """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.new_remote_id = 'new_entity'

            self.updated_idp = sdk_fakes.generate_fake_resource(
                _identity_provider.IdentityProvider,
                id=self.idp.id,
                domain_id=self.domain.id,
                remote_ids=[self.new_remote_id],
            )
            self.identity_sdk_client.update_identity_provider.return_value = (
                self.updated_idp
            )

        prepare(self)
        arglist = [
            '--enable',
            self.idp.id,
            '--remote-id',
            self.new_remote_id,
        ]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('description', None),
            ('enable', True),
            ('disable', False),
            ('remote_ids', [self.new_remote_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_identity_provider.assert_called_with(
            self.idp.id,
            is_enabled=True,
            remote_ids=[self.new_remote_id],
        )

    def test_identity_provider_replace_remote_ids_file(self):
        """Enable Identity Provider.

        Set Identity Provider's ``enabled`` attribute to True.
        """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.new_remote_id = 'new_entity'

            self.updated_idp = sdk_fakes.generate_fake_resource(
                _identity_provider.IdentityProvider,
                id=self.idp.id,
                domain_id=self.domain.id,
                remote_ids=[self.new_remote_id],
            )
            self.identity_sdk_client.update_identity_provider.return_value = (
                self.updated_idp
            )

        prepare(self)
        arglist = [
            '--enable',
            self.idp.id,
            '--remote-id-file',
            self.new_remote_id,
        ]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('description', None),
            ('enable', True),
            ('disable', False),
            ('remote_id_file', self.new_remote_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = self.new_remote_id
        with mock.patch(
            "openstackclient.identity.v3.identity_provider."
            "utils.read_blob_file_contents",
            mocker,
        ):
            self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_identity_provider.assert_called_with(
            self.idp.id,
            is_enabled=True,
            remote_ids=[self.new_remote_id],
        )

    def test_identity_provider_no_options(self):
        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.updated_idp = sdk_fakes.generate_fake_resource(
                _identity_provider.IdentityProvider,
                id=self.idp.id,
                domain_id=self.domain.id,
                remote_ids=self.idp.remote_ids,
            )
            self.identity_sdk_client.update_identity_provider.return_value = (
                self.updated_idp
            )

        prepare(self)
        arglist = [
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('enable', False),
            ('disable', False),
            ('remote_ids', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

    def test_identity_provider_set_authttl_positive(self):
        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.updated_idp = sdk_fakes.generate_fake_resource(
                _identity_provider.IdentityProvider,
                id=self.idp.id,
                authorization_ttl=60,
                domain_id=self.domain.id,
                remote_ids=self.idp.remote_ids,
            )
            self.identity_sdk_client.update_identity_provider.return_value = (
                self.updated_idp
            )

        prepare(self)
        arglist = ['--authorization-ttl', '60', self.idp.id]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('enable', False),
            ('disable', False),
            ('remote_ids', None),
            ('authorization_ttl', 60),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_identity_provider.assert_called_with(
            self.idp.id,
            authorization_ttl=60,
        )

    def test_identity_provider_set_authttl_zero(self):
        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.updated_idp = sdk_fakes.generate_fake_resource(
                _identity_provider.IdentityProvider,
                id=self.idp.id,
                authorization_ttl=0,
                domain_id=self.domain.id,
                remote_ids=self.idp.remote_ids,
            )
            self.identity_sdk_client.update_identity_provider.return_value = (
                self.updated_idp
            )

        prepare(self)
        arglist = ['--authorization-ttl', '0', self.idp.id]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('enable', False),
            ('disable', False),
            ('remote_ids', None),
            ('authorization_ttl', 0),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_identity_provider.assert_called_with(
            self.idp.id,
            authorization_ttl=0,
        )

    def test_identity_provider_set_authttl_negative(self):
        arglist = ['--authorization-ttl', '-1', self.idp.id]
        verifylist = [
            ('identity_provider', self.idp.id),
            ('enable', False),
            ('disable', False),
            ('remote_ids', None),
            ('authorization_ttl', -1),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_identity_provider_set_authttl_not_int(self):
        arglist = ['--authorization-ttl', 'spam', self.idp.id]
        verifylist = []
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestIdentityProviderShow(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.idp = sdk_fakes.generate_fake_resource(
            _identity_provider.IdentityProvider,
            remote_ids=['entity1', 'entity2'],
        )

        self.identity_sdk_client.get_identity_provider.return_value = self.idp

        self.cmd = identity_provider.ShowIdentityProvider(self.app, None)

    def test_identity_provider_show(self):
        arglist = [
            self.idp.id,
        ]
        verifylist = [
            ('identity_provider', self.idp.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.get_identity_provider.assert_called_with(
            self.idp.id,
        )

        collist = (
            'authorization_ttl',
            'description',
            'domain_id',
            'enabled',
            'id',
            'remote_ids',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.idp.authorization_ttl,
            self.idp.description,
            self.idp.domain_id,
            True,
            self.idp.id,
            format_columns.ListColumn(self.idp.remote_ids),
        )
        self.assertCountEqual(datalist, data)
