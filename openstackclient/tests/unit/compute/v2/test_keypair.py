#   Copyright 2016 IBM
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
from unittest import mock
from unittest.mock import call
import uuid

from osc_lib import exceptions

from openstackclient.compute.v2 import keypair
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestKeypair(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        # Initialize the user mock
        self.users_mock = self.identity_client.users
        self.users_mock.reset_mock()
        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )


class TestKeypairCreate(TestKeypair):
    def setUp(self):
        super().setUp()

        self.keypair = compute_fakes.create_one_keypair()

        self.columns = (
            'created_at',
            'fingerprint',
            'id',
            'is_deleted',
            'name',
            'type',
            'user_id',
        )
        self.data = (
            self.keypair.created_at,
            self.keypair.fingerprint,
            self.keypair.id,
            self.keypair.is_deleted,
            self.keypair.name,
            self.keypair.type,
            self.keypair.user_id,
        )

        # Get the command object to test
        self.cmd = keypair.CreateKeypair(self.app, None)

        self.compute_sdk_client.create_keypair.return_value = self.keypair

    @mock.patch.object(
        keypair,
        '_generate_keypair',
        return_value=keypair.Keypair('private', 'public'),
    )
    def test_keypair_create_no_options(self, mock_generate):
        arglist = [
            self.keypair.name,
        ]
        verifylist = [
            ('name', self.keypair.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_sdk_client.create_keypair.assert_called_with(
            name=self.keypair.name,
            public_key=mock_generate.return_value.public_key,
        )

        self.assertEqual({}, columns)
        self.assertEqual({}, data)

    def test_keypair_create_public_key(self):
        self.data = (
            self.keypair.created_at,
            self.keypair.fingerprint,
            self.keypair.id,
            self.keypair.is_deleted,
            self.keypair.name,
            self.keypair.type,
            self.keypair.user_id,
        )

        arglist = [
            '--public-key',
            self.keypair.public_key,
            self.keypair.name,
        ]
        verifylist = [
            ('public_key', self.keypair.public_key),
            ('name', self.keypair.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch(
            'openstackclient.compute.v2.keypair.open'
        ) as mock_open:
            mock_open.return_value = mock.MagicMock()
            m_file = mock_open.return_value.__enter__.return_value
            m_file.read.return_value = 'dummy'

            columns, data = self.cmd.take_action(parsed_args)

            self.compute_sdk_client.create_keypair.assert_called_with(
                name=self.keypair.name,
                public_key=self.keypair.public_key,
            )

            self.assertEqual(self.columns, columns)
            self.assertEqual(self.data, data)

    @mock.patch.object(
        keypair,
        '_generate_keypair',
        return_value=keypair.Keypair('private', 'public'),
    )
    def test_keypair_create_private_key(self, mock_generate):
        tmp_pk_file = '/tmp/kp-file-' + uuid.uuid4().hex
        arglist = [
            '--private-key',
            tmp_pk_file,
            self.keypair.name,
        ]
        verifylist = [
            ('private_key', tmp_pk_file),
            ('name', self.keypair.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch(
            'openstackclient.compute.v2.keypair.open'
        ) as mock_open:
            mock_open.return_value = mock.MagicMock()
            m_file = mock_open.return_value.__enter__.return_value

            columns, data = self.cmd.take_action(parsed_args)

            self.compute_sdk_client.create_keypair.assert_called_with(
                name=self.keypair.name,
                public_key=mock_generate.return_value.public_key,
            )

            mock_open.assert_called_once_with(tmp_pk_file, 'w+')
            m_file.write.assert_called_once_with(
                mock_generate.return_value.private_key,
            )

            self.assertEqual(self.columns, columns)
            self.assertEqual(self.data, data)

    def test_keypair_create_with_key_type(self):
        self.set_compute_api_version('2.2')

        for key_type in ['x509', 'ssh']:
            self.compute_sdk_client.create_keypair.return_value = self.keypair

            self.data = (
                self.keypair.created_at,
                self.keypair.fingerprint,
                self.keypair.id,
                self.keypair.is_deleted,
                self.keypair.name,
                self.keypair.type,
                self.keypair.user_id,
            )
            arglist = [
                '--public-key',
                self.keypair.public_key,
                self.keypair.name,
                '--type',
                key_type,
            ]
            verifylist = [
                ('public_key', self.keypair.public_key),
                ('name', self.keypair.name),
                ('type', key_type),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            with mock.patch(
                'openstackclient.compute.v2.keypair.open'
            ) as mock_open:
                mock_open.return_value = mock.MagicMock()
                m_file = mock_open.return_value.__enter__.return_value
                m_file.read.return_value = 'dummy'
                columns, data = self.cmd.take_action(parsed_args)

            self.compute_sdk_client.create_keypair.assert_called_with(
                name=self.keypair.name,
                public_key=self.keypair.public_key,
                key_type=key_type,
            )

            self.assertEqual(self.columns, columns)
            self.assertEqual(self.data, data)

    def test_keypair_create_with_key_type_pre_v22(self):
        self.set_compute_api_version('2.1')

        for key_type in ['x509', 'ssh']:
            arglist = [
                '--public-key',
                self.keypair.public_key,
                self.keypair.name,
                '--type',
                'ssh',
            ]
            verifylist = [
                ('public_key', self.keypair.public_key),
                ('name', self.keypair.name),
                ('type', 'ssh'),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            with mock.patch(
                'openstackclient.compute.v2.keypair.open'
            ) as mock_open:
                mock_open.return_value = mock.MagicMock()
                m_file = mock_open.return_value.__enter__.return_value
                m_file.read.return_value = 'dummy'

                ex = self.assertRaises(
                    exceptions.CommandError, self.cmd.take_action, parsed_args
                )

            self.assertIn(
                '--os-compute-api-version 2.2 or greater is required', str(ex)
            )

    @mock.patch.object(
        keypair,
        '_generate_keypair',
        return_value=keypair.Keypair('private', 'public'),
    )
    def test_key_pair_create_with_user(self, mock_generate):
        self.set_compute_api_version('2.10')

        arglist = [
            '--user',
            identity_fakes.user_name,
            self.keypair.name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('name', self.keypair.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_sdk_client.create_keypair.assert_called_with(
            name=self.keypair.name,
            user_id=identity_fakes.user_id,
            public_key=mock_generate.return_value.public_key,
        )

        self.assertEqual({}, columns)
        self.assertEqual({}, data)

    def test_key_pair_create_with_user_pre_v210(self):
        self.set_compute_api_version('2.9')

        arglist = [
            '--user',
            identity_fakes.user_name,
            self.keypair.name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('name', self.keypair.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.10 or greater is required', str(ex)
        )


class TestKeypairDelete(TestKeypair):
    keypairs = compute_fakes.create_keypairs(count=2)

    def setUp(self):
        super().setUp()

        self.cmd = keypair.DeleteKeypair(self.app, None)

    def test_keypair_delete(self):
        arglist = [self.keypairs[0].name]
        verifylist = [
            ('name', [self.keypairs[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ret = self.cmd.take_action(parsed_args)

        self.assertIsNone(ret)
        self.compute_sdk_client.delete_keypair.assert_called_with(
            self.keypairs[0].name, ignore_missing=False
        )

    def test_delete_multiple_keypairs(self):
        arglist = []
        for k in self.keypairs:
            arglist.append(k.name)
        verifylist = [
            ('name', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for k in self.keypairs:
            calls.append(call(k.name, ignore_missing=False))
        self.compute_sdk_client.delete_keypair.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_keypairs_with_exception(self):
        arglist = [
            self.keypairs[0].name,
            'unexist_keypair',
        ]
        verifylist = [
            ('name', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.compute_sdk_client.delete_keypair.side_effect = [
            None,
            exceptions.CommandError,
        ]
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 keys failed to delete.', str(e))

        calls = []
        for k in arglist:
            calls.append(call(k, ignore_missing=False))
        self.compute_sdk_client.delete_keypair.assert_has_calls(calls)

    def test_keypair_delete_with_user(self):
        self.set_compute_api_version('2.10')

        arglist = ['--user', identity_fakes.user_name, self.keypairs[0].name]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('name', [self.keypairs[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ret = self.cmd.take_action(parsed_args)

        self.assertIsNone(ret)
        self.compute_sdk_client.delete_keypair.assert_called_with(
            self.keypairs[0].name,
            user_id=identity_fakes.user_id,
            ignore_missing=False,
        )

    def test_keypair_delete_with_user_pre_v210(self):
        self.set_compute_api_version('2.9')

        arglist = ['--user', identity_fakes.user_name, self.keypairs[0].name]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('name', [self.keypairs[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.10 or greater is required', str(ex)
        )


class TestKeypairList(TestKeypair):
    # Return value of self.compute_sdk_client.keypairs().
    keypairs = compute_fakes.create_keypairs(count=1)

    def setUp(self):
        super().setUp()

        self.compute_sdk_client.keypairs.return_value = self.keypairs

        # Get the command object to test
        self.cmd = keypair.ListKeypair(self.app, None)

    def test_keypair_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values

        self.compute_sdk_client.keypairs.assert_called_with()

        self.assertEqual(('Name', 'Fingerprint'), columns)
        self.assertEqual(
            ((self.keypairs[0].name, self.keypairs[0].fingerprint),),
            tuple(data),
        )

    def test_keypair_list_v22(self):
        self.set_compute_api_version('2.22')

        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values

        self.compute_sdk_client.keypairs.assert_called_with()

        self.assertEqual(('Name', 'Fingerprint', 'Type'), columns)
        self.assertEqual(
            (
                (
                    self.keypairs[0].name,
                    self.keypairs[0].fingerprint,
                    self.keypairs[0].type,
                ),
            ),
            tuple(data),
        )

    def test_keypair_list_with_user(self):
        self.set_compute_api_version('2.35')

        users_mock = self.identity_client.users
        users_mock.reset_mock()
        users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        arglist = [
            '--user',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        users_mock.get.assert_called_with(identity_fakes.user_name)
        self.compute_sdk_client.keypairs.assert_called_with(
            user_id=identity_fakes.user_id,
        )

        self.assertEqual(('Name', 'Fingerprint', 'Type'), columns)
        self.assertEqual(
            (
                (
                    self.keypairs[0].name,
                    self.keypairs[0].fingerprint,
                    self.keypairs[0].type,
                ),
            ),
            tuple(data),
        )

    def test_keypair_list_with_user_pre_v210(self):
        self.set_compute_api_version('2.9')

        arglist = [
            '--user',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.10 or greater is required', str(ex)
        )

    def test_keypair_list_with_project(self):
        self.set_compute_api_version('2.35')

        projects_mock = self.identity_client.tenants
        projects_mock.reset_mock()
        projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        users_mock = self.identity_client.users
        users_mock.reset_mock()
        users_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.USER),
                loaded=True,
            ),
        ]

        arglist = ['--project', identity_fakes.project_name]
        verifylist = [('project', identity_fakes.project_name)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        projects_mock.get.assert_called_with(identity_fakes.project_name)
        users_mock.list.assert_called_with(tenant_id=identity_fakes.project_id)
        self.compute_sdk_client.keypairs.assert_called_with(
            user_id=identity_fakes.user_id,
        )

        self.assertEqual(('Name', 'Fingerprint', 'Type'), columns)
        self.assertEqual(
            (
                (
                    self.keypairs[0].name,
                    self.keypairs[0].fingerprint,
                    self.keypairs[0].type,
                ),
            ),
            tuple(data),
        )

    def test_keypair_list_with_project_pre_v210(self):
        self.set_compute_api_version('2.9')

        arglist = ['--project', identity_fakes.project_name]
        verifylist = [('project', identity_fakes.project_name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.10 or greater is required', str(ex)
        )

    def test_keypair_list_conflicting_user_options(self):
        arglist = [
            '--user',
            identity_fakes.user_name,
            '--project',
            identity_fakes.project_name,
        ]

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def test_keypair_list_with_limit(self):
        self.set_compute_api_version('2.35')

        arglist = [
            '--limit',
            '1',
        ]
        verifylist = [
            ('limit', 1),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_sdk_client.keypairs.assert_called_with(limit=1)

    def test_keypair_list_with_limit_pre_v235(self):
        self.set_compute_api_version('2.34')

        arglist = [
            '--limit',
            '1',
        ]
        verifylist = [
            ('limit', 1),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.assertIn(
            '--os-compute-api-version 2.35 or greater is required', str(ex)
        )

    def test_keypair_list_with_marker(self):
        self.set_compute_api_version('2.35')

        arglist = [
            '--marker',
            'test_kp',
        ]
        verifylist = [
            ('marker', 'test_kp'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_sdk_client.keypairs.assert_called_with(marker='test_kp')

    def test_keypair_list_with_marker_pre_v235(self):
        self.set_compute_api_version('2.34')

        arglist = [
            '--marker',
            'test_kp',
        ]
        verifylist = [
            ('marker', 'test_kp'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.assertIn(
            '--os-compute-api-version 2.35 or greater is required', str(ex)
        )


class TestKeypairShow(TestKeypair):
    def setUp(self):
        super().setUp()

        self.columns = (
            'created_at',
            'fingerprint',
            'id',
            'is_deleted',
            'name',
            'private_key',
            'type',
            'user_id',
        )

        self.cmd = keypair.ShowKeypair(self.app, None)

    def test_keypair_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should boil here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_keypair_show(self):
        self.keypair = compute_fakes.create_one_keypair()
        self.compute_sdk_client.find_keypair.return_value = self.keypair

        self.data = (
            self.keypair.created_at,
            self.keypair.fingerprint,
            self.keypair.id,
            self.keypair.is_deleted,
            self.keypair.name,
            self.keypair.private_key,
            self.keypair.type,
            self.keypair.user_id,
        )

        arglist = [self.keypair.name]
        verifylist = [('name', self.keypair.name)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_sdk_client.find_keypair.assert_called_with(
            self.keypair.name, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_keypair_show_public(self):
        self.keypair = compute_fakes.create_one_keypair()
        self.compute_sdk_client.find_keypair.return_value = self.keypair

        arglist = ['--public-key', self.keypair.name]
        verifylist = [('public_key', True), ('name', self.keypair.name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual({}, columns)
        self.assertEqual({}, data)

    def test_keypair_show_with_user(self):
        self.set_compute_api_version('2.10')

        self.keypair = compute_fakes.create_one_keypair()
        self.compute_sdk_client.find_keypair.return_value = self.keypair

        self.data = (
            self.keypair.created_at,
            self.keypair.fingerprint,
            self.keypair.id,
            self.keypair.is_deleted,
            self.keypair.name,
            self.keypair.private_key,
            self.keypair.type,
            self.keypair.user_id,
        )

        arglist = [
            '--user',
            identity_fakes.user_name,
            self.keypair.name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('name', self.keypair.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.get.assert_called_with(identity_fakes.user_name)
        self.compute_sdk_client.find_keypair.assert_called_with(
            self.keypair.name,
            ignore_missing=False,
            user_id=identity_fakes.user_id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_keypair_show_with_user_pre_v210(self):
        self.set_compute_api_version('2.9')

        self.keypair = compute_fakes.create_one_keypair()
        arglist = [
            '--user',
            identity_fakes.user_name,
            self.keypair.name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('name', self.keypair.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-compute-api-version 2.10 or greater is required',
            str(ex),
        )
