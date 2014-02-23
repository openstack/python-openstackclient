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

"""Service action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from keystoneclient import exceptions as identity_exc
from openstackclient.common import exceptions
from openstackclient.common import utils


class CreateService(show.ShowOne):
    """Create new service"""

    log = logging.getLogger(__name__ + '.CreateService')

    def get_parser(self, prog_name):
        parser = super(CreateService, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<service-name>',
            help='New service name',
        )
        parser.add_argument(
            '--type',
            metavar='<service-type>',
            required=True,
            help='New service type (compute, image, identity, volume, etc)',
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
            parsed_args.description)

        info = {}
        info.update(service._info)
        return zip(*sorted(six.iteritems(info)))


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
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        service = utils.find_resource(
            identity_client.services,
            parsed_args.service,
        )

        identity_client.services.delete(service.id)
        return


class ListService(lister.Lister):
    """List services"""

    log = logging.getLogger(__name__ + '.ListService')

    def get_parser(self, prog_name):
        parser = super(ListService, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output')
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
                ) for s in data))


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
        parser.add_argument(
            '--catalog',
            action='store_true',
            default=False,
            help='Show service catalog information',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.catalog:
            endpoints = identity_client.service_catalog.get_endpoints(
                service_type=parsed_args.service)
            for (service, service_endpoints) in six.iteritems(endpoints):
                if service_endpoints:
                    info = {"type": service}
                    info.update(service_endpoints[0])
                    return zip(*sorted(six.iteritems(info)))

            msg = ("No service catalog with a type, name or ID of '%s' "
                   "exists." % (parsed_args.service))
            raise exceptions.CommandError(msg)
        else:
            try:
                # search for the usual ID or name
                service = utils.find_resource(
                    identity_client.services,
                    parsed_args.service,
                )
            except exceptions.CommandError:
                try:
                    # search for service type
                    service = identity_client.services.find(
                        type=parsed_args.service)
                # FIXME(dtroyer): This exception should eventually come from
                #                 common client exceptions
                except identity_exc.NotFound:
                    msg = ("No service with a type, name or ID of '%s' exists."
                           % parsed_args.service)
                    raise exceptions.CommandError(msg)

            info = {}
            info.update(service._info)
            return zip(*sorted(six.iteritems(info)))
