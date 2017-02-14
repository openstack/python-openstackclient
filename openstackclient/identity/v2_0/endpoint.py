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

"""Endpoint action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class CreateEndpoint(command.ShowOne):
    _description = _("Create new endpoint")

    def get_parser(self, prog_name):
        parser = super(CreateEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help=_('Service to be associated with new endpoint (name or ID)'),
        )
        parser.add_argument(
            '--publicurl',
            metavar='<url>',
            required=True,
            help=_('New endpoint public URL (required)'),
        )
        parser.add_argument(
            '--adminurl',
            metavar='<url>',
            help=_('New endpoint admin URL'),
        )
        parser.add_argument(
            '--internalurl',
            metavar='<url>',
            help=_('New endpoint internal URL'),
        )
        parser.add_argument(
            '--region',
            metavar='<region-id>',
            help=_('New endpoint region ID'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        service = common.find_service(identity_client, parsed_args.service)
        endpoint = identity_client.endpoints.create(
            parsed_args.region,
            service.id,
            parsed_args.publicurl,
            parsed_args.adminurl,
            parsed_args.internalurl,)

        info = {}
        info.update(endpoint._info)
        info['service_name'] = service.name
        info['service_type'] = service.type
        return zip(*sorted(six.iteritems(info)))


class DeleteEndpoint(command.Command):
    _description = _("Delete endpoint(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoints',
            metavar='<endpoint-id>',
            nargs='+',
            help=_('Endpoint(s) to delete (ID only)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        result = 0
        for endpoint in parsed_args.endpoints:
            try:
                identity_client.endpoints.delete(endpoint)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete endpoint with "
                          "ID '%(endpoint)s': %(e)s"),
                          {'endpoint': endpoint, 'e': e})

        if result > 0:
            total = len(parsed_args.endpoints)
            msg = (_("%(result)s of %(total)s endpoints failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListEndpoint(command.Lister):
    _description = _("List endpoints")

    def get_parser(self, prog_name):
        parser = super(ListEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        if parsed_args.long:
            columns = ('ID', 'Region', 'Service Name', 'Service Type',
                       'PublicURL', 'AdminURL', 'InternalURL')
        else:
            columns = ('ID', 'Region', 'Service Name', 'Service Type')
        data = identity_client.endpoints.list()

        for ep in data:
            service = common.find_service(identity_client, ep.service_id)
            ep.service_name = service.name
            ep.service_type = service.type
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ShowEndpoint(command.ShowOne):
    _description = _("Display endpoint details")

    def get_parser(self, prog_name):
        parser = super(ShowEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint_or_service',
            metavar='<endpoint>',
            help=_('Endpoint to display (endpoint ID, service ID,'
                   ' service name, service type)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        data = identity_client.endpoints.list()
        match = None
        for ep in data:
            if ep.id == parsed_args.endpoint_or_service:
                match = ep
                service = common.find_service(identity_client, ep.service_id)
        if match is None:
            service = common.find_service(identity_client,
                                          parsed_args.endpoint_or_service)
            for ep in data:
                if ep.service_id == service.id:
                    match = ep
        if match is None:
            return None
        info = {}
        info.update(match._info)
        info['service_name'] = service.name
        info['service_type'] = service.type
        return zip(*sorted(six.iteritems(info)))
