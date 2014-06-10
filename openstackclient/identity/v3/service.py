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

"""Identity v3 Service action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils
from openstackclient.identity import common


class CreateService(show.ShowOne):
    """Create new service"""

    log = logging.getLogger(__name__ + '.CreateService')

    def get_parser(self, prog_name):
        parser = super(CreateService, self).get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<service-type>',
            help='New service type (compute, image, identity, volume, etc)',
        )
        parser.add_argument(
            '--name',
            metavar='<service-name>',
            help='New service name',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable project',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable project',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        enabled = True
        if parsed_args.disable:
            enabled = False

        service = identity_client.services.create(
            name=parsed_args.name,
            type=parsed_args.type,
            enabled=enabled,
        )

        return zip(*sorted(six.iteritems(service._info)))


class DeleteService(command.Command):
    """Delete service"""

    log = logging.getLogger(__name__ + '.DeleteService')

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Service to delete (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        service = common.find_service(identity_client, parsed_args.service)

        identity_client.services.delete(service.id)
        return


class ListService(lister.Lister):
    """List services"""

    log = logging.getLogger(__name__ + '.ListService')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        columns = ('ID', 'Name', 'Type', 'Enabled')
        data = self.app.client_manager.identity.services.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetService(command.Command):
    """Set service properties"""

    log = logging.getLogger(__name__ + '.SetService')

    def get_parser(self, prog_name):
        parser = super(SetService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Service to update (name or ID)',
        )
        parser.add_argument(
            '--type',
            metavar='<service-type>',
            help='New service type (compute, image, identity, volume, etc)',
        )
        parser.add_argument(
            '--name',
            metavar='<service-name>',
            help='New service name',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable project',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable project',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if (not parsed_args.name
                and not parsed_args.type
                and not parsed_args.enable
                and not parsed_args.disable):
            return

        service = common.find_service(identity_client, parsed_args.service)

        kwargs = service._info
        if parsed_args.type:
            kwargs['type'] = parsed_args.type
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False
        if 'id' in kwargs:
            del kwargs['id']

        identity_client.services.update(
            service.id,
            **kwargs
        )
        return


class ShowService(show.ShowOne):
    """Show service details"""

    log = logging.getLogger(__name__ + '.ShowService')

    def get_parser(self, prog_name):
        parser = super(ShowService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Service to display (type, name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        service = common.find_service(identity_client, parsed_args.service)

        return zip(*sorted(six.iteritems(service._info)))
