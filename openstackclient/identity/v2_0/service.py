# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
Service action implementations
"""

import logging

from cliff import command
from cliff import lister
from cliff import show

from keystoneclient import exceptions as identity_exc
from openstackclient.common import exceptions
from openstackclient.common import utils


class CreateService(show.ShowOne):
    """Create service command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.CreateService')

    def get_parser(self, prog_name):
        parser = super(CreateService, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<service-name>',
            help='New service name')
        parser.add_argument(
            '--type',
            metavar='<service-type>',
            required=True,
            help='New service type',
        )
        parser.add_argument(
            '--description',
            metavar='<service-description>',
            help='New service description',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        service = identity_client.services.create(
            parsed_args.name,
            parsed_args.type,
            parsed_args.description,
        )

        info = {}
        info.update(service._info)
        return zip(*sorted(info.iteritems()))


class DeleteService(command.Command):
    """Delete service command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.DeleteService')

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service-id>',
            help='ID of service to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        identity_client.services.delete(parsed_args.service)
        return


class ListService(lister.Lister):
    """List service command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ListService')

    def get_parser(self, prog_name):
        parser = super(ListService, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        if parsed_args.long:
            columns = ('ID', 'Name', 'Type', 'Description')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.identity.services.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data),
               )


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
        try:
            # search for the usual ID or name
            service = utils.find_resource(
                identity_client.services, parsed_args.service)
        except exceptions.CommandError:
            try:
                # search for service type
                service = identity_client.services.find(
                    type=parsed_args.service)
            # FIXME(dtroyer): This exception should eventually come from
            #                 common client exceptions
            except identity_exc.NotFound:
                msg = "No service with a type, name or ID of '%s' exists." % \
                    name_or_id
                raise exceptions.CommandError(msg)

        info = {}
        info.update(service._info)
        return zip(*sorted(info.iteritems()))
