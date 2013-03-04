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

from openstackclient.common import utils


class CreateType(show.ShowOne):
    """Create type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.CreateType')

    def get_parser(self, prog_name):
        parser = super(CreateType, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New type name',
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


class DeleteType(command.Command):
    """Delete type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.DeleteType')

    def get_parser(self, prog_name):
        parser = super(DeleteType, self).get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<type>',
            help='Name or ID of type to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.type)
        volume_client.volume_types.delete(volume_type.id)
        return


class ListType(lister.Lister):
    """List type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.ListType')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        columns = ('ID', 'Name')
        data = self.app.client_manager.volume.volume_types.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetType(command.Command):
    """Set type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.SetType')

    def get_parser(self, prog_name):
        parser = super(SetType, self).get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<type>',
            help='Type ID to update',
        )
        parser.add_argument(
            'meta_data',
            metavar='<key=value>',
            help='meta-data to add to volume type',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        meta = dict(v.split('=') for v in parsed_args.meta_data.split(' '))
        volume_client = self.app.client_manager.volume
        volume_type = volume_client.volume_types.get(
            parsed_args.type
        )

        volume_type.set_keys(meta)

        return


class UnsetType(command.Command):
    """Unset type command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.UnsetType')

    def get_parser(self, prog_name):
        parser = super(UnsetType, self).get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<type>',
            help='Type ID to update',
        )
        parser.add_argument(
            'meta_data',
            metavar='<key>',
            help='meta-data to remove from volume type (key only)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume_type = volume_client.volume_types.get(
            parsed_args.type
        )
        key_list = []
        key_list.append(parsed_args.meta_data)
        volume_type.unset_keys(key_list)

        return
