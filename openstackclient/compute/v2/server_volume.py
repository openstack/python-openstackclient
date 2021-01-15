# Copyright 2020, Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Compute v2 Server action implementations"""

from novaclient import api_versions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


class ListServerVolume(command.Lister):
    """List all the volumes attached to a server."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            help=_('Server to list volume attachments for (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        volumes = compute_client.volumes.get_server_volumes(server.id)

        columns = (
            'id',
            'device',
            'serverId',
            'volumeId',
        )
        column_headers = (
            'ID',
            'Device',
            'Server ID',
            'Volume ID',
        )
        if compute_client.api_version >= api_versions.APIVersion('2.70'):
            columns += ('tag',)
            column_headers += ('Tag',)

        if compute_client.api_version >= api_versions.APIVersion('2.79'):
            columns += ('delete_on_termination',)
            column_headers += ('Delete On Termination?',)

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s, columns, mixed_case_fields=('serverId', 'volumeId')
                ) for s in volumes
            ),
        )


class UpdateServerVolume(command.Command):
    """Update a volume attachment on the server."""

    def get_parser(self, prog_name):
        parser = super(UpdateServerVolume, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            help=_('Server to update volume for (name or ID)'),
        )
        parser.add_argument(
            'volume',
            help=_('Volume (ID)'),
        )
        termination_group = parser.add_mutually_exclusive_group()
        termination_group.add_argument(
            '--delete-on-termination',
            action='store_true',
            dest='delete_on_termination',
            default=None,
            help=_(
                'Delete the volume when the server is destroyed '
                '(supported by --os-compute-api-version 2.85 or above)'
            ),
        )
        termination_group.add_argument(
            '--preserve-on-termination',
            action='store_false',
            dest='delete_on_termination',
            help=_(
                'Preserve the volume when the server is destroyed '
                '(supported by --os-compute-api-version 2.85 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute

        if parsed_args.delete_on_termination is not None:
            if compute_client.api_version < api_versions.APIVersion('2.85'):
                msg = _(
                    '--os-compute-api-version 2.85 or greater is required to '
                    'support the --(no-)delete-on-termination option'
                )
                raise exceptions.CommandError(msg)

            server = utils.find_resource(
                compute_client.servers,
                parsed_args.server,
            )

            # NOTE(stephenfin): This may look silly, and that's because it is.
            # This API was originally used only for the swapping volumes, which
            # is an internal operation that should only be done by
            # orchestration software rather than a human. We're not going to
            # expose that, but we are going to expose the ability to change the
            # delete on termination behavior.
            compute_client.volumes.update_server_volume(
                server.id,
                parsed_args.volume,
                parsed_args.volume,
                delete_on_termination=parsed_args.delete_on_termination,
            )
