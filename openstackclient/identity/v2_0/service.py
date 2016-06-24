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

import argparse
import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class CreateService(command.ShowOne):
    """Create new service"""

    def get_parser(self, prog_name):
        parser = super(CreateService, self).get_parser(prog_name)
        parser.add_argument(
            'type_or_name',
            metavar='<type>',
            help=_('New service type (compute, image, identity, volume, etc)'),
        )
        type_or_name_group = parser.add_mutually_exclusive_group()
        type_or_name_group.add_argument(
            '--type',
            metavar='<type>',
            help=argparse.SUPPRESS,
        )
        type_or_name_group.add_argument(
            '--name',
            metavar='<name>',
            help=_('New service name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New service description'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        type_or_name = parsed_args.type_or_name
        name = parsed_args.name
        type = parsed_args.type

        # If only a single positional is present, it's a <type>.
        # This is not currently legal so it is considered a new case.
        if not type and not name:
            type = type_or_name
        # If --type option is present then positional is handled as <name>;
        # display deprecation message.
        elif type:
            name = type_or_name
            LOG.warning(_('The argument --type is deprecated, use service'
                          ' create --name <service-name> type instead.'))
        # If --name option is present the positional is handled as <type>.
        # Making --type optional is new, but back-compatible
        elif name:
            type = type_or_name

        service = identity_client.services.create(
            name,
            type,
            parsed_args.description)

        info = {}
        info.update(service._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteService(command.Command):
    """Delete service(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument(
            'services',
            metavar='<service>',
            nargs='+',
            help=_('Service(s) to delete (type, name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        result = 0
        for service in parsed_args.services:
            try:
                service = common.find_service(identity_client, service)
                identity_client.services.delete(service.id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete service with "
                          "name or ID '%(service)s': %(e)s")
                          % {'service': service, 'e': e})

        if result > 0:
            total = len(parsed_args.services)
            msg = (_("%(result)s of %(total)s services failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListService(command.Lister):
    """List services"""

    def get_parser(self, prog_name):
        parser = super(ListService, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):

        if parsed_args.long:
            columns = ('ID', 'Name', 'Type', 'Description')
        else:
            columns = ('ID', 'Name', 'Type')
        data = self.app.client_manager.identity.services.list()
        return (
            columns,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowService(command.ShowOne):
    """Display service details"""

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
        identity_client = self.app.client_manager.identity
        auth_ref = self.app.client_manager.auth_ref

        if parsed_args.catalog:
            endpoints = auth_ref.service_catalog.get_endpoints(
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
