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
            help='Name of the volume',
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            required=True,
            type=int,
            help='New volume size',
        )
        parser.add_argument(
            '--snapshot-id',
            metavar='<snapshot-id>',
            help='ID of the snapshot',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='Description of the volume',
        )
        parser.add_argument(
            '--volume-type',
            metavar='<volume-type>',
            help='Type of volume',
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help='Specify a different user (admin only)',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Specify a different project (admin only)',
        )
        parser.add_argument(
            '--availability-zone',
            metavar='<availability-zone>',
            help='Availability zone to use',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to store for this volume '
                 '(repeat option to set multiple properties)',
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            help='Reference to a stored image',
        )
        parser.add_argument(
            '--source',
            metavar='<volume>',
            help='Source for volume clone',
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        identity_client = self.app.client_manager.identity
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
                identity_client.tenants, parsed_args.project).id

        user = None
        if parsed_args.user:
            user = utils.find_resource(
                identity_client.users, parsed_args.user).id

        volume = volume_client.volumes.create(
            parsed_args.size,
            parsed_args.snapshot_id,
            source_volume,
            parsed_args.name,
            parsed_args.description,
            parsed_args.volume_type,
            user,
            project,
            parsed_args.availability_zone,
            parsed_args.property,
            parsed_args.image
        )
        # Map 'metadata' column to 'properties'
        volume._info.update(
            {'properties': utils.format_dict(volume._info.pop('metadata'))}
        )

        return zip(*sorted(six.iteritems(volume._info)))


class DeleteVolume(command.Command):
    """Delete volume"""

    log = logging.getLogger(__name__ + '.DeleteVolume')

    def get_parser(self, prog_name):
        parser = super(DeleteVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Name or ID of volume to delete',
        )
        parser.add_argument(
            '--force',
            dest='force',
            action='store_true',
            default=False,
            help='Attempt forced removal of a volume, regardless of state',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(
            volume_client.volumes, parsed_args.volume)
        if parsed_args.force:
            volume_client.volumes.force_delete(volume.id)
        else:
            volume_client.volumes.delete(volume.id)
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
            help='Display properties',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        if parsed_args.long:
            columns = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Volume Type',
                'Bootable',
                'Attached to',
                'Metadata',
            )
            column_headers = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Type',
                'Bootable',
                'Attached',
                'Properties',
            )
        else:
            columns = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Attached to',
            )
            column_headers = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Attached',
            )
        search_opts = {
            'all_tenants': parsed_args.all_projects,
            'display_name': parsed_args.name,
            'status': parsed_args.status,
        }

        volume_client = self.app.client_manager.volume
        data = volume_client.volumes.list(search_opts=search_opts)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict},
                ) for s in data))


class SetVolume(command.Command):
    """Set volume properties"""

    log = logging.getLogger(__name__ + '.SetVolume')

    def get_parser(self, prog_name):
        parser = super(SetVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Name or ID of volume to change',
        )
        parser.add_argument(
            '--name',
            metavar='<new-name>',
            help='New volume name',
        )
        parser.add_argument(
            '--description',
            metavar='<new-description>',
            help='New volume description',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add/change for this volume '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        if parsed_args.property:
            volume_client.volumes.set_metadata(volume.id, parsed_args.property)

        kwargs = {}
        if parsed_args.name:
            kwargs['display_name'] = parsed_args.name
        if parsed_args.description:
            kwargs['display_description'] = parsed_args.description
        if kwargs:
            volume_client.volumes.update(volume.id, **kwargs)

        if not kwargs and not parsed_args.property:
            self.app.log.error("No changes requested\n")

        return


class ShowVolume(show.ShowOne):
    """Show specific volume"""

    log = logging.getLogger(__name__ + '.ShowVolume')

    def get_parser(self, prog_name):
        parser = super(ShowVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Name or ID of volume to display',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)
        # Map 'metadata' column to 'properties'
        volume._info.update(
            {'properties': utils.format_dict(volume._info.pop('metadata'))}
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
            help='Name or ID of volume to change',
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help='Property key to remove from volume '
                 '(repeat to set multiple values)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
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
