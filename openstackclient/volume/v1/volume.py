#   Copyright 2012-2013 OpenStack, LLC.
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
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateVolume(show.ShowOne):
    """Create volume command"""

    api = 'volume'
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
            '--user-id',
            metavar='<user-id>',
            help='User id derived from context',
        )
        parser.add_argument(
            '--project-id',
            metavar='<project-id>',
            help='Project id derived from context',
        )
        parser.add_argument(
            '--availability-zone',
            metavar='<availability-zone>',
            help='Availability Zone to use',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            help='Optional property to set on volume creation',
        )
        parser.add_argument(
            '--image-ref',
            metavar='<image-ref>',
            help='reference to an image stored in glance',
        )
        parser.add_argument(
            '--source-volid',
            metavar='<source-volid>',
            help='ID of source volume to clone from',
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        volume_client = self.app.client_manager.volume

        meta = None
        if parsed_args.meta_data:
            meta = dict(v.split('=') for v in parsed_args.meta_data.split(' '))

        volume = volume_client.volumes.create(
            parsed_args.size,
            parsed_args.snapshot_id,
            parsed_args.source_volid,
            parsed_args.name,
            parsed_args.description,
            parsed_args.volume_type,
            parsed_args.user_id,
            parsed_args.project_id,
            parsed_args.availability_zone,
            meta,
            parsed_args.image_ref
        )

        return zip(*sorted(volume._info.iteritems()))


class DeleteVolume(command.Command):
    """Delete volume command"""

    api = 'volume'
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
    """List volume command"""

    api = 'volume'
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
            '--all-tenants',
            action='store_true',
            default=False,
            help='Display information from all tenants (Admin-only)',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Display meta-data',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        columns = ('ID', 'Status', 'Display Name', 'Size',
                   'Volume Type', 'Bootable', 'Attached to')
        if parsed_args.long:
            columns = ('ID', 'Status', 'Display Name', 'Size',
                       'Volume Type', 'Bootable', 'Attached to', 'Meta-data')

        search_opts = {
            'all_tenants': parsed_args.all_tenants,
            'display_name': parsed_args.name,
            'status': parsed_args.status,
        }

        volume_client = self.app.client_manager.volume
        data = volume_client.volumes.list(search_opts=search_opts)

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Meta-data': _format_meta_data},
                ) for s in data))


class SetVolume(command.Command):
    """Set volume command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.SetVolume')

    def get_parser(self, prog_name):
        parser = super(SetVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Name or ID of volume to change')
        parser.add_argument(
            '--name',
            metavar='<new-volume-name>',
            help='New volume name')
        parser.add_argument(
            '--description',
            metavar='<volume-description>',
            help='New volume description')
        parser.add_argument(
            '--meta-data',
            metavar='<key=value>',
            help='meta-data to add to volume')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        meta = None
        if parsed_args.property:
            meta = dict(v.split('=') for v in parsed_args.property.split(' '))
            volume_client.volumes.set_metadata(volume.id, meta)

        kwargs = {}
        if parsed_args.name:
            kwargs['display_name'] = parsed_args.name
        if parsed_args.description:
            kwargs['display_description'] = parsed_args.description

        if not kwargs and not meta:
            sys.stdout.write("Volume not updated, no arguments present \n")
            return
        volume_client.volumes.update(volume.id, **kwargs)
        return


class ShowVolume(show.ShowOne):
    """Show volume command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.ShowVolume')

    def get_parser(self, prog_name):
        parser = super(ShowVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Name or ID of volume to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        return zip(*sorted(volume._info.iteritems()))


class UnsetVolume(command.Command):
    """Unset volume command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.UnsetVolume')

    def get_parser(self, prog_name):
        parser = super(UnsetVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Name or ID of volume to change')
        parser.add_argument(
            '--meta-data',
            metavar='<key>',
            help='meta-data to remove from volume (key only)')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(
            volume_client.volumes, parsed_args.volume)

        if not parsed_args.meta_data:
            sys.stdout.write("Volume not updated, no arguments present \n")
            return

        key_list = []
        key_list.append(parsed_args.meta_data)
        volume_client.volumes.delete_metadata(volume.id, key_list)

        return


def _format_meta_data(volume):
    """Return a string containing the key value pairs

    :param server: a single volume resource
    :rtype: a string formatted to key=value
    """

    keys = volume.metadata
    output = ""
    for s in keys:
        output = output + s + "=" + keys[s] + "; "
    return output
