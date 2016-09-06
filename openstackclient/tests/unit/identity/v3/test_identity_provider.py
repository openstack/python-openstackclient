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
import mock

from openstackclient.identity.v3 import identity_provider
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestIdentityProvider(identity_fakes.TestFederatedIdentity):

    def setUp(self):
        super(TestIdentityProvider, self).setUp()

        federation_lib = self.app.client_manager.identity.federation
        self.identity_providers_mock = federation_lib.identity_providers
        self.identity_providers_mock.reset_mock()


class TestIdentityProviderCreate(TestIdentityProvider):

    columns = (
        'description',
        'enabled',
        'id',
        'remote_ids',
    )
    datalist = (
        identity_fakes.idp_description,
        True,
        identity_fakes.idp_id,
        identity_fakes.formatted_idp_remote_ids,
    )

    def setUp(self):
        super(TestIdentityProviderCreate, self).setUp()

        copied_idp = copy.deepcopy(identity_fakes.IDENTITY_PROVIDER)
        resource = fakes.FakeResource(None, copied_idp, loaded=True)
        self.identity_providers_mock.create.return_value = resource
        self.cmd = identity_provider.CreateIdentityProvider(self.app, None)

    def test_create_identity_provider_no_options(self):
        arglist = [
            identity_fakes.idp_id,
        ]
        verifylist = [
            ('identity_provider_id', identity_fakes.idp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': None,
            'enabled': True,
            'description': None,
        }

        self.identity_providers_mock.create.assert_called_with(
            id=identity_fakes.idp_id,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_create_identity_provider_description(self):
        arglist = [
            '--description', identity_fakes.idp_description,
            identity_fakes.idp_id,
        ]
        verifylist = [
            ('identity_provider_id', identity_fakes.idp_id),
            ('description', identity_fakes.idp_description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': None,
            'description': identity_fakes.idp_description,
            'enabled': True,
        }

        self.identity_providers_mock.create.assert_called_with(
            id=identity_fakes.idp_id,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_create_identity_provider_remote_id(self):
        arglist = [
            identity_fakes.idp_id,
            '--remote-id', identity_fakes.idp_remote_ids[0]
        ]
        verifylist = [
            ('identity_provider_id', identity_fakes.idp_id),
            ('remote_id', identity_fakes.idp_remote_ids[:1]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': identity_fakes.idp_remote_ids[:1],
            'description': None,
            'enabled': True,
        }

        self.identity_providers_mock.create.assert_called_with(
            id=identity_fakes.idp_id,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_create_identity_provider_remote_ids_multiple(self):
        arglist = [
            '--remote-id', identity_fakes.idp_remote_ids[0],
            '--remote-id', identity_fakes.idp_remote_ids[1],
            identity_fakes.idp_id
        ]
        verifylist = [
            ('identity_provider_id', identity_fakes.idp_id),
            ('remote_id', identity_fakes.idp_remote_ids),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': identity_fakes.idp_remote_ids,
            'description': None,
            'enabled': True,
        }

        self.identity_providers_mock.create.assert_called_with(
            id=identity_fakes.idp_id,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_create_identity_provider_remote_ids_file(self):
        arglist = [
            '--remote-id-file', '/tmp/file_name',
            identity_fakes.idp_id,
        ]
        verifylist = [
            ('identity_provider_id', identity_fakes.idp_id),
            ('remote_id_file', '/tmp/file_name'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = "\n".join(identity_fakes.idp_remote_ids)
        with mock.patch("openstackclient.identity.v3.identity_provider."
                        "utils.read_blob_file_contents", mocker):
            columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': identity_fakes.idp_remote_ids,
            'description': None,
            'enabled': True,
        }

        self.identity_providers_mock.create.assert_called_with(
            id=identity_fakes.idp_id,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_create_identity_provider_disabled(self):

        # Prepare FakeResource object
        IDENTITY_PROVIDER = copy.deepcopy(identity_fakes.IDENTITY_PROVIDER)
        IDENTITY_PROVIDER['enabled'] = False
        IDENTITY_PROVIDER['description'] = None

        resource = fakes.FakeResource(None, IDENTITY_PROVIDER, loaded=True)
        self.identity_providers_mock.create.return_value = resource

        arglist = [
            '--disable',
            identity_fakes.idp_id,
        ]
        verifylist = [
            ('identity_provider_id', identity_fakes.idp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remote_ids': None,
            'enabled': False,
            'description': None,
        }

        self.identity_providers_mock.create.assert_called_with(
            id=identity_fakes.idp_id,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            False,
            identity_fakes.idp_id,
            identity_fakes.formatted_idp_remote_ids
        )
        self.assertEqual(datalist, data)


class TestIdentityProviderDelete(TestIdentityProvider):

    def setUp(self):
        super(TestIdentityProviderDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.identity_providers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.IDENTITY_PROVIDER),
            loaded=True,
        )

        self.identity_providers_mock.delete.return_value = None
        self.cmd = identity_provider.DeleteIdentityProvider(self.app, None)

    def test_delete_identity_provider(self):
        arglist = [
            identity_fakes.idp_id,
        ]
        verifylist = [
            ('identity_provider', [identity_fakes.idp_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_providers_mock.delete.assert_called_with(
            identity_fakes.idp_id,
        )
        self.assertIsNone(result)


class TestIdentityProviderList(TestIdentityProvider):

    def setUp(self):
        super(TestIdentityProviderList, self).setUp()

        self.identity_providers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.IDENTITY_PROVIDER),
            loaded=True,
        )
        self.identity_providers_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.IDENTITY_PROVIDER),
                loaded=True,
            ),
        ]

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

        self.identity_providers_mock.list.assert_called_with()

        collist = ('ID', 'Enabled', 'Description')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.idp_id,
            True,
            identity_fakes.idp_description,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestIdentityProviderSet(TestIdentityProvider):

    columns = (
        'description',
        'enabled',
        'id',
        'remote_ids',
    )
    datalist = (
        identity_fakes.idp_description,
        True,
        identity_fakes.idp_id,
        identity_fakes.idp_remote_ids,
    )

    def setUp(self):
        super(TestIdentityProviderSet, self).setUp()
        self.cmd = identity_provider.SetIdentityProvider(self.app, None)

    def test_identity_provider_set_description(self):
        """Set Identity Provider's description. """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            updated_idp = copy.deepcopy(identity_fakes.IDENTITY_PROVIDER)
            updated_idp['enabled'] = False
            resources = fakes.FakeResource(
                None,
                updated_idp,
                loaded=True
            )
            self.identity_providers_mock.update.return_value = resources

        prepare(self)
        new_description = 'new desc'
        arglist = [
            '--description', new_description,
            identity_fakes.idp_id
        ]
        verifylist = [
            ('identity_provider', identity_fakes.idp_id),
            ('description', new_description),
            ('enable', False),
            ('disable', False),
            ('remote_id', None)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.identity_providers_mock.update.assert_called_with(
            identity_fakes.idp_id,
            description=new_description,
        )

    def test_identity_provider_disable(self):
        """Disable Identity Provider

        Set Identity Provider's ``enabled`` attribute to False.
        """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            updated_idp = copy.deepcopy(identity_fakes.IDENTITY_PROVIDER)
            updated_idp['enabled'] = False
            resources = fakes.FakeResource(
                None,
                updated_idp,
                loaded=True
            )
            self.identity_providers_mock.update.return_value = resources

        prepare(self)
        arglist = [
            '--disable', identity_fakes.idp_id,
            '--remote-id', identity_fakes.idp_remote_ids[0],
            '--remote-id', identity_fakes.idp_remote_ids[1]
        ]
        verifylist = [
            ('identity_provider', identity_fakes.idp_id),
            ('description', None),
            ('enable', False),
            ('disable', True),
            ('remote_id', identity_fakes.idp_remote_ids)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.identity_providers_mock.update.assert_called_with(
            identity_fakes.idp_id,
            enabled=False,
            remote_ids=identity_fakes.idp_remote_ids
        )

    def test_identity_provider_enable(self):
        """Enable Identity Provider.

        Set Identity Provider's ``enabled`` attribute to True.
        """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            resources = fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.IDENTITY_PROVIDER),
                loaded=True
            )
            self.identity_providers_mock.update.return_value = resources

        prepare(self)
        arglist = [
            '--enable', identity_fakes.idp_id,
            '--remote-id', identity_fakes.idp_remote_ids[0],
            '--remote-id', identity_fakes.idp_remote_ids[1]
        ]
        verifylist = [
            ('identity_provider', identity_fakes.idp_id),
            ('description', None),
            ('enable', True),
            ('disable', False),
            ('remote_id', identity_fakes.idp_remote_ids)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.identity_providers_mock.update.assert_called_with(
            identity_fakes.idp_id, enabled=True,
            remote_ids=identity_fakes.idp_remote_ids)

    def test_identity_provider_replace_remote_ids(self):
        """Enable Identity Provider.

        Set Identity Provider's ``enabled`` attribute to True.
        """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.new_remote_id = 'new_entity'

            updated_idp = copy.deepcopy(identity_fakes.IDENTITY_PROVIDER)
            updated_idp['remote_ids'] = [self.new_remote_id]
            resources = fakes.FakeResource(
                None,
                updated_idp,
                loaded=True
            )
            self.identity_providers_mock.update.return_value = resources

        prepare(self)
        arglist = [
            '--enable', identity_fakes.idp_id,
            '--remote-id', self.new_remote_id
        ]
        verifylist = [
            ('identity_provider', identity_fakes.idp_id),
            ('description', None),
            ('enable', True),
            ('disable', False),
            ('remote_id', [self.new_remote_id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.identity_providers_mock.update.assert_called_with(
            identity_fakes.idp_id, enabled=True,
            remote_ids=[self.new_remote_id])

    def test_identity_provider_replace_remote_ids_file(self):
        """Enable Identity Provider.

        Set Identity Provider's ``enabled`` attribute to True.
        """

        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            self.new_remote_id = 'new_entity'

            updated_idp = copy.deepcopy(identity_fakes.IDENTITY_PROVIDER)
            updated_idp['remote_ids'] = [self.new_remote_id]
            resources = fakes.FakeResource(
                None,
                updated_idp,
                loaded=True
            )
            self.identity_providers_mock.update.return_value = resources

        prepare(self)
        arglist = [
            '--enable', identity_fakes.idp_id,
            '--remote-id-file', self.new_remote_id,
        ]
        verifylist = [
            ('identity_provider', identity_fakes.idp_id),
            ('description', None),
            ('enable', True),
            ('disable', False),
            ('remote_id_file', self.new_remote_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = self.new_remote_id
        with mock.patch("openstackclient.identity.v3.identity_provider."
                        "utils.read_blob_file_contents", mocker):
            self.cmd.take_action(parsed_args)
        self.identity_providers_mock.update.assert_called_with(
            identity_fakes.idp_id, enabled=True,
            remote_ids=[self.new_remote_id])

    def test_identity_provider_no_options(self):
        def prepare(self):
            """Prepare fake return objects before the test is executed"""
            resources = fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.IDENTITY_PROVIDER),
                loaded=True
            )
            self.identity_providers_mock.get.return_value = resources

            resources = fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.IDENTITY_PROVIDER),
                loaded=True,
            )
            self.identity_providers_mock.update.return_value = resources

        prepare(self)
        arglist = [
            identity_fakes.idp_id,
        ]
        verifylist = [
            ('identity_provider', identity_fakes.idp_id),
            ('enable', False),
            ('disable', False),
            ('remote_id', None)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)


class TestIdentityProviderShow(TestIdentityProvider):

    def setUp(self):
        super(TestIdentityProviderShow, self).setUp()

        ret = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.IDENTITY_PROVIDER),
            loaded=True,
        )

        self.identity_providers_mock.get.side_effect = [Exception("Not found"),
                                                        ret]
        self.identity_providers_mock.get.return_value = ret

        # Get the command object to test
        self.cmd = identity_provider.ShowIdentityProvider(self.app, None)

    def test_identity_provider_show(self):
        arglist = [
            identity_fakes.idp_id,
        ]
        verifylist = [
            ('identity_provider', identity_fakes.idp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_providers_mock.get.assert_called_with(
            identity_fakes.idp_id,
            id='test_idp'
        )

        collist = ('description', 'enabled', 'id', 'remote_ids')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.idp_description,
            True,
            identity_fakes.idp_id,
            identity_fakes.formatted_idp_remote_ids
        )
        self.assertEqual(datalist, data)
