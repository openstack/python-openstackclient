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

from manilaclient.common.apiclient.exceptions import BadRequest
from osc_lib import exceptions

from openstackclient.share.v2 import share_group_type_access
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.share.v2 import fakes as share_fakes


class TestShareGroupTypeAccess(share_fakes.TestShare):
    def setUp(self):
        super().setUp()

        self.type_access_mock = self.share_client.share_group_type_access
        self.type_access_mock.reset_mock()

        self.share_group_types_mock = self.share_client.share_group_types
        self.share_group_types_mock.reset_mock()

        self.projects_mock = self.identity_client.projects
        self.projects_mock.reset_mock()


class TestShareGroupTypeAccessAllow(TestShareGroupTypeAccess):
    def setUp(self):
        super().setUp()

        self.project = identity_fakes.FakeProject.create_one_project()

        self.share_group_type = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                attrs={'is_public': False}
            )
        )
        self.share_group_types_mock.get.return_value = self.share_group_type
        self.projects_mock.get.return_value = self.project

        self.type_access_mock.add_project_access.return_value = None

        # Get the command object to test
        self.cmd = share_group_type_access.ShareGroupTypeAccessAllow(
            self.app, None
        )

    def test_share_group_type_access_create(self):
        arglist = [self.share_group_type.id, self.project.id]
        verifylist = [
            ('share_group_type', self.share_group_type.id),
            ('projects', [self.project.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.type_access_mock.add_project_access.assert_called_with(
            self.share_group_type, self.project.id
        )

        self.assertIsNone(result)

    def test_share_group_type_access_create_invalid_project_exception(self):
        arglist = [self.share_group_type.id, 'invalid_project_format']
        verifylist = [
            ('share_group_type', self.share_group_type.id),
            ('projects', ['invalid_project_format']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.type_access_mock.add_project_access.side_effect = BadRequest()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareGroupTypeAccessList(TestShareGroupTypeAccess):
    columns = ['Project ID']
    data = (('',), ('',))

    def setUp(self):
        super().setUp()

        self.type_access_mock.list.return_value = (self.columns, self.data)

        # Get the command object to test
        self.cmd = share_group_type_access.ListShareGroupTypeAccess(
            self.app, None
        )

    def test_share_group_type_access_list(self):
        share_group_type = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                attrs={'is_public': False}
            )
        )
        self.share_group_types_mock.get.return_value = share_group_type

        arglist = [
            share_group_type.id,
        ]
        verifylist = [('share_group_type', share_group_type.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.type_access_mock.list.assert_called_once_with(share_group_type)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_share_group_type_access_list_public_type(self):
        share_group_type = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                attrs={'is_public': True}
            )
        )

        self.share_group_types_mock.get.return_value = share_group_type

        arglist = [
            share_group_type.id,
        ]
        verifylist = [('share_group_type', share_group_type.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareGroupTypeAccessDeny(TestShareGroupTypeAccess):
    def setUp(self):
        super().setUp()

        self.project = identity_fakes.FakeProject.create_one_project()

        self.share_group_type = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                attrs={'is_public': False}
            )
        )
        self.share_group_types_mock.get.return_value = self.share_group_type
        self.projects_mock.get.return_value = self.project

        self.type_access_mock.remove_project_access.return_value = None

        # Get the command object to test
        self.cmd = share_group_type_access.ShareGroupTypeAccessDeny(
            self.app, None
        )

    def test_share_group_type_access_delete(self):
        arglist = [self.share_group_type.id, self.project.id]
        verifylist = [
            ('share_group_type', self.share_group_type.id),
            ('projects', [self.project.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.type_access_mock.remove_project_access.assert_called_with(
            self.share_group_type, self.project.id
        )

        self.assertIsNone(result)

    def test_share_group_type_access_delete_exception(self):
        arglist = [self.share_group_type.id, 'invalid_project_format']
        verifylist = [
            ('share_group_type', self.share_group_type.id),
            ('projects', ['invalid_project_format']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.type_access_mock.remove_project_access.side_effect = BadRequest()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
