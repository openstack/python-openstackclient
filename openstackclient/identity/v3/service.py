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

"""Identity v3 Service action implementations"""

import logging
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateService(show.ShowOne):
    """Create service command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.CreateService')

    def get_parser(self, prog_name):
        parser = super(CreateService, self).get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<service-type>',
            help='New service type (compute, image, identity, volume, etc)')
        parser.add_argument(
            '--name',
            metavar='<service-name>',
            help='New service name')
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable user')
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable user')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        service = identity_client.services.create(
            parsed_args.name,
            parsed_args.type,
            parsed_args.enabled)

        return zip(*sorted(service._info.iteritems()))


class DeleteService(command.Command):
    """Delete service command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.DeleteService')

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Name or ID of service to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        service_id = utils.find_resource(
            identity_client.services, parsed_args.service).id

        identity_client.services.delete(service_id)
        return


class ListService(lister.Lister):
    """List service command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ListService')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        columns = ('ID', 'Name', 'Type', 'Enabled')
        data = self.app.client_manager.identity.services.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetService(show.ShowOne):
    """Set service command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.SetService')

    def get_parser(self, prog_name):
        parser = super(SetService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Service name or ID to update')
        parser.add_argument(
            '--type',
            metavar='<service-type>',
            help='New service type (compute, image, identity, volume, etc)')
        parser.add_argument(
            '--name',
            metavar='<service-name>',
            help='New service name')
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable user')
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable user')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        service = utils.find_resource(identity_client.services,
                                      parsed_args.service)

        if not parsed_args.name and not parsed_args.type:
            sys.stdout.write("Service not updated, no arguments present")
            return

        identity_client.services.update(
            service,
            parsed_args.name,
            parsed_args.type,
            parsed_args.enabled)

        return


class ShowService(show.ShowOne):
    """Show service command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ShowService')

    def get_parser(self, prog_name):
        parser = super(ShowService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Type, name or ID of service to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        service = utils.find_resource(identity_client.services,
                                      parsed_args.service)

        return zip(*sorted(service._info.iteritems()))
