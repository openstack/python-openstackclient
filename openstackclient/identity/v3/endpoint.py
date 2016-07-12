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

"""Identity v3 Endpoint action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def get_service_name(service):
    if hasattr(service, 'name'):
        return service.name
    else:
        return ''


class CreateEndpoint(command.ShowOne):
    """Create new endpoint"""

    def get_parser(self, prog_name):
        parser = super(CreateEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help=_('Service to be associated with new endpoint (name or ID)'),
        )
        parser.add_argument(
            'interface',
            metavar='<interface>',
            choices=['admin', 'public', 'internal'],
            help=_('New endpoint interface type (admin, public or internal)'),
        )
        parser.add_argument(
            'url',
            metavar='<url>',
            help=_('New endpoint URL'),
        )
        parser.add_argument(
            '--region',
            metavar='<region-id>',
            help=_('New endpoint region ID'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help=_('Enable endpoint (default)'),
        )
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help=_('Disable endpoint'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        service = common.find_service(identity_client, parsed_args.service)

        endpoint = identity_client.endpoints.create(
            service=service.id,
            url=parsed_args.url,
            interface=parsed_args.interface,
            region=parsed_args.region,
            enabled=parsed_args.enabled
        )

        info = {}
        endpoint._info.pop('links')
        info.update(endpoint._info)
        info['service_name'] = get_service_name(service)
        info['service_type'] = service.type
        return zip(*sorted(six.iteritems(info)))


class DeleteEndpoint(command.Command):
    """Delete endpoint(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint-id>',
            nargs='+',
            help=_('Endpoint(s) to delete (ID only)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.endpoint:
            try:
                endpoint_id = utils.find_resource(
                    identity_client.endpoints, i).id
                identity_client.endpoints.delete(endpoint_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete endpoint with "
                          "ID '%(endpoint)s': %(e)s")
                          % {'endpoint': i, 'e': e})

        if result > 0:
            total = len(parsed_args.endpoint)
            msg = (_("%(result)s of %(total)s endpoints failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListEndpoint(command.Lister):
    """List endpoints"""

    def get_parser(self, prog_name):
        parser = super(ListEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            '--service',
            metavar='<service>',
            help=_('Filter by service (name or ID)'),
        )
        parser.add_argument(
            '--interface',
            metavar='<interface>',
            choices=['admin', 'public', 'internal'],
            help=_('Filter by interface type (admin, public or internal)'),
        )
        parser.add_argument(
            '--region',
            metavar='<region-id>',
            help=_('Filter by region ID'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        columns = ('ID', 'Region', 'Service Name', 'Service Type',
                   'Enabled', 'Interface', 'URL')
        kwargs = {}
        if parsed_args.service:
            service = common.find_service(identity_client, parsed_args.service)
            kwargs['service'] = service.id
        if parsed_args.interface:
            kwargs['interface'] = parsed_args.interface
        if parsed_args.region:
            kwargs['region'] = parsed_args.region
        data = identity_client.endpoints.list(**kwargs)

        for ep in data:
            service = common.find_service(identity_client, ep.service_id)
            ep.service_name = get_service_name(service)
            ep.service_type = service.type
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetEndpoint(command.Command):
    """Set endpoint properties"""

    def get_parser(self, prog_name):
        parser = super(SetEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint-id>',
            help=_('Endpoint to modify (ID only)'),
        )
        parser.add_argument(
            '--region',
            metavar='<region-id>',
            help=_('New endpoint region ID'),
        )
        parser.add_argument(
            '--interface',
            metavar='<interface>',
            choices=['admin', 'public', 'internal'],
            help=_('New endpoint interface type (admin, public or internal)'),
        )
        parser.add_argument(
            '--url',
            metavar='<url>',
            help=_('New endpoint URL'),
        )
        parser.add_argument(
            '--service',
            metavar='<service>',
            help=_('New endpoint service (name or ID)'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            help=_('Enable endpoint'),
        )
        enable_group.add_argument(
            '--disable',
            dest='disabled',
            action='store_true',
            help=_('Disable endpoint'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        endpoint = utils.find_resource(identity_client.endpoints,
                                       parsed_args.endpoint)

        service_id = None
        if parsed_args.service:
            service = common.find_service(identity_client, parsed_args.service)
            service_id = service.id
        enabled = None
        if parsed_args.enabled:
            enabled = True
        if parsed_args.disabled:
            enabled = False

        identity_client.endpoints.update(
            endpoint.id,
            service=service_id,
            url=parsed_args.url,
            interface=parsed_args.interface,
            region=parsed_args.region,
            enabled=enabled
        )


class ShowEndpoint(command.ShowOne):
    """Display endpoint details"""

    def get_parser(self, prog_name):
        parser = super(ShowEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint>',
            help=_('Endpoint to display (endpoint ID, service ID,'
                   ' service name, service type)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        endpoint = utils.find_resource(identity_client.endpoints,
                                       parsed_args.endpoint)

        service = common.find_service(identity_client, endpoint.service_id)

        info = {}
        endpoint._info.pop('links')
        info.update(endpoint._info)
        info['service_name'] = get_service_name(service)
        info['service_type'] = service.type
        return zip(*sorted(six.iteritems(info)))
