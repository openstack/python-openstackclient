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

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_endpoint(endpoint, service):
    columns = (
        'is_enabled',
        'id',
        'interface',
        'region_id',
        'region_id',
        'service_id',
        'url',
    )
    column_headers = (
        'enabled',
        'id',
        'interface',
        'region',
        'region_id',
        'service_id',
        'url',
        'service_name',
        'service_type',
    )

    data = utils.get_item_properties(endpoint, columns)
    data += (getattr(service, 'name', ''), service.type)
    return column_headers, data


class AddProjectToEndpoint(command.Command):
    _description = _("Associate a project to an endpoint")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint>',
            help=_(
                'Endpoint to associate with specified project (name or ID)'
            ),
        )
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Project to associate with specified endpoint name or ID)'),
        )
        common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.identity

        endpoint = utils.find_resource(client.endpoints, parsed_args.endpoint)

        project = common.find_project(
            client, parsed_args.project, parsed_args.project_domain
        )

        client.endpoint_filter.add_endpoint_to_project(
            project=project.id, endpoint=endpoint.id
        )


class CreateEndpoint(command.ShowOne):
    _description = _("Create new endpoint")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity
        service = common.find_service_sdk(identity_client, parsed_args.service)

        kwargs = {}

        kwargs['service_id'] = service.id
        kwargs['url'] = parsed_args.url
        kwargs['interface'] = parsed_args.interface
        kwargs['is_enabled'] = parsed_args.enabled

        if parsed_args.region:
            region = identity_client.get_region(parsed_args.region)
            kwargs['region_id'] = region.id

        endpoint = identity_client.create_endpoint(**kwargs)

        return _format_endpoint(endpoint, service=service)


class DeleteEndpoint(command.Command):
    _description = _("Delete endpoint(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint-id>',
            nargs='+',
            help=_('Endpoint(s) to delete (ID only)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        result = 0
        for i in parsed_args.endpoint:
            try:
                endpoint_id = identity_client.find_endpoint(i).id
                identity_client.delete_endpoint(endpoint_id)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete endpoint with "
                        "ID '%(endpoint)s': %(e)s"
                    ),
                    {'endpoint': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.endpoint)
            msg = _("%(result)s of %(total)s endpoints failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListEndpoint(command.Lister):
    _description = _("List endpoints")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--service',
            metavar='<service>',
            help=_('Filter by service (type, name or ID)'),
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
        list_group = parser.add_mutually_exclusive_group()
        list_group.add_argument(
            '--endpoint',
            metavar='<endpoint-group>',
            help=_('Endpoint to list filters'),
        )
        list_group.add_argument(
            '--project',
            metavar='<project>',
            help=_('Project to list filters (name or ID)'),
        )
        common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        endpoint = None
        if parsed_args.endpoint:
            endpoint = identity_client.find_endpoint(parsed_args.endpoint)
        project = None
        if parsed_args.project:
            project = identity_client.find_project(
                parsed_args.project,
                parsed_args.project_domain,
            )

        if endpoint:
            column_headers: tuple[str, ...] = ('ID', 'Name')
            columns: tuple[str, ...] = ('id', 'name')
            data = identity_client.endpoint_projects(endpoint=endpoint.id)
        else:
            column_headers = (
                'ID',
                'Region',
                'Service Name',
                'Service Type',
                'Enabled',
                'Interface',
                'URL',
            )
            columns = (
                'id',
                'region_id',
                'service_name',
                'service_type',
                'is_enabled',
                'interface',
                'url',
            )
            kwargs = {}
            if parsed_args.service:
                service = common.find_service_sdk(
                    identity_client, parsed_args.service
                )
                kwargs['service_id'] = service.id
            if parsed_args.interface:
                kwargs['interface'] = parsed_args.interface
            if parsed_args.region:
                region = identity_client.get_region(parsed_args.region)
                kwargs['region_id'] = region.id

            if project:
                data = list(
                    identity_client.project_endpoints(project=project.id)
                )
            else:
                data = list(identity_client.endpoints(**kwargs))

            for ep in data:
                service = identity_client.find_service(ep.service_id)
                ep.service_name = getattr(service, 'name', '')
                ep.service_type = service.type

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class RemoveProjectFromEndpoint(command.Command):
    _description = _("Dissociate a project from an endpoint")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint>',
            help=_(
                'Endpoint to dissociate from specified project (name or ID)'
            ),
        )
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_(
                'Project to dissociate from specified endpoint name or ID)'
            ),
        )
        common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.identity

        endpoint = utils.find_resource(client.endpoints, parsed_args.endpoint)

        project = common.find_project(
            client, parsed_args.project, parsed_args.project_domain
        )

        client.endpoint_filter.delete_endpoint_from_project(
            project=project.id, endpoint=endpoint.id
        )


class SetEndpoint(command.Command):
    _description = _("Set endpoint properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity
        endpoint = identity_client.find_endpoint(parsed_args.endpoint)

        kwargs = {}

        if parsed_args.service:
            service = common.find_service_sdk(
                identity_client, parsed_args.service
            )
            kwargs['service_id'] = service.id

        if parsed_args.enabled:
            kwargs['is_enabled'] = True
        if parsed_args.disabled:
            kwargs['is_enabled'] = False

        if parsed_args.url:
            kwargs['url'] = parsed_args.url

        if parsed_args.interface:
            kwargs['interface'] = parsed_args.interface

        if parsed_args.region:
            kwargs['region_id'] = parsed_args.region

        identity_client.update_endpoint(
            endpoint.id,
            **kwargs,
        )


class ShowEndpoint(command.ShowOne):
    _description = _("Display endpoint details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'endpoint',
            metavar='<endpoint>',
            help=_(
                'Endpoint to display (endpoint ID, service ID,'
                ' service name, service type)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        endpoint = identity_client.find_endpoint(parsed_args.endpoint)

        service = common.find_service_sdk(identity_client, endpoint.service_id)

        return _format_endpoint(endpoint, service)
