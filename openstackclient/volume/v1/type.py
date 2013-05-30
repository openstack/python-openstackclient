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

"""Volume v1 Type action implementations"""

import logging

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import parseractions
from openstackclient.common import utils


class CreateVolumeType(show.ShowOne):
    """Create volume type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.CreateVolumeType')

    def get_parser(self, prog_name):
        parser = super(CreateVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New volume type name',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume_type = volume_client.volume_types.create(
            parsed_args.name
        )

        info = {}
        info.update(volume_type._info)
        return zip(*sorted(info.iteritems()))


class DeleteVolumeType(command.Command):
    """Delete volume type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.DeleteVolumeType')

    def get_parser(self, prog_name):
        parser = super(DeleteVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help='Name or ID of volume type to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume_type_id = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type).id
        volume_client.volume_types.delete(volume_type_id)
        return


class ListVolumeType(lister.Lister):
    """List volume type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.ListVolumeType')

    def get_parser(self, prog_name):
        parser = super(ListVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        if parsed_args.long:
            columns = ('ID', 'Name', 'Extra Specs')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.volume.volume_types.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Extra Specs': _format_type_list_extra_specs},
                ) for s in data))


class SetVolumeType(command.Command):
    """Set volume type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.SetVolumeType')

    def get_parser(self, prog_name):
        parser = super(SetVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help='Volume type name or ID to update',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add/change for this volume type '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type)

        if parsed_args.property:
            volume_type.set_keys(parsed_args.property)

        return


class UnsetVolumeType(command.Command):
    """Unset volume type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.UnsetVolumeType')

    def get_parser(self, prog_name):
        parser = super(UnsetVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help='Type ID or name to remove',
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help='Property key to remove from volume '
                 '(repeat option to remove multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types,
            parsed_args.volume_type,
        )

        if parsed_args.property:
            volume_client.volumes.delete_metadata(
                volume_type.id,
                parsed_args.property,
            )
        else:
            self.app.log.error("No changes requested\n")
        return


def _format_type_list_extra_specs(vol_type):
    """Return a string containing the key value pairs

    :param server: a single VolumeType resource
    :rtype: a string formatted to key=value
    """

    keys = vol_type.get_keys()
    output = ""
    for s in keys:
        output = output + s + "=" + keys[s] + "; "
    return output
