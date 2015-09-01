#   Copyright 2012-2013 OpenStack Foundation
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

"""Volume v1 Volume action implementations"""

import argparse
import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import parseractions
from openstackclient.common import utils


class CreateVolume(show.ShowOne):
    """Create new volume"""

    log = logging.getLogger(__name__ + '.CreateVolume')

    def get_parser(self, prog_name):
        parser = super(CreateVolume, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New volume name',
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            required=True,
            type=int,
            help='New volume size in GB',
        )
        snapshot_group = parser.add_mutually_exclusive_group()
        snapshot_group.add_argument(
            '--snapshot',
            metavar='<snapshot>',
            help='Use <snapshot> as source of new volume',
        )
        snapshot_group.add_argument(
            '--snapshot-id',
            metavar='<snapshot-id>',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New volume description',
        )
        parser.add_argument(
            '--type',
            metavar='<volume-type>',
            help='Use <volume-type> as the new volume type',
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help='Specify an alternate user (name or ID)',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Specify an alternate project (name or ID)',
        )
        parser.add_argument(
            '--availability-zone',
            metavar='<availability-zone>',
            help='Create new volume in <availability-zone>',
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            help='Use <image> as source of new volume (name or ID)',
        )
        parser.add_argument(
            '--source',
            metavar='<volume>',
            help='Volume to clone (name or ID)',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Set a property on this volume '
                 '(repeat option to set multiple properties)',
        )

        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image
        volume_client = self.app.client_manager.volume

        source_volume = None
        if parsed_args.source:
            source_volume = utils.find_resource(
                volume_client.volumes,
                parsed_args.source,
            ).id

        project = None
        if parsed_args.project:
            project = utils.find_resource(
                identity_client.tenants,
                parsed_args.project,
            ).id

        user = None
        if parsed_args.user:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            ).id

        image = None
        if parsed_args.image:
            image = utils.find_resource(
                image_client.images,
                parsed_args.image,
            ).id

        snapshot = parsed_args.snapshot or parsed_args.snapshot_id

        volume = volume_client.volumes.create(
            parsed_args.size,
            snapshot,
            source_volume,
            parsed_args.name,
            parsed_args.description,
            parsed_args.type,
            user,
            project,
            parsed_args.availability_zone,
            parsed_args.property,
            image,
        )
        # Map 'metadata' column to 'properties'
        volume._info.update(
            {
                'properties': utils.format_dict(volume._info.pop('metadata')),
                'type': volume._info.pop('volume_type'),
            },
        )

        return zip(*sorted(six.iteritems(volume._info)))


class DeleteVolume(command.Command):
    """Delete volume(s)"""

    log = logging.getLogger(__name__ + '.DeleteVolume')

    def get_parser(self, prog_name):
        parser = super(DeleteVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volumes',
            metavar='<volume>',
            nargs="+",
            help='Volume(s) to delete (name or ID)',
        )
        parser.add_argument(
            '--force',
            dest='force',
            action='store_true',
            default=False,
            help='Attempt forced removal of volume(s), regardless of state '
                 '(defaults to False)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        for volume in parsed_args.volumes:
            volume_obj = utils.find_resource(
                volume_client.volumes, volume)
            if parsed_args.force:
                volume_client.volumes.force_delete(volume_obj.id)
            else:
                volume_client.volumes.delete(volume_obj.id)
        return


class ListVolume(lister.Lister):
    """List volumes"""

    log = logging.getLogger(__name__ + '.ListVolume')

    def get_parser(self, prog_name):
        parser = super(ListVolume, self).get_parser(prog_name)
        parser.add_argument(
            '--status',
            metavar='<status>',
            help='Filter results by status',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Filter results by name',
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help='Include all projects (admin only)',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        volume_client = self.app.client_manager.volume
        compute_client = self.app.client_manager.compute

        def _format_attach(attachments):
            """Return a formatted string of a volume's attached instances

            :param volume: a volume.attachments field
            :rtype: a string of formatted instances
            """

            msg = ''
            for attachment in attachments:
                server = attachment['server_id']
                if server in server_cache.keys():
                    server = server_cache[server].name
                device = attachment['device']
                msg += 'Attached to %s on %s ' % (server, device)
            return msg

        if parsed_args.long:
            columns = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Volume Type',
                'Bootable',
                'Attachments',
                'Metadata',
            )
            column_headers = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Type',
                'Bootable',
                'Attached to',
                'Properties',
            )
        else:
            columns = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Attachments',
            )
            column_headers = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Attached to',
            )

        # Cache the server list
        server_cache = {}
        try:
            for s in compute_client.servers.list():
                server_cache[s.id] = s
        except Exception:
            # Just forget it if there's any trouble
            pass

        search_opts = {
            'all_tenants': parsed_args.all_projects,
            'display_name': parsed_args.name,
            'status': parsed_args.status,
        }

        data = volume_client.volumes.list(search_opts=search_opts)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict,
                                'Attachments': _format_attach},
                ) for s in data))


class SetVolume(command.Command):
    """Set volume properties"""

    log = logging.getLogger(__name__ + '.SetVolume')

    def get_parser(self, prog_name):
        parser = super(SetVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Volume to change (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='New volume name',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New volume description',
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            type=int,
            help='Extend volume size in GB',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add or modify for this volume '
                 '(repeat option to set multiple properties)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        if parsed_args.size:
            if volume.status != 'available':
                self.app.log.error("Volume is in %s state, it must be "
                                   "available before size can be extended" %
                                   volume.status)
                return
            if parsed_args.size <= volume.size:
                self.app.log.error("New size must be greater than %s GB" %
                                   volume.size)
                return
            volume_client.volumes.extend(volume.id, parsed_args.size)

        if parsed_args.property:
            volume_client.volumes.set_metadata(volume.id, parsed_args.property)

        kwargs = {}
        if parsed_args.name:
            kwargs['display_name'] = parsed_args.name
        if parsed_args.description:
            kwargs['display_description'] = parsed_args.description
        if kwargs:
            volume_client.volumes.update(volume.id, **kwargs)

        if not kwargs and not parsed_args.property and not parsed_args.size:
            self.app.log.error("No changes requested\n")

        return


class ShowVolume(show.ShowOne):
    """Show volume details"""

    log = logging.getLogger(__name__ + '.ShowVolume')

    def get_parser(self, prog_name):
        parser = super(ShowVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Volume to display (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)
        # Map 'metadata' column to 'properties'
        volume._info.update(
            {
                'properties': utils.format_dict(volume._info.pop('metadata')),
                'type': volume._info.pop('volume_type'),
            },
        )
        if 'os-vol-tenant-attr:tenant_id' in volume._info:
            volume._info.update(
                {'project_id': volume._info.pop(
                    'os-vol-tenant-attr:tenant_id')}
            )
        return zip(*sorted(six.iteritems(volume._info)))


class UnsetVolume(command.Command):
    """Unset volume properties"""

    log = logging.getLogger(__name__ + '.UnsetVolume')

    def get_parser(self, prog_name):
        parser = super(UnsetVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Volume to modify (name or ID)',
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help='Property to remove from volume '
                 '(repeat option to remove multiple properties)',
            required=True,
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(
            volume_client.volumes, parsed_args.volume)

        if parsed_args.property:
            volume_client.volumes.delete_metadata(
                volume.id,
                parsed_args.property,
            )
        else:
            self.app.log.error("No changes requested\n")
        return
