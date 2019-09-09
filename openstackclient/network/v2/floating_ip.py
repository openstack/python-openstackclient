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

"""IP Floating action implementations"""

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import sdk_utils
from openstackclient.network.v2 import _tag


_formatters = {
    'location': format_columns.DictColumn,
    'port_details': utils.format_dict,
}


def _get_network_columns(item):
    column_map = {
        'tenant_id': 'project_id',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    network_client = client_manager.network

    # Name of a network could be empty string.
    if parsed_args.network is not None:
        network = network_client.find_network(parsed_args.network,
                                              ignore_missing=False)
        attrs['floating_network_id'] = network.id

    if parsed_args.subnet:
        subnet = network_client.find_subnet(parsed_args.subnet,
                                            ignore_missing=False)
        attrs['subnet_id'] = subnet.id

    if parsed_args.port:
        port = network_client.find_port(parsed_args.port,
                                        ignore_missing=False)
        attrs['port_id'] = port.id

    if parsed_args.floating_ip_address:
        attrs['floating_ip_address'] = parsed_args.floating_ip_address

    if parsed_args.fixed_ip_address:
        attrs['fixed_ip_address'] = parsed_args.fixed_ip_address

    if parsed_args.qos_policy:
        attrs['qos_policy_id'] = network_client.find_qos_policy(
            parsed_args.qos_policy, ignore_missing=False).id

    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description

    if parsed_args.project:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    if parsed_args.dns_domain:
        attrs['dns_domain'] = parsed_args.dns_domain

    if parsed_args.dns_name:
        attrs['dns_name'] = parsed_args.dns_name

    return attrs


class CreateFloatingIP(common.NetworkAndComputeShowOne):
    _description = _("Create floating IP")

    def update_parser_common(self, parser):
        # In Compute v2 network, floating IPs could be allocated from floating
        # IP pools, which are actually external networks. So deprecate the
        # parameter "pool", and use "network" instead.
        parser.add_argument(
            'network',
            metavar='<network>',
            help=_("Network to allocate floating IP from (name or ID)")
        )
        return parser

    def update_parser_network(self, parser):
        parser.add_argument(
            '--subnet',
            metavar='<subnet>',
            help=_("Subnet on which you want to create the floating IP "
                   "(name or ID)")
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_("Port to be associated with the floating IP "
                   "(name or ID)")
        )
        parser.add_argument(
            '--floating-ip-address',
            metavar='<ip-address>',
            dest='floating_ip_address',
            help=_("Floating IP address")
        )
        parser.add_argument(
            '--fixed-ip-address',
            metavar='<ip-address>',
            dest='fixed_ip_address',
            help=_("Fixed IP address mapped to the floating IP")
        )
        parser.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("Attach QoS policy to the floating IP (name or ID)")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set floating IP description')
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        parser.add_argument(
            '--dns-domain',
            metavar='<dns-domain>',
            dest='dns_domain',
            help=_("Set DNS domain for this floating IP")
        )
        parser.add_argument(
            '--dns-name',
            metavar='<dns-name>',
            dest='dns_name',
            help=_("Set DNS name for this floating IP")
        )

        identity_common.add_project_domain_option_to_parser(parser)
        _tag.add_tag_option_to_parser_for_create(parser, _('floating IP'))
        return parser

    def take_action_network(self, client, parsed_args):
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        with common.check_missing_extension_if_error(
                self.app.client_manager.network, attrs):
            obj = client.create_ip(**attrs)

        # tags cannot be set when created, so tags need to be set later.
        _tag.update_tags_for_set(client, obj, parsed_args)

        display_columns, columns = _get_network_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = client.api.floating_ip_create(parsed_args.network)
        columns = _get_columns(obj)
        data = utils.get_dict_properties(obj, columns)
        return (columns, data)


class DeleteFloatingIP(common.NetworkAndComputeDelete):
    _description = _("Delete floating IP(s)")

    # Used by base class to find resources in parsed_args.
    resource = 'floating_ip'
    r = None

    def update_parser_common(self, parser):
        parser.add_argument(
            'floating_ip',
            metavar="<floating-ip>",
            nargs="+",
            help=_("Floating IP(s) to delete (IP address or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_ip(
            self.r,
            ignore_missing=False,
        )
        client.delete_ip(obj)

    def take_action_compute(self, client, parsed_args):
        client.api.floating_ip_delete(self.r)


class ListFloatingIP(common.NetworkAndComputeLister):
    # TODO(songminglong): Use SDK resource mapped attribute names once
    # the OSC minimum requirements include SDK 1.0
    _description = _("List floating IP(s)")

    def update_parser_network(self, parser):
        parser.add_argument(
            '--network',
            metavar='<network>',
            help=_("List floating IP(s) according to "
                   "given network (name or ID)")
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_("List floating IP(s) according to "
                   "given port (name or ID)")
        )
        parser.add_argument(
            '--fixed-ip-address',
            metavar='<ip-address>',
            help=_("List floating IP(s) according to "
                   "given fixed IP address")
        )
        parser.add_argument(
            '--floating-ip-address',
            metavar='<ip-address>',
            help=_("List floating IP(s) according to "
                   "given floating IP address")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            choices=['ACTIVE', 'DOWN'],
            help=_("List floating IP(s) according to "
                   "given status ('ACTIVE', 'DOWN')")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List floating IP(s) according to "
                   "given project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--router',
            metavar='<router>',
            help=_("List floating IP(s) according to "
                   "given router (name or ID)")
        )
        _tag.add_tag_filtering_option_to_parser(parser, _('floating IP'))

        return parser

    def take_action_network(self, client, parsed_args):
        network_client = self.app.client_manager.network
        identity_client = self.app.client_manager.identity

        columns = (
            'id',
            'floating_ip_address',
            'fixed_ip_address',
            'port_id',
            'floating_network_id',
            'project_id',
        )
        headers = (
            'ID',
            'Floating IP Address',
            'Fixed IP Address',
            'Port',
            'Floating Network',
            'Project',
        )
        if parsed_args.long:
            columns = columns + (
                'router_id',
                'status',
                'description',
                'tags',
                'dns_name',
                'dns_domain',
            )
            headers = headers + (
                'Router',
                'Status',
                'Description',
                'Tags',
                'DNS Name',
                'DNS Domain',
            )

        query = {}

        if parsed_args.network is not None:
            network = network_client.find_network(parsed_args.network,
                                                  ignore_missing=False)
            query['floating_network_id'] = network.id
        if parsed_args.port is not None:
            port = network_client.find_port(parsed_args.port,
                                            ignore_missing=False)
            query['port_id'] = port.id
        if parsed_args.fixed_ip_address is not None:
            query['fixed_ip_address'] = parsed_args.fixed_ip_address
        if parsed_args.floating_ip_address is not None:
            query['floating_ip_address'] = parsed_args.floating_ip_address
        if parsed_args.status:
            query['status'] = parsed_args.status
        if parsed_args.project is not None:
            project = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            )
            query['tenant_id'] = project.id
            query['project_id'] = project.id
        if parsed_args.router is not None:
            router = network_client.find_router(parsed_args.router,
                                                ignore_missing=False)
            query['router_id'] = router.id

        _tag.get_tag_filtering_args(parsed_args, query)

        data = client.ips(**query)

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))

    def take_action_compute(self, client, parsed_args):
        columns = (
            'ID',
            'IP',
            'Fixed IP',
            'Instance ID',
            'Pool',
        )
        headers = (
            'ID',
            'Floating IP Address',
            'Fixed IP Address',
            'Server',
            'Pool',
        )

        data = client.api.floating_ip_list()

        return (headers,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetFloatingIP(command.Command):
    _description = _("Set floating IP Properties")

    def get_parser(self, prog_name):
        parser = super(SetFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            'floating_ip',
            metavar='<floating-ip>',
            help=_("Floating IP to modify (IP address or ID)"))
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_("Associate the floating IP with port (name or ID)")),
        parser.add_argument(
            '--fixed-ip-address',
            metavar='<ip-address>',
            dest='fixed_ip_address',
            help=_("Fixed IP of the port "
                   "(required only if port has multiple IPs)")
        )
        qos_policy_group = parser.add_mutually_exclusive_group()
        qos_policy_group.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("Attach QoS policy to the floating IP (name or ID)")
        )
        qos_policy_group.add_argument(
            '--no-qos-policy',
            action='store_true',
            help=_("Remove the QoS policy attached to the floating IP")
        )

        _tag.add_tag_option_to_parser_for_set(parser, _('floating IP'))

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        obj = client.find_ip(
            parsed_args.floating_ip,
            ignore_missing=False,
        )
        if parsed_args.port:
            port = client.find_port(parsed_args.port,
                                    ignore_missing=False)
            attrs['port_id'] = port.id

        if parsed_args.fixed_ip_address:
            attrs['fixed_ip_address'] = parsed_args.fixed_ip_address

        if parsed_args.qos_policy:
            attrs['qos_policy_id'] = client.find_qos_policy(
                parsed_args.qos_policy, ignore_missing=False).id

        if 'no_qos_policy' in parsed_args and parsed_args.no_qos_policy:
            attrs['qos_policy_id'] = None

        if attrs:
            client.update_ip(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_set(client, obj, parsed_args)


class ShowFloatingIP(common.NetworkAndComputeShowOne):
    _description = _("Display floating IP details")

    def update_parser_common(self, parser):
        parser.add_argument(
            'floating_ip',
            metavar="<floating-ip>",
            help=_("Floating IP to display (IP address or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_ip(
            parsed_args.floating_ip,
            ignore_missing=False,
        )
        display_columns, columns = _get_network_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = client.api.floating_ip_find(parsed_args.floating_ip)
        columns = _get_columns(obj)
        data = utils.get_dict_properties(obj, columns)
        return (columns, data)


class UnsetFloatingIP(command.Command):
    _description = _("Unset floating IP Properties")

    def get_parser(self, prog_name):
        parser = super(UnsetFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            'floating_ip',
            metavar='<floating-ip>',
            help=_("Floating IP to disassociate (IP address or ID)"))
        parser.add_argument(
            '--port',
            action='store_true',
            default=False,
            help=_("Disassociate any port associated with the floating IP")
        )
        parser.add_argument(
            '--qos-policy',
            action='store_true',
            default=False,
            help=_("Remove the QoS policy attached to the floating IP")
        )
        _tag.add_tag_option_to_parser_for_unset(parser, _('floating IP'))

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_ip(
            parsed_args.floating_ip,
            ignore_missing=False,
        )
        attrs = {}
        if parsed_args.port:
            attrs['port_id'] = None
        if parsed_args.qos_policy:
            attrs['qos_policy_id'] = None

        if attrs:
            client.update_ip(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_unset(client, obj, parsed_args)
