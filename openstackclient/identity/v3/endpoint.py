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
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateEndpoint(show.ShowOne):
    """Create endpoint command"""

    log = logging.getLogger(__name__ + '.CreateEndpoint')

    def get_parser(self, prog_name):
        parser = super(CreateEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Name or ID of new endpoint service')
        parser.add_argument(
            'interface',
            metavar='<interface>',
            choices=['admin', 'public', 'internal'],
            help='New endpoint interface, must be admin, public or internal')
        parser.add_argument(
            'url',
            metavar='<url>',
            help='New endpoint URL')
        parser.add_argument(
            '--region',
            metavar='<region>',
            help='New endpoint region')
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable user',
        )
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable user',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        service = utils.find_resource(identity_client.services,
                                      parsed_args.service)

        endpoint = identity_client.endpoints.create(
            service.id,
            parsed_args.url,
            parsed_args.interface,
            parsed_args.region,
            parsed_args.enabled
        )

        info = {}
        info.update(endpoint._info)
        info['service_name'] = service.name
        info['service_type'] = service.type
        return zip(*sorted(six.iteritems(info)))


class DeleteEndpoint(command.Command):
    """Delete endpoint command"""

    log = logging.getLogger(__name__ + '.DeleteEndpoint')

    def get_parser(self, prog_name):
        parser = super(DeleteEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint>',
            help='ID of endpoint to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        endpoint_id = utils.find_resource(identity_client.endpoints,
                                          parsed_args.endpoint).id
        identity_client.endpoints.delete(endpoint_id)
        return


class ListEndpoint(lister.Lister):
    """List endpoint command"""

    log = logging.getLogger(__name__ + '.ListEndpoint')

    def get_parser(self, prog_name):
        parser = super(ListEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        if parsed_args.long:
            columns = ('ID', 'Region', 'Service Name', 'Service Type',
                       'Enabled', 'Interface', 'URL')
        else:
            columns = ('ID', 'Region', 'Service Name', 'Enabled')
        data = identity_client.endpoints.list()

        for ep in data:
            service = utils.find_resource(
                identity_client.services, ep.service_id)
            ep.service_name = service.name
            ep.service_type = service.type
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetEndpoint(command.Command):
    """Set endpoint command"""

    log = logging.getLogger(__name__ + '.SetEndpoint')

    def get_parser(self, prog_name):
        parser = super(SetEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint>',
            help='ID of endpoint to update')
        parser.add_argument(
            '--interface',
            metavar='<interface>',
            choices=['admin', 'public', 'internal'],
            help='New endpoint interface, must be admin|public|internal')
        parser.add_argument(
            '--url',
            metavar='<url>',
            help='New endpoint URL')
        parser.add_argument(
            '--service',
            metavar='<service>',
            help='Name or ID of new endpoint service')
        parser.add_argument(
            '--region',
            metavar='<region>',
            help='New endpoint region')
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable user',
        )
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable user',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        endpoint = utils.find_resource(identity_client.endpoints,
                                       parsed_args.endpoint)
        service = utils.find_resource(identity_client.services,
                                      parsed_args.service)

        if (not parsed_args.interface and not parsed_args.url
                and not parsed_args.service and not parsed_args.region):
            sys.stdout.write("Endpoint not updated, no arguments present")
            return

        identity_client.endpoints.update(
            endpoint.id,
            service.id,
            parsed_args.url,
            parsed_args.interface,
            parsed_args.region,
            parsed_args.enabled
        )

        return


class ShowEndpoint(show.ShowOne):
    """Show endpoint command"""

    log = logging.getLogger(__name__ + '.ShowEndpoint')

    def get_parser(self, prog_name):
        parser = super(ShowEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint>',
            help='ID of endpoint to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        endpoint = utils.find_resource(identity_client.endpoints,
                                       parsed_args.endpoint)

        service = utils.find_resource(identity_client.services,
                                      endpoint.service_id)

        info = {}
        info.update(endpoint._info)
        info['service_name'] = service.name
        info['service_type'] = service.type
        return zip(*sorted(six.iteritems(info)))
