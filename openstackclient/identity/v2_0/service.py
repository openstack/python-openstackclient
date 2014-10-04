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

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.i18n import _  # noqa
from openstackclient.identity import common


class CreateService(show.ShowOne):
    """Create new service"""

    log = logging.getLogger(__name__ + '.CreateService')

    def get_parser(self, prog_name):
        parser = super(CreateService, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<service-name>',
            help=_('New service name'),
        )
        parser.add_argument(
            '--type',
            metavar='<service-type>',
            required=True,
            help=_('New service type (compute, image, identity, volume, etc)'),
        )
        parser.add_argument(
            '--description',
            metavar='<service-description>',
            help=_('New service description'),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
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
            help=_('Service to delete (name or ID)'),
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

    def get_parser(self, prog_name):
        parser = super(ListService, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'))
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

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
            help=_('Service to display (type, name or ID)'),
        )
        parser.add_argument(
            '--catalog',
            action='store_true',
            default=False,
            help=_('Show service catalog information'),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.catalog:
            endpoints = identity_client.service_catalog.get_endpoints(
                service_type=parsed_args.service)
            for (service, service_endpoints) in six.iteritems(endpoints):
                if service_endpoints:
                    info = {"type": service}
                    info.update(service_endpoints[0])
                    return zip(*sorted(six.iteritems(info)))

            msg = _("No service catalog with a type, name or ID of '%s' "
                    "exists.") % (parsed_args.service)
            raise exceptions.CommandError(msg)
        else:
            service = common.find_service(identity_client, parsed_args.service)
            info = {}
            info.update(service._info)
            return zip(*sorted(six.iteritems(info)))
