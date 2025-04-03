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

from openstack import utils as sdk_utils
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

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        volumes = compute_client.volume_attachments(server)

        columns: tuple[str, ...] = ()
        column_headers: tuple[str, ...] = ()

        if not sdk_utils.supports_microversion(compute_client, '2.89'):
            columns += ('id',)
            column_headers += ('ID',)

        columns += (
            'device',
            'server_id',
            'volume_id',
        )
        column_headers += (
            'Device',
            'Server ID',
            'Volume ID',
        )

        if sdk_utils.supports_microversion(compute_client, '2.70'):
            columns += ('tag',)
            column_headers += ('Tag',)

        if sdk_utils.supports_microversion(compute_client, '2.79'):
            columns += ('delete_on_termination',)
            column_headers += ('Delete On Termination?',)

        if sdk_utils.supports_microversion(compute_client, '2.89'):
            columns += ('attachment_id', 'bdm_id')
            column_headers += ('Attachment ID', 'BlockDeviceMapping UUID')

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in volumes),
        )


class SetServerVolume(command.Command):
    """Update a volume attachment on the server."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            help=_('Server to update volume for (name or ID)'),
        )
        parser.add_argument(
            'volume',
            help=_('Volume to update attachment for (name or ID)'),
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
        volume_client = self.app.client_manager.sdk_connection.volume

        if parsed_args.delete_on_termination is not None:
            if not sdk_utils.supports_microversion(compute_client, '2.85'):
                msg = _(
                    '--os-compute-api-version 2.85 or greater is required to '
                    'support the -delete-on-termination or '
                    '--preserve-on-termination option'
                )
                raise exceptions.CommandError(msg)

            server = compute_client.find_server(
                parsed_args.server,
                ignore_missing=False,
            )
            volume = volume_client.find_volume(
                parsed_args.volume,
                ignore_missing=False,
            )

            compute_client.update_volume_attachment(
                server,
                volume,
                delete_on_termination=parsed_args.delete_on_termination,
            )


# Legacy alias
class UpdateServerVolume(SetServerVolume):
    """DEPRECATED: Use 'server volume set' instead."""
