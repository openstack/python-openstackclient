#    Copyright 2017 FUJITSU LIMITED
#    All Rights Reserved.
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

from osc_lib.cli import identity as identity_utils
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


_attr_map = [
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('type', 'Type', column_util.LIST_BOTH),
    ('endpoints', 'Endpoints', column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
]

_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'type': 'Type',
    'endpoints': 'Endpoints',
    'description': 'Description',
    'project_id': 'Project',
}


class CreateEndpointGroup(command.ShowOne):
    _description = _("Create an endpoint group")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the endpoint group'),
        )
        parser.add_argument(
            'name', metavar='<name>', help=_('Name for the endpoint group')
        )
        parser.add_argument(
            '--type',
            required=True,
            choices=['subnet', 'cidr'],
            help=_(
                'Type of endpoints in group (e.g. subnet, cidr, network, '
                'router). Currently only subnet and cidr are supported.'
            ),
        )
        parser.add_argument(
            '--value',
            action='append',
            dest='endpoints',
            required=True,
            help=_(
                'Endpoint(s) for the group. Must all be of the same type. '
                '(--value) option can be repeated'
            ),
        )
        identity_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        if parsed_args.project is not None:
            attrs['project_id'] = identity_common.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
        if parsed_args.description:
            attrs['description'] = parsed_args.description

        if parsed_args.name:
            attrs['name'] = str(parsed_args.name)
        attrs['type'] = parsed_args.type
        if parsed_args.type == 'subnet':
            _subnet_ids = [
                client.find_subnet(endpoint, ignore_missing=False)['id']
                for endpoint in parsed_args.endpoints
            ]
            attrs['endpoints'] = _subnet_ids
        else:
            attrs['endpoints'] = parsed_args.endpoints
        obj = client.create_vpn_endpoint_group(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id']
        )
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteEndpointGroup(command.Command):
    _description = _("Delete endpoint group(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'endpoint_group',
            metavar='<endpoint-group>',
            nargs='+',
            help=_('Endpoint group(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for endpoint in parsed_args.endpoint_group:
            try:
                endpoint_id = client.find_vpn_endpoint_group(
                    endpoint, ignore_missing=False
                ).id
                client.delete_vpn_endpoint_group(endpoint_id)
            except Exception as e:
                result += 1
                print(
                    f"Failed to delete endpoint group with "
                    f"name or ID {endpoint}: {e}"
                )

        if result > 0:
            total = len(parsed_args.endpoint_group)
            msg = _(
                "%(result)s of %(total)s endpoint group failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListEndpointGroup(command.Lister):
    _description = _("List endpoint groups that belong to a given project")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.vpn_endpoint_groups()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long
        )
        return (headers, (utils.get_dict_properties(s, columns) for s in obj))


class SetEndpointGroup(command.Command):
    _description = _("Set endpoint group properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the endpoint group'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set a name for the endpoint group'),
        )
        parser.add_argument(
            'endpoint_group',
            metavar='<endpoint-group>',
            help=_('Endpoint group to set (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        if parsed_args.description:
            attrs['description'] = parsed_args.description
        if parsed_args.name:
            attrs['name'] = str(parsed_args.name)
        endpoint_id = client.find_vpn_endpoint_group(
            parsed_args.endpoint_group, ignore_missing=False
        )['id']
        try:
            client.update_vpn_endpoint_group(endpoint_id, **attrs)
        except Exception as e:
            msg = _(
                "Failed to set endpoint group %(endpoint_group)s: %(e)s"
            ) % {'endpoint_group': parsed_args.endpoint_group, 'e': e}
            raise exceptions.CommandError(msg)


class ShowEndpointGroup(command.ShowOne):
    _description = _("Display endpoint group details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'endpoint_group',
            metavar='<endpoint-group>',
            help=_('Endpoint group to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_vpn_endpoint_group(
            parsed_args.endpoint_group, ignore_missing=False
        )
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id']
        )
        data = utils.get_dict_properties(obj, columns)
        return (display_columns, data)
