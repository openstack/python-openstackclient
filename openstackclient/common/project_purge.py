#   Copyright 2012 OpenStack Foundation
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
#

import logging

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)


class ProjectPurge(command.Command):
    _description = _("Clean resources associated with a project")

    def get_parser(self, prog_name):
        parser = super(ProjectPurge, self).get_parser(prog_name)
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help=_("List a project's resources"),
        )
        parser.add_argument(
            '--keep-project',
            action='store_true',
            help=_("Clean project resources, but don't delete the project"),
        )
        project_group = parser.add_mutually_exclusive_group(required=True)
        project_group.add_argument(
            '--auth-project',
            action='store_true',
            help=_('Delete resources of the project used to authenticate'),
        )
        project_group.add_argument(
            '--project',
            metavar='<project>',
            help=_('Project to clean (name or ID)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if parsed_args.auth_project:
            project_id = self.app.client_manager.auth_ref.project_id
        elif parsed_args.project:
            try:
                project_id = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain,
                ).id
            except AttributeError:  # using v2 auth and supplying a domain
                project_id = utils.find_resource(
                    identity_client.tenants,
                    parsed_args.project,
                ).id

        # delete all non-identity resources
        self.delete_resources(parsed_args.dry_run, project_id)

        # clean up the project
        if not parsed_args.keep_project:
            LOG.warning(_('Deleting project: %s'), project_id)
            if not parsed_args.dry_run:
                identity_client.projects.delete(project_id)

    def delete_resources(self, dry_run, project_id):
        # servers
        try:
            compute_client = self.app.client_manager.compute
            search_opts = {'tenant_id': project_id, 'all_tenants': True}
            data = compute_client.servers.list(search_opts=search_opts)
            self.delete_objects(
                compute_client.servers.delete, data, 'server', dry_run)
        except Exception:
            pass

        # images
        try:
            image_client = self.app.client_manager.image
            api_version = int(image_client.version)
            if api_version == 1:
                data = image_client.images.list(owner=project_id)
            elif api_version == 2:
                kwargs = {'filters': {'owner': project_id}}
                data = image_client.images.list(**kwargs)
            else:
                raise NotImplementedError
            self.delete_objects(
                image_client.images.delete, data, 'image', dry_run)
        except Exception:
            pass

        # volumes, snapshots, backups
        volume_client = self.app.client_manager.volume
        search_opts = {'project_id': project_id, 'all_tenants': True}
        try:
            data = volume_client.volume_snapshots.list(search_opts=search_opts)
            self.delete_objects(
                self.delete_one_volume_snapshot,
                data,
                'volume snapshot',
                dry_run)
        except Exception:
            pass
        try:
            data = volume_client.backups.list(search_opts=search_opts)
            self.delete_objects(
                self.delete_one_volume_backup,
                data,
                'volume backup',
                dry_run)
        except Exception:
            pass
        try:
            data = volume_client.volumes.list(search_opts=search_opts)
            self.delete_objects(
                volume_client.volumes.force_delete, data, 'volume', dry_run)
        except Exception:
            pass

    def delete_objects(self, func_delete, data, resource, dry_run):
        result = 0
        for i in data:
            LOG.warning(_('Deleting %(resource)s : %(id)s') %
                        {'resource': resource, 'id': i.id})
            if not dry_run:
                try:
                    func_delete(i.id)
                except Exception as e:
                    result += 1
                    LOG.error(_("Failed to delete %(resource)s with "
                                "ID '%(id)s': %(e)s")
                              % {'resource': resource, 'id': i.id, 'e': e})
        if result > 0:
            total = len(data)
            msg = (_("%(result)s of %(total)s %(resource)ss failed "
                   "to delete.") %
                   {'result': result,
                    'total': total,
                    'resource': resource})
            LOG.error(msg)

    def delete_one_volume_snapshot(self, snapshot_id):
        volume_client = self.app.client_manager.volume
        try:
            volume_client.volume_snapshots.delete(snapshot_id)
        except Exception:
            # Only volume v2 support deleting by force
            volume_client.volume_snapshots.delete(snapshot_id, force=True)

    def delete_one_volume_backup(self, backup_id):
        volume_client = self.app.client_manager.volume
        try:
            volume_client.backups.delete(backup_id)
        except Exception:
            # Only volume v2 support deleting by force
            volume_client.backups.delete(backup_id, force=True)
