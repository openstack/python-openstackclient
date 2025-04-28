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

from unittest import mock
from unittest.mock import call

from openstack import exceptions as sdk_exc
from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import group as _group
from openstack.identity.v3 import user as _user
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.identity.v3 import group
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestGroupAddUser(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self._group = sdk_fakes.generate_fake_resource(_group.Group)
        self.users = tuple(
            sdk_fakes.generate_fake_resources(_user.User, count=2)
        )

        self.identity_sdk_client.find_group.return_value = self._group
        self.identity_sdk_client.add_user_to_group.return_value = None

        self.cmd = group.AddUserToGroup(self.app, None)

    def test_group_add_user(self):
        self.identity_sdk_client.find_user.return_value = self.users[0]
        arglist = [
            self._group.name,
            self.users[0].name,
        ]
        verifylist = [
            ('group', self._group.name),
            ('user', [self.users[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.add_user_to_group.assert_called_once_with(
            self.users[0].id, self._group.id
        )
        self.assertIsNone(result)

    def test_group_add_multi_users(self):
        self.identity_sdk_client.find_user.side_effect = [
            self.users[0],
            self.users[1],
        ]
        arglist = [
            self._group.name,
            self.users[0].name,
            self.users[1].name,
        ]
        verifylist = [
            ('group', self._group.name),
            ('user', [self.users[0].name, self.users[1].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        calls = [
            call(self.users[0].id, self._group.id),
            call(self.users[1].id, self._group.id),
        ]
        self.identity_sdk_client.add_user_to_group.assert_has_calls(calls)
        self.assertIsNone(result)

    @mock.patch.object(group.LOG, 'error')
    def test_group_add_user_with_error(self, mock_error):
        self.identity_sdk_client.add_user_to_group.side_effect = [
            sdk_exc.ResourceNotFound,
            None,
        ]
        arglist = [
            self._group.name,
            self.users[0].name,
            self.users[1].name,
        ]
        verifylist = [
            ('group', self._group.name),
            ('user', [self.users[0].name, self.users[1].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            msg = f"1 of 2 users not added to group {self._group.name}."
            self.assertEqual(msg, str(e))
        msg = f"{self.users[0].name} not added to group {self._group.name}: {str(sdk_exc.ResourceNotFound())}"
        mock_error.assert_called_once_with(msg)


class TestGroupCheckUser(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.group = sdk_fakes.generate_fake_resource(_group.Group)
        self.user = sdk_fakes.generate_fake_resource(_user.User)

        self.identity_sdk_client.find_group.return_value = self.group
        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.check_user_in_group.return_value = True

        self.cmd = group.CheckUserInGroup(self.app, None)

    def test_group_check_user(self):
        arglist = [
            self.group.name,
            self.user.name,
        ]
        verifylist = [
            ('group', self.group.name),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.check_user_in_group.assert_called_once_with(
            self.user.id, self.group.id
        )
        self.assertIsNone(result)

    def test_group_check_user_server_error(self):
        self.identity_sdk_client.check_user_in_group.side_effect = (
            sdk_exc.SDKException
        )
        arglist = [
            self.group.name,
            self.user.name,
        ]
        verifylist = [
            ('group', self.group.name),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            sdk_exc.SDKException, self.cmd.take_action, parsed_args
        )


class TestGroupCreate(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    columns = (
        'description',
        'domain_id',
        'id',
        'name',
    )

    def setUp(self):
        super().setUp()
        self.group = sdk_fakes.generate_fake_resource(
            _group.Group, description=None, domain_id=None
        )
        self.group_with_options = sdk_fakes.generate_fake_resource(
            _group.Group, domain_id=self.domain.id
        )

        self.identity_sdk_client.find_group.return_value = self.group
        self.identity_sdk_client.find_domain.return_value = self.domain

        self.cmd = group.CreateGroup(self.app, None)

    def test_group_create(self):
        self.identity_sdk_client.create_group.return_value = self.group
        arglist = [
            self.group.name,
        ]
        verifylist = [
            ('name', self.group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.create_group.assert_called_once_with(
            name=self.group.name,
        )
        self.assertEqual(self.columns, columns)
        datalist = (
            self.group.description,
            None,
            self.group.id,
            self.group.name,
        )
        self.assertEqual(datalist, data)

    def test_group_create_with_options(self):
        self.identity_sdk_client.create_group.return_value = (
            self.group_with_options
        )
        arglist = [
            '--domain',
            self.domain.name,
            '--description',
            self.group_with_options.description,
            self.group_with_options.name,
        ]
        verifylist = [
            ('domain', self.domain.name),
            ('description', self.group_with_options.description),
            ('name', self.group_with_options.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.create_group.assert_called_once_with(
            name=self.group_with_options.name,
            domain_id=self.domain.id,
            description=self.group_with_options.description,
        )
        self.assertEqual(self.columns, columns)
        datalist = (
            self.group_with_options.description,
            self.domain.id,
            self.group_with_options.id,
            self.group_with_options.name,
        )
        self.assertEqual(datalist, data)

    def test_group_create_or_show(self):
        self.identity_sdk_client.find_group.return_value = self.group
        self.identity_sdk_client.create_group.side_effect = (
            sdk_exc.ConflictException
        )
        arglist = [
            '--or-show',
            self.group.name,
        ]
        verifylist = [
            ('or_show', True),
            ('name', self.group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_group.assert_called_once_with(
            self.group.name
        )
        self.assertEqual(self.columns, columns)
        datalist = (
            self.group.description,
            None,
            self.group.id,
            self.group.name,
        )
        self.assertEqual(datalist, data)

    def test_group_create_or_show_with_domain(self):
        self.identity_sdk_client.find_group.return_value = (
            self.group_with_options
        )
        self.identity_sdk_client.create_group.side_effect = (
            sdk_exc.ConflictException
        )
        arglist = [
            '--or-show',
            self.group_with_options.name,
            '--domain',
            self.domain.id,
        ]
        verifylist = [
            ('or_show', True),
            ('name', self.group_with_options.name),
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_group.assert_called_once_with(
            self.group_with_options.name, domain_id=self.domain.id
        )
        self.assertEqual(self.columns, columns)
        datalist = (
            self.group_with_options.description,
            self.domain.id,
            self.group_with_options.id,
            self.group_with_options.name,
        )
        self.assertEqual(datalist, data)


class TestGroupDelete(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    def setUp(self):
        super().setUp()

        self.group = sdk_fakes.generate_fake_resource(
            _group.Group,
            domain_id=None,
        )
        self.group_with_domain = sdk_fakes.generate_fake_resource(
            _group.Group,
            name=self.group.name,
            domain_id=self.domain.id,
        )
        self.identity_sdk_client.delete_group.return_value = None
        self.identity_sdk_client.find_domain.return_value = self.domain

        self.cmd = group.DeleteGroup(self.app, None)

    def test_group_delete(self):
        self.identity_sdk_client.find_group.return_value = self.group
        arglist = [
            self.group.id,
        ]
        verifylist = [
            ('groups', [self.group.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_group.assert_called_once_with(
            name_or_id=self.group.id, ignore_missing=False
        )
        self.identity_sdk_client.delete_group.assert_called_once_with(
            self.group.id
        )
        self.assertIsNone(result)

    def test_group_multi_delete(self):
        self.identity_sdk_client.find_group.side_effect = [
            self.group,
            self.group_with_domain,
        ]
        arglist = [self.group.id, self.group_with_domain.id]
        verifylist = [
            ('groups', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_group.assert_has_calls(
            [mock.call(self.group.id), mock.call(self.group_with_domain.id)]
        )
        self.assertIsNone(result)

    def test_group_delete_with_domain(self):
        self.identity_sdk_client.find_domain.side_effect = [
            sdk_exc.ForbiddenException
        ]
        self.identity_sdk_client.find_group.return_value = (
            self.group_with_domain
        )

        arglist = [
            '--domain',
            self.group_with_domain.domain_id,
            self.group_with_domain.name,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('groups', [self.group_with_domain.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_group.assert_called_with(
            name_or_id=self.group_with_domain.name,
            ignore_missing=False,
            domain_id=self.domain.id,
        )
        self.identity_sdk_client.delete_group.assert_called_once_with(
            self.group_with_domain.id
        )
        self.assertIsNone(result)

    def test_delete_multi_groups_with_exception(self):
        self.identity_sdk_client.find_group.side_effect = [
            self.group,
            self.group_with_domain,
            exceptions.CommandError,
        ]
        arglist = [
            self.group.id,
            self.group_with_domain.id,
            'unexist_group',
        ]
        verifylist = [
            ('groups', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 3 groups failed to delete.', str(e))

        self.identity_sdk_client.find_group.assert_has_calls(
            [
                mock.call(name_or_id=self.group.id, ignore_missing=False),
                mock.call(
                    name_or_id=self.group_with_domain.id, ignore_missing=False
                ),
                mock.call(name_or_id='unexist_group', ignore_missing=False),
            ]
        )

        self.assertEqual(3, self.identity_sdk_client.find_group.call_count)
        self.identity_sdk_client.delete_group.assert_has_calls(
            [
                mock.call(self.group.id),
                mock.call(self.group_with_domain.id),
            ]
        )


class TestGroupList(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    columns = (
        'ID',
        'Name',
    )

    def setUp(self):
        super().setUp()

        self.group = sdk_fakes.generate_fake_resource(
            _group.Group, description=None, domain_id=None
        )
        self.group_with_domain = sdk_fakes.generate_fake_resource(
            _group.Group, domain_id=self.domain.id
        )
        self.user = sdk_fakes.generate_fake_resource(_user.User)

        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.find_domain.return_value = self.domain

        # Get the command object to test
        self.cmd = group.ListGroup(self.app, None)

    def test_group_list_no_options(self):
        self.identity_sdk_client.groups.return_value = [
            self.group,
            self.group_with_domain,
        ]
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.groups.assert_called_with()

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.group.id,
                self.group.name,
            ),
            (
                self.group_with_domain.id,
                self.group_with_domain.name,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_group_list_domain(self):
        self.identity_sdk_client.groups.return_value = [self.group_with_domain]
        arglist = [
            '--domain',
            self.domain.id,
        ]
        verifylist = [
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain_id': self.domain.id,
        }

        self.identity_sdk_client.groups.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = ((self.group_with_domain.id, self.group_with_domain.name),)
        self.assertEqual(datalist, tuple(data))

    def test_group_list_user(self):
        self.identity_sdk_client.user_groups.return_value = [self.group]
        arglist = [
            '--user',
            self.user.name,
        ]
        verifylist = [
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.user_groups.assert_called_with(self.user.id)

        self.assertEqual(self.columns, columns)

        datalist = ((self.group.id, self.group.name),)
        self.assertEqual(datalist, tuple(data))

    def test_group_list_user_domain(self):
        self.identity_sdk_client.user_groups.return_value = [
            self.group_with_domain
        ]
        arglist = [
            '--user',
            self.user.name,
            '--domain',
            self.domain.name,
        ]
        verifylist = [
            ('user', self.user.name),
            ('domain', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain_id': self.domain.id,
        }

        self.identity_sdk_client.user_groups.assert_called_with(
            self.user.id, **kwargs
        )

        self.assertEqual(self.columns, columns)

        datalist = ((self.group_with_domain.id, self.group_with_domain.name),)
        self.assertEqual(datalist, tuple(data))

    def test_group_list_long(self):
        self.identity_sdk_client.groups.return_value = [
            self.group,
            self.group_with_domain,
        ]
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

        self.identity_sdk_client.groups.assert_called_with()

        long_columns = self.columns + (
            'Domain ID',
            'Description',
        )
        datalist = (
            (
                self.group.id,
                self.group.name,
                self.group.domain_id,
                self.group.description,
            ),
            (
                self.group_with_domain.id,
                self.group_with_domain.name,
                self.group_with_domain.domain_id,
                self.group_with_domain.description,
            ),
        )
        self.assertEqual(long_columns, columns)
        self.assertEqual(datalist, tuple(data))


class TestGroupRemoveUser(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self._group = sdk_fakes.generate_fake_resource(_group.Group)
        self.users = tuple(
            sdk_fakes.generate_fake_resources(_user.User, count=2)
        )

        self.identity_sdk_client.find_group.return_value = self._group
        self.identity_sdk_client.remove_user_from_group.return_value = None

        self.cmd = group.RemoveUserFromGroup(self.app, None)

    def test_group_remove_user(self):
        self.identity_sdk_client.find_user.return_value = self.users[0]
        arglist = [
            self._group.id,
            self.users[0].id,
        ]
        verifylist = [
            ('group', self._group.id),
            ('user', [self.users[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.remove_user_from_group.assert_called_once_with(
            self.users[0].id, self._group.id
        )
        self.assertIsNone(result)

    def test_group_remove_multi_users(self):
        self.identity_sdk_client.find_user.side_effect = [
            self.users[0],
            self.users[1],
        ]
        arglist = [
            self._group.name,
            self.users[0].name,
            self.users[1].name,
        ]
        verifylist = [
            ('group', self._group.name),
            ('user', [self.users[0].name, self.users[1].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        calls = [
            call(self.users[0].id, self._group.id),
            call(self.users[1].id, self._group.id),
        ]
        self.identity_sdk_client.remove_user_from_group.assert_has_calls(calls)
        self.assertIsNone(result)

    @mock.patch.object(group.LOG, 'error')
    def test_group_remove_user_with_error(self, mock_error):
        self.identity_sdk_client.remove_user_from_group.side_effect = [
            sdk_exc.ResourceNotFound(),
            None,
        ]
        arglist = [
            self._group.id,
            self.users[0].id,
            self.users[1].id,
        ]
        verifylist = [
            ('group', self._group.id),
            ('user', [self.users[0].id, self.users[1].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            msg = f"1 of 2 users not removed from group {self._group.id}."
            self.assertEqual(msg, str(e))
        msg = f"{self.users[0].id} not removed from group {self._group.id}: {str(sdk_exc.ResourceNotFound())}"
        mock_error.assert_called_once_with(msg)


class TestGroupSet(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    def setUp(self):
        super().setUp()
        self.group = sdk_fakes.generate_fake_resource(
            _group.Group, domain_id=self.domain.id
        )
        self.group_with_domain = sdk_fakes.generate_fake_resource(
            _group.Group, name=self.group.name, domain_id=self.domain.id
        )

        self.identity_sdk_client.find_group.return_value = self.group
        self.identity_sdk_client.find_domain.return_value = self.domain

        self.cmd = group.SetGroup(self.app, None)

    def test_group_set_nothing(self):
        self.identity_sdk_client.update_group.return_value = self.group
        arglist = [
            self.group.id,
        ]
        verifylist = [
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_group.assert_called_once_with(
            self.group.id
        )
        self.assertIsNone(result)

    def test_group_set_name_and_description(self):
        self.identity_sdk_client.update_group.return_value = self.group
        arglist = [
            '--name',
            'new_name',
            '--description',
            'new_description',
            self.group.id,
        ]
        verifylist = [
            ('name', 'new_name'),
            ('description', 'new_description'),
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        kwargs = {
            'name': 'new_name',
            'description': 'new_description',
        }
        self.identity_sdk_client.update_group.assert_called_once_with(
            self.group.id, **kwargs
        )
        self.assertIsNone(result)

    def test_group_set_with_domain(self):
        self.identity_sdk_client.find_domain.side_effect = [
            sdk_exc.ForbiddenException
        ]
        self.identity_sdk_client.find_group.return_value = (
            self.group_with_domain
        )
        arglist = [
            '--domain',
            self.domain.id,
            self.group_with_domain.name,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('group', self.group_with_domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_group.assert_called_once_with(
            name_or_id=self.group_with_domain.name,
            ignore_missing=False,
            domain_id=self.domain.id,
        )
        self.identity_sdk_client.update_group.assert_called_once_with(
            self.group_with_domain.id
        )
        self.assertIsNone(result)


class TestGroupShow(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    columns = (
        'description',
        'domain_id',
        'id',
        'name',
    )

    def setUp(self):
        super().setUp()
        self.group = sdk_fakes.generate_fake_resource(
            _group.Group, description=None, domain_id=None
        )
        self.group_with_domain = sdk_fakes.generate_fake_resource(
            _group.Group, name=self.group.name, domain_id=self.domain.id
        )

        self.identity_sdk_client.find_domain.return_value = self.domain

        self.cmd = group.ShowGroup(self.app, None)

    def test_group_show(self):
        self.identity_sdk_client.find_group.return_value = self.group
        arglist = [
            self.group.id,
        ]
        verifylist = [
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_group.assert_called_once_with(
            self.group.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            self.group.id,
            self.group.name,
        )
        self.assertEqual(datalist, data)

    def test_group_show_with_domain(self):
        self.identity_sdk_client.find_group.return_value = (
            self.group_with_domain
        )
        arglist = [
            '--domain',
            self.domain.id,
            self.group_with_domain.name,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('group', self.group_with_domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_group.assert_called_once_with(
            self.group_with_domain.name,
            domain_id=self.domain.id,
            ignore_missing=False,
        )
        self.assertEqual(self.columns, columns)
        datalist = (
            self.group_with_domain.description,
            self.domain.id,
            self.group_with_domain.id,
            self.group_with_domain.name,
        )
        self.assertEqual(datalist, data)
