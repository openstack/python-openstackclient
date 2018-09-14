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

import mock

from osc_lib import exceptions

from openstackclient.common import project_purge
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


class TestProjectPurgeInit(tests_utils.TestCommand):

    def setUp(self):
        super(TestProjectPurgeInit, self).setUp()
        compute_client = compute_fakes.FakeComputev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.compute = compute_client
        self.servers_mock = compute_client.servers
        self.servers_mock.reset_mock()

        volume_client = volume_fakes.FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.volume = volume_client
        self.volumes_mock = volume_client.volumes
        self.volumes_mock.reset_mock()
        self.snapshots_mock = volume_client.volume_snapshots
        self.snapshots_mock.reset_mock()
        self.backups_mock = volume_client.backups
        self.backups_mock.reset_mock()

        identity_client = identity_fakes.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.domains_mock = identity_client.domains
        self.domains_mock.reset_mock()
        self.projects_mock = identity_client.projects
        self.projects_mock.reset_mock()

        image_client = image_fakes.FakeImagev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.image = image_client
        self.images_mock = image_client.images
        self.images_mock.reset_mock()


class TestProjectPurge(TestProjectPurgeInit):

    project = identity_fakes.FakeProject.create_one_project()
    server = compute_fakes.FakeServer.create_one_server()
    image = image_fakes.FakeImage.create_one_image()
    volume = volume_fakes.FakeVolume.create_one_volume()
    backup = volume_fakes.FakeBackup.create_one_backup()
    snapshot = volume_fakes.FakeSnapshot.create_one_snapshot()

    def setUp(self):
        super(TestProjectPurge, self).setUp()
        self.projects_mock.get.return_value = self.project
        self.projects_mock.delete.return_value = None
        self.images_mock.list.return_value = [self.image]
        self.images_mock.delete.return_value = None
        self.servers_mock.list.return_value = [self.server]
        self.servers_mock.delete.return_value = None
        self.volumes_mock.list.return_value = [self.volume]
        self.volumes_mock.delete.return_value = None
        self.volumes_mock.force_delete.return_value = None
        self.snapshots_mock.list.return_value = [self.snapshot]
        self.snapshots_mock.delete.return_value = None
        self.backups_mock.list.return_value = [self.backup]
        self.backups_mock.delete.return_value = None

        self.cmd = project_purge.ProjectPurge(self.app, None)

    def test_project_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_project_purge_with_project(self):
        arglist = [
            '--project', self.project.id,
        ]
        verifylist = [
            ('dry_run', False),
            ('keep_project', False),
            ('auth_project', False),
            ('project', self.project.id),
            ('project_domain', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_once_with(self.project.id)
        self.projects_mock.delete.assert_called_once_with(self.project.id)
        self.servers_mock.list.assert_called_once_with(
            search_opts={'tenant_id': self.project.id, 'all_tenants': True})
        kwargs = {'filters': {'owner': self.project.id}}
        self.images_mock.list.assert_called_once_with(**kwargs)
        volume_search_opts = {'project_id': self.project.id,
                              'all_tenants': True}
        self.volumes_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.snapshots_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.backups_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.servers_mock.delete.assert_called_once_with(self.server.id)
        self.images_mock.delete.assert_called_once_with(self.image.id)
        self.volumes_mock.force_delete.assert_called_once_with(self.volume.id)
        self.snapshots_mock.delete.assert_called_once_with(self.snapshot.id)
        self.backups_mock.delete.assert_called_once_with(self.backup.id)
        self.assertIsNone(result)

    def test_project_purge_with_dry_run(self):
        arglist = [
            '--dry-run',
            '--project', self.project.id,
        ]
        verifylist = [
            ('dry_run', True),
            ('keep_project', False),
            ('auth_project', False),
            ('project', self.project.id),
            ('project_domain', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_once_with(self.project.id)
        self.projects_mock.delete.assert_not_called()
        self.servers_mock.list.assert_called_once_with(
            search_opts={'tenant_id': self.project.id, 'all_tenants': True})
        kwargs = {'filters': {'owner': self.project.id}}
        self.images_mock.list.assert_called_once_with(**kwargs)
        volume_search_opts = {'project_id': self.project.id,
                              'all_tenants': True}
        self.volumes_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.snapshots_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.backups_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.servers_mock.delete.assert_not_called()
        self.images_mock.delete.assert_not_called()
        self.volumes_mock.force_delete.assert_not_called()
        self.snapshots_mock.delete.assert_not_called()
        self.backups_mock.delete.assert_not_called()
        self.assertIsNone(result)

    def test_project_purge_with_keep_project(self):
        arglist = [
            '--keep-project',
            '--project', self.project.id,
        ]
        verifylist = [
            ('dry_run', False),
            ('keep_project', True),
            ('auth_project', False),
            ('project', self.project.id),
            ('project_domain', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_once_with(self.project.id)
        self.projects_mock.delete.assert_not_called()
        self.servers_mock.list.assert_called_once_with(
            search_opts={'tenant_id': self.project.id, 'all_tenants': True})
        kwargs = {'filters': {'owner': self.project.id}}
        self.images_mock.list.assert_called_once_with(**kwargs)
        volume_search_opts = {'project_id': self.project.id,
                              'all_tenants': True}
        self.volumes_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.snapshots_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.backups_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.servers_mock.delete.assert_called_once_with(self.server.id)
        self.images_mock.delete.assert_called_once_with(self.image.id)
        self.volumes_mock.force_delete.assert_called_once_with(self.volume.id)
        self.snapshots_mock.delete.assert_called_once_with(self.snapshot.id)
        self.backups_mock.delete.assert_called_once_with(self.backup.id)
        self.assertIsNone(result)

    def test_project_purge_with_auth_project(self):
        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.project_id = self.project.id
        arglist = [
            '--auth-project',
        ]
        verifylist = [
            ('dry_run', False),
            ('keep_project', False),
            ('auth_project', True),
            ('project', None),
            ('project_domain', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_not_called()
        self.projects_mock.delete.assert_called_once_with(self.project.id)
        self.servers_mock.list.assert_called_once_with(
            search_opts={'tenant_id': self.project.id, 'all_tenants': True})
        kwargs = {'filters': {'owner': self.project.id}}
        self.images_mock.list.assert_called_once_with(**kwargs)
        volume_search_opts = {'project_id': self.project.id,
                              'all_tenants': True}
        self.volumes_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.snapshots_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.backups_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.servers_mock.delete.assert_called_once_with(self.server.id)
        self.images_mock.delete.assert_called_once_with(self.image.id)
        self.volumes_mock.force_delete.assert_called_once_with(self.volume.id)
        self.snapshots_mock.delete.assert_called_once_with(self.snapshot.id)
        self.backups_mock.delete.assert_called_once_with(self.backup.id)
        self.assertIsNone(result)

    @mock.patch.object(project_purge.LOG, 'error')
    def test_project_purge_with_exception(self, mock_error):
        self.servers_mock.delete.side_effect = exceptions.CommandError()
        arglist = [
            '--project', self.project.id,
        ]
        verifylist = [
            ('dry_run', False),
            ('keep_project', False),
            ('auth_project', False),
            ('project', self.project.id),
            ('project_domain', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_once_with(self.project.id)
        self.projects_mock.delete.assert_called_once_with(self.project.id)
        self.servers_mock.list.assert_called_once_with(
            search_opts={'tenant_id': self.project.id, 'all_tenants': True})
        kwargs = {'filters': {'owner': self.project.id}}
        self.images_mock.list.assert_called_once_with(**kwargs)
        volume_search_opts = {'project_id': self.project.id,
                              'all_tenants': True}
        self.volumes_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.snapshots_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.backups_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.servers_mock.delete.assert_called_once_with(self.server.id)
        self.images_mock.delete.assert_called_once_with(self.image.id)
        self.volumes_mock.force_delete.assert_called_once_with(self.volume.id)
        self.snapshots_mock.delete.assert_called_once_with(self.snapshot.id)
        self.backups_mock.delete.assert_called_once_with(self.backup.id)
        mock_error.assert_called_with("1 of 1 servers failed to delete.")
        self.assertIsNone(result)

    def test_project_purge_with_force_delete_backup(self):
        self.backups_mock.delete.side_effect = [exceptions.CommandError, None]
        arglist = [
            '--project', self.project.id,
        ]
        verifylist = [
            ('dry_run', False),
            ('keep_project', False),
            ('auth_project', False),
            ('project', self.project.id),
            ('project_domain', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_once_with(self.project.id)
        self.projects_mock.delete.assert_called_once_with(self.project.id)
        self.servers_mock.list.assert_called_once_with(
            search_opts={'tenant_id': self.project.id, 'all_tenants': True})
        kwargs = {'filters': {'owner': self.project.id}}
        self.images_mock.list.assert_called_once_with(**kwargs)
        volume_search_opts = {'project_id': self.project.id,
                              'all_tenants': True}
        self.volumes_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.snapshots_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.backups_mock.list.assert_called_once_with(
            search_opts=volume_search_opts)
        self.servers_mock.delete.assert_called_once_with(self.server.id)
        self.images_mock.delete.assert_called_once_with(self.image.id)
        self.volumes_mock.force_delete.assert_called_once_with(self.volume.id)
        self.snapshots_mock.delete.assert_called_once_with(self.snapshot.id)
        self.assertEqual(2, self.backups_mock.delete.call_count)
        self.backups_mock.delete.assert_called_with(self.backup.id, force=True)
        self.assertIsNone(result)
