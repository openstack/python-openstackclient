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

from openstackclient.common import project_cleanup
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as test_utils


class TestProjectCleanup(test_utils.TestCommand):
    project = identity_fakes.FakeProject.create_one_project()

    def setUp(self):
        super().setUp()
        self.cmd = project_cleanup.ProjectCleanup(self.app, None)

        self.project_cleanup_mock = mock.Mock()
        self.sdk_connect_as_project_mock = mock.Mock(
            return_value=self.app.client_manager.sdk_connection
        )
        self.app.client_manager.sdk_connection.project_cleanup = (
            self.project_cleanup_mock
        )
        self.app.client_manager.sdk_connection.identity.find_project = (
            mock.Mock(return_value=self.project)
        )
        self.app.client_manager.sdk_connection.connect_as_project = (
            self.sdk_connect_as_project_mock
        )

    def test_project_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_project_cleanup_with_filters(self):
        arglist = [
            '--project',
            self.project.id,
            '--created-before',
            '2200-01-01',
            '--updated-before',
            '2200-01-02',
        ]
        verifylist = [
            ('dry_run', False),
            ('auth_project', False),
            ('project', self.project.id),
            ('created_before', '2200-01-01'),
            ('updated_before', '2200-01-02'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = None

        with mock.patch('getpass.getpass', return_value='y'):
            result = self.cmd.take_action(parsed_args)

        self.sdk_connect_as_project_mock.assert_called_with(self.project)
        filters = {'created_at': '2200-01-01', 'updated_at': '2200-01-02'}

        calls = [
            mock.call(
                dry_run=True,
                status_queue=mock.ANY,
                filters=filters,
                skip_resources=None,
            ),
            mock.call(
                dry_run=False,
                status_queue=mock.ANY,
                filters=filters,
                skip_resources=None,
            ),
        ]
        self.project_cleanup_mock.assert_has_calls(calls)

        self.assertIsNone(result)

    def test_project_cleanup_with_auto_approve(self):
        arglist = [
            '--project',
            self.project.id,
            '--auto-approve',
        ]
        verifylist = [
            ('dry_run', False),
            ('auth_project', False),
            ('project', self.project.id),
            ('auto_approve', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = None

        result = self.cmd.take_action(parsed_args)

        self.sdk_connect_as_project_mock.assert_called_with(self.project)
        calls = [
            mock.call(
                dry_run=True,
                status_queue=mock.ANY,
                filters={},
                skip_resources=None,
            ),
            mock.call(
                dry_run=False,
                status_queue=mock.ANY,
                filters={},
                skip_resources=None,
            ),
        ]
        self.project_cleanup_mock.assert_has_calls(calls)

        self.assertIsNone(result)

    def test_project_cleanup_with_project(self):
        arglist = [
            '--project',
            self.project.id,
        ]
        verifylist = [
            ('dry_run', False),
            ('auth_project', False),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = None

        with mock.patch('getpass.getpass', return_value='y'):
            result = self.cmd.take_action(parsed_args)

        self.sdk_connect_as_project_mock.assert_called_with(self.project)
        calls = [
            mock.call(
                dry_run=True,
                status_queue=mock.ANY,
                filters={},
                skip_resources=None,
            ),
            mock.call(
                dry_run=False,
                status_queue=mock.ANY,
                filters={},
                skip_resources=None,
            ),
        ]
        self.project_cleanup_mock.assert_has_calls(calls)

        self.assertIsNone(result)

    def test_project_cleanup_with_project_abort(self):
        arglist = [
            '--project',
            self.project.id,
        ]
        verifylist = [
            ('dry_run', False),
            ('auth_project', False),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = None

        with mock.patch('getpass.getpass', return_value='y'):
            result = self.cmd.take_action(parsed_args)

        self.sdk_connect_as_project_mock.assert_called_with(self.project)
        calls = [
            mock.call(
                dry_run=True,
                status_queue=mock.ANY,
                filters={},
                skip_resources=None,
            ),
        ]
        self.project_cleanup_mock.assert_has_calls(calls)

        self.assertIsNone(result)

    def test_project_cleanup_with_dry_run(self):
        arglist = [
            '--dry-run',
            '--project',
            self.project.id,
        ]
        verifylist = [
            ('dry_run', True),
            ('auth_project', False),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = None

        result = self.cmd.take_action(parsed_args)

        self.sdk_connect_as_project_mock.assert_called_with(self.project)
        self.project_cleanup_mock.assert_called_once_with(
            dry_run=True,
            status_queue=mock.ANY,
            filters={},
            skip_resources=None,
        )

        self.assertIsNone(result)

    def test_project_cleanup_with_auth_project(self):
        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.project_id = self.project.id
        arglist = [
            '--auth-project',
        ]
        verifylist = [
            ('dry_run', False),
            ('auth_project', True),
            ('project', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = None

        with mock.patch('getpass.getpass', return_value='y'):
            result = self.cmd.take_action(parsed_args)

        self.sdk_connect_as_project_mock.assert_not_called()
        calls = [
            mock.call(
                dry_run=True,
                status_queue=mock.ANY,
                filters={},
                skip_resources=None,
            ),
            mock.call(
                dry_run=False,
                status_queue=mock.ANY,
                filters={},
                skip_resources=None,
            ),
        ]
        self.project_cleanup_mock.assert_has_calls(calls)

        self.assertIsNone(result)

    def test_project_cleanup_with_skip_resource(self):
        skip_resource = "block_storage.backup"
        arglist = [
            '--project',
            self.project.id,
            '--skip-resource',
            skip_resource,
        ]
        verifylist = [('skip_resource', [skip_resource])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = None

        with mock.patch('getpass.getpass', return_value='y'):
            result = self.cmd.take_action(parsed_args)

        self.sdk_connect_as_project_mock.assert_called_with(self.project)

        calls = [
            mock.call(
                dry_run=True,
                status_queue=mock.ANY,
                filters={},
                skip_resources=[skip_resource],
            ),
            mock.call(
                dry_run=False,
                status_queue=mock.ANY,
                filters={},
                skip_resources=[skip_resource],
            ),
        ]
        self.project_cleanup_mock.assert_has_calls(calls)

        self.assertIsNone(result)
