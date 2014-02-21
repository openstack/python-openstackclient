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
import six

from cliff import command
from cliff import lister
from cliff import show

from keystoneclient import exceptions as identity_exc
from openstackclient.common import exceptions
from openstackclient.common import utils


class CreateEndpoint(show.ShowOne):
    """Create endpoint command"""

    log = logging.getLogger(__name__ + '.CreateEndpoint')

    def get_parser(self, prog_name):
        parser = super(CreateEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<endpoint-service>',
            help='New endpoint service')
        parser.add_argument(
            '--region',
            metavar='<region>',
            help='New endpoint region')
        parser.add_argument(
            '--publicurl',
            metavar='<public-url>',
            help='New endpoint public URL')
        parser.add_argument(
            '--adminurl',
            metavar='<admin-url>',
            help='New endpoint admin URL')
        parser.add_argument(
            '--internalurl',
            metavar='<internal-url>',
            help='New endpoint internal URL')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        service = utils.find_resource(identity_client.services,
                                      parsed_args.service)
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
    """Delete endpoint command"""

    log = logging.getLogger(__name__ + '.DeleteEndpoint')

    def get_parser(self, prog_name):
        parser = super(DeleteEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint-id>',
            help='ID of endpoint to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        identity_client.endpoints.delete(parsed_args.endpoint)
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
                       'PublicURL', 'AdminURL', 'InternalURL')
        else:
            columns = ('ID', 'Region', 'Service Name', 'Service Type')
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


class ShowEndpoint(show.ShowOne):
    """Show endpoint command"""

    log = logging.getLogger(__name__ + '.ShowEndpoint')

    def get_parser(self, prog_name):
        parser = super(ShowEndpoint, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Name or ID of service endpoint to display')
        parser.add_argument(
            '--type',
            metavar='<endpoint-type>',
            default='publicURL',
            help='Endpoint type: publicURL, internalURL, adminURL ' +
                 '(default publicURL)')
        parser.add_argument(
            '--attr',
            metavar='<endpoint-attribute>',
            help='Endpoint attribute to use for selection')
        parser.add_argument(
            '--value',
            metavar='<endpoint-value>',
            help='Value of endpoint attribute to use for selection')
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='Show all endpoints for this service')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if not parsed_args.all:
            # Find endpoint filtered by a specific attribute or service type
            kwargs = {
                'service_type': parsed_args.service,
                'endpoint_type': parsed_args.type,
            }
            if parsed_args.attr and parsed_args.value:
                kwargs.update({
                    'attr': parsed_args.attr,
                    'filter_value': parsed_args.value,
                })
            elif parsed_args.attr or parsed_args.value:
                msg = 'Both --attr and --value required'
                raise exceptions.CommandError(msg)

            url = identity_client.service_catalog.url_for(**kwargs)
            info = {'%s.%s' % (parsed_args.service, parsed_args.type): url}
            return zip(*sorted(six.iteritems(info)))
        else:
            # The Identity 2.0 API doesn't support retrieving a single
            # endpoint so we have to do this ourselves
            try:
                service = utils.find_resource(identity_client.services,
                                              parsed_args.service)
            except exceptions.CommandError:
                try:
                    # search for service type
                    service = identity_client.services.find(
                        type=parsed_args.service)
                # FIXME(dtroyer): This exception should eventually come from
                #                 common client exceptions
                except identity_exc.NotFound:
                    msg = "No service with a type, name or ID of '%s' exists" \
                        % parsed_args.service
                    raise exceptions.CommandError(msg)

            data = identity_client.endpoints.list()
            for ep in data:
                if ep.service_id == service.id:
                    info = {}
                    info.update(ep._info)
                    service = utils.find_resource(identity_client.services,
                                                  ep.service_id)
                    info['service_name'] = service.name
                    info['service_type'] = service.type
                    return zip(*sorted(six.iteritems(info)))
