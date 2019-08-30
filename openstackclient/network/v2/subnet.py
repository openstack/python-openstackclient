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

"""Subnet action implementations"""

import copy
import logging

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import sdk_utils
from openstackclient.network.v2 import _tag


LOG = logging.getLogger(__name__)


def _update_arguments(obj_list, parsed_args_list, option):
    for item in parsed_args_list:
        try:
            obj_list.remove(item)
        except ValueError:
            msg = (_("Subnet does not contain %(option)s %(value)s") %
                   {'option': option, 'value': item})
            raise exceptions.CommandError(msg)


class AllocationPoolsColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        pool_formatted = ['%s-%s' % (pool.get('start', ''),
                                     pool.get('end', ''))
                          for pool in self._value]
        return ','.join(pool_formatted)


class HostRoutesColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        # Map the host route keys to match --host-route option.
        return utils.format_list_of_dicts(
            convert_entries_to_gateway(self._value))


_formatters = {
    'allocation_pools': AllocationPoolsColumn,
    'dns_nameservers': format_columns.ListColumn,
    'host_routes': HostRoutesColumn,
    'location': format_columns.DictColumn,
    'service_types': format_columns.ListColumn,
    'tags': format_columns.ListColumn,
}


def _get_common_parse_arguments(parser, is_create=True):
    parser.add_argument(
        '--allocation-pool',
        metavar='start=<ip-address>,end=<ip-address>',
        dest='allocation_pools',
        action=parseractions.MultiKeyValueAction,
        required_keys=['start', 'end'],
        help=_("Allocation pool IP addresses for this subnet "
               "e.g.: start=192.168.199.2,end=192.168.199.254 "
               "(repeat option to add multiple IP addresses)")
    )
    if not is_create:
        parser.add_argument(
            '--no-allocation-pool',
            action='store_true',
            help=_("Clear associated allocation-pools from the subnet. "
                   "Specify both --allocation-pool and --no-allocation-pool "
                   "to overwrite the current allocation pool information.")
        )
    parser.add_argument(
        '--dns-nameserver',
        metavar='<dns-nameserver>',
        action='append',
        dest='dns_nameservers',
        help=_("DNS server for this subnet "
               "(repeat option to set multiple DNS servers)")
    )

    if not is_create:
        parser.add_argument(
            '--no-dns-nameservers',
            action='store_true',
            help=_("Clear existing information of DNS Nameservers. "
                   "Specify both --dns-nameserver and --no-dns-nameserver "
                   "to overwrite the current DNS Nameserver information.")
        )
    parser.add_argument(
        '--host-route',
        metavar='destination=<subnet>,gateway=<ip-address>',
        dest='host_routes',
        action=parseractions.MultiKeyValueAction,
        required_keys=['destination', 'gateway'],
        help=_("Additional route for this subnet "
               "e.g.: destination=10.10.0.0/16,gateway=192.168.71.254 "
               "destination: destination subnet (in CIDR notation) "
               "gateway: nexthop IP address "
               "(repeat option to add multiple routes)")
    )
    if not is_create:
        parser.add_argument(
            '--no-host-route',
            action='store_true',
            help=_("Clear associated host-routes from the subnet. "
                   "Specify both --host-route and --no-host-route "
                   "to overwrite the current host route information.")
        )
    parser.add_argument(
        '--service-type',
        metavar='<service-type>',
        action='append',
        dest='service_types',
        help=_("Service type for this subnet "
               "e.g.: network:floatingip_agent_gateway. "
               "Must be a valid device owner value for a network port "
               "(repeat option to set multiple service types)")
    )


def _get_columns(item):
    column_map = {
        'is_dhcp_enabled': 'enable_dhcp',
        'subnet_pool_id': 'subnetpool_id',
        'tenant_id': 'project_id',
    }
    # Do not show this column when displaying a subnet
    invisible_columns = ['use_default_subnet_pool']
    return sdk_utils.get_osc_show_columns_for_sdk_resource(
        item,
        column_map,
        invisible_columns=invisible_columns
    )


def convert_entries_to_nexthop(entries):
    # Change 'gateway' entry to 'nexthop'
    changed_entries = copy.deepcopy(entries)
    for entry in changed_entries:
        if 'gateway' in entry:
            entry['nexthop'] = entry['gateway']
            del entry['gateway']

    return changed_entries


def convert_entries_to_gateway(entries):
    # Change 'nexthop' entry to 'gateway'
    changed_entries = copy.deepcopy(entries)
    for entry in changed_entries:
        if 'nexthop' in entry:
            entry['gateway'] = entry['nexthop']
            del entry['nexthop']

    return changed_entries


def _get_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    client = client_manager.network
    if 'name' in parsed_args and parsed_args.name is not None:
        attrs['name'] = parsed_args.name

    if is_create:
        if 'project' in parsed_args and parsed_args.project is not None:
            identity_client = client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['tenant_id'] = project_id
        attrs['network_id'] = client.find_network(parsed_args.network,
                                                  ignore_missing=False).id
        if parsed_args.subnet_pool is not None:
            subnet_pool = client.find_subnet_pool(parsed_args.subnet_pool,
                                                  ignore_missing=False)
            attrs['subnetpool_id'] = subnet_pool.id
        if parsed_args.use_prefix_delegation:
            attrs['subnetpool_id'] = "prefix_delegation"
        if parsed_args.use_default_subnet_pool:
            attrs['use_default_subnet_pool'] = True
        if parsed_args.prefix_length is not None:
            attrs['prefixlen'] = parsed_args.prefix_length
        if parsed_args.subnet_range is not None:
            attrs['cidr'] = parsed_args.subnet_range
        if parsed_args.ip_version is not None:
            attrs['ip_version'] = parsed_args.ip_version
        if parsed_args.ipv6_ra_mode is not None:
            attrs['ipv6_ra_mode'] = parsed_args.ipv6_ra_mode
        if parsed_args.ipv6_address_mode is not None:
            attrs['ipv6_address_mode'] = parsed_args.ipv6_address_mode

    if parsed_args.network_segment is not None:
        attrs['segment_id'] = client.find_segment(
            parsed_args.network_segment, ignore_missing=False).id
    if 'gateway' in parsed_args and parsed_args.gateway is not None:
        gateway = parsed_args.gateway.lower()

        if not is_create and gateway == 'auto':
            msg = _("Auto option is not available for Subnet Set. "
                    "Valid options are <ip-address> or none")
            raise exceptions.CommandError(msg)
        elif gateway != 'auto':
            if gateway == 'none':
                attrs['gateway_ip'] = None
            else:
                attrs['gateway_ip'] = gateway
    if ('allocation_pools' in parsed_args and
       parsed_args.allocation_pools is not None):
        attrs['allocation_pools'] = parsed_args.allocation_pools
    if parsed_args.dhcp:
        attrs['enable_dhcp'] = True
    if parsed_args.no_dhcp:
        attrs['enable_dhcp'] = False
    if ('dns_nameservers' in parsed_args and
       parsed_args.dns_nameservers is not None):
        attrs['dns_nameservers'] = parsed_args.dns_nameservers
    if 'host_routes' in parsed_args and parsed_args.host_routes is not None:
        # Change 'gateway' entry to 'nexthop' to match the API
        attrs['host_routes'] = convert_entries_to_nexthop(
            parsed_args.host_routes)
    if ('service_types' in parsed_args and
       parsed_args.service_types is not None):
        attrs['service_types'] = parsed_args.service_types
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    return attrs


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateSubnet(command.ShowOne):
    _description = _("Create a subnet")

    def get_parser(self, prog_name):
        parser = super(CreateSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New subnet name")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        subnet_pool_group = parser.add_mutually_exclusive_group()
        subnet_pool_group.add_argument(
            '--subnet-pool',
            metavar='<subnet-pool>',
            help=_("Subnet pool from which this subnet will obtain a CIDR "
                   "(Name or ID)")
        )
        subnet_pool_group.add_argument(
            '--use-prefix-delegation',
            help=_("Use 'prefix-delegation' if IP is IPv6 format "
                   "and IP would be delegated externally")
        )
        subnet_pool_group.add_argument(
            '--use-default-subnet-pool',
            action='store_true',
            help=_("Use default subnet pool for --ip-version")
        )
        parser.add_argument(
            '--prefix-length',
            metavar='<prefix-length>',
            help=_("Prefix length for subnet allocation from subnet pool")
        )
        parser.add_argument(
            '--subnet-range',
            metavar='<subnet-range>',
            help=_("Subnet range in CIDR notation "
                   "(required if --subnet-pool is not specified, "
                   "optional otherwise)")
        )
        dhcp_enable_group = parser.add_mutually_exclusive_group()
        dhcp_enable_group.add_argument(
            '--dhcp',
            action='store_true',
            help=_("Enable DHCP (default)")
        )
        dhcp_enable_group.add_argument(
            '--no-dhcp',
            action='store_true',
            help=_("Disable DHCP")
        )
        parser.add_argument(
            '--gateway',
            metavar='<gateway>',
            default='auto',
            help=_("Specify a gateway for the subnet.  The three options are: "
                   "<ip-address>: Specific IP address to use as the gateway, "
                   "'auto': Gateway address should automatically be chosen "
                   "from within the subnet itself, 'none': This subnet will "
                   "not use a gateway, e.g.: --gateway 192.168.9.1, "
                   "--gateway auto, --gateway none (default is 'auto').")
        )
        parser.add_argument(
            '--ip-version',
            type=int,
            default=4,
            choices=[4, 6],
            help=_("IP version (default is 4).  Note that when subnet pool is "
                   "specified, IP version is determined from the subnet pool "
                   "and this option is ignored.")
        )
        parser.add_argument(
            '--ipv6-ra-mode',
            choices=['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac'],
            help=_("IPv6 RA (Router Advertisement) mode, "
                   "valid modes: [dhcpv6-stateful, dhcpv6-stateless, slaac]")
        )
        parser.add_argument(
            '--ipv6-address-mode',
            choices=['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac'],
            help=_("IPv6 address mode, "
                   "valid modes: [dhcpv6-stateful, dhcpv6-stateless, slaac]")
        )
        parser.add_argument(
            '--network-segment',
            metavar='<network-segment>',
            help=_("Network segment to associate with this subnet "
                   "(name or ID)")
        )
        parser.add_argument(
            '--network',
            required=True,
            metavar='<network>',
            help=_("Network this subnet belongs to (name or ID)")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set subnet description")
        )
        _get_common_parse_arguments(parser)
        _tag.add_tag_option_to_parser_for_create(parser, _('subnet'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_subnet(**attrs)
        # tags cannot be set when created, so tags need to be set later.
        _tag.update_tags_for_set(client, obj, parsed_args)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)


class DeleteSubnet(command.Command):
    _description = _("Delete subnet(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            nargs='+',
            help=_("Subnet(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for subnet in parsed_args.subnet:
            try:
                obj = client.find_subnet(subnet, ignore_missing=False)
                client.delete_subnet(obj)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete subnet with "
                          "name or ID '%(subnet)s': %(e)s"),
                          {'subnet': subnet, 'e': e})

        if result > 0:
            total = len(parsed_args.subnet)
            msg = (_("%(result)s of %(total)s subnets failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


# TODO(abhiraut): Use only the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListSubnet(command.Lister):
    _description = _("List subnets")

    def get_parser(self, prog_name):
        parser = super(ListSubnet, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        parser.add_argument(
            '--ip-version',
            type=int,
            choices=[4, 6],
            metavar='<ip-version>',
            dest='ip_version',
            help=_("List only subnets of given IP version in output. "
                   "Allowed values for IP version are 4 and 6."),
        )
        dhcp_enable_group = parser.add_mutually_exclusive_group()
        dhcp_enable_group.add_argument(
            '--dhcp',
            action='store_true',
            help=_("List subnets which have DHCP enabled")
        )
        dhcp_enable_group.add_argument(
            '--no-dhcp',
            action='store_true',
            help=_("List subnets which have DHCP disabled")
        )
        parser.add_argument(
            '--service-type',
            metavar='<service-type>',
            action='append',
            dest='service_types',
            help=_("List only subnets of a given service type in output "
                   "e.g.: network:floatingip_agent_gateway. "
                   "Must be a valid device owner value for a network port "
                   "(repeat option to list multiple service types)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List only subnets which belong to a given project "
                   "in output (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--network',
            metavar='<network>',
            help=_("List only subnets which belong to a given network "
                   "in output (name or ID)")
        )
        parser.add_argument(
            '--gateway',
            metavar='<gateway>',
            help=_("List only subnets of given gateway IP in output")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("List only subnets of given name in output")
        )
        parser.add_argument(
            '--subnet-range',
            metavar='<subnet-range>',
            help=_("List only subnets of given subnet range "
                   "(in CIDR notation) in output "
                   "e.g.: --subnet-range 10.10.0.0/16")
        )
        _tag.add_tag_filtering_option_to_parser(parser, _('subnets'))
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        network_client = self.app.client_manager.network
        filters = {}
        if parsed_args.ip_version:
            filters['ip_version'] = parsed_args.ip_version
        if parsed_args.dhcp:
            filters['enable_dhcp'] = True
            filters['is_dhcp_enabled'] = True
        elif parsed_args.no_dhcp:
            filters['enable_dhcp'] = False
            filters['is_dhcp_enabled'] = False
        if parsed_args.service_types:
            filters['service_types'] = parsed_args.service_types
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            filters['tenant_id'] = project_id
            filters['project_id'] = project_id
        if parsed_args.network:
            network_id = network_client.find_network(parsed_args.network,
                                                     ignore_missing=False).id
            filters['network_id'] = network_id
        if parsed_args.gateway:
            filters['gateway_ip'] = parsed_args.gateway
        if parsed_args.name:
            filters['name'] = parsed_args.name
        if parsed_args.subnet_range:
            filters['cidr'] = parsed_args.subnet_range
        _tag.get_tag_filtering_args(parsed_args, filters)
        data = network_client.subnets(**filters)

        headers = ('ID', 'Name', 'Network', 'Subnet')
        columns = ('id', 'name', 'network_id', 'cidr')
        if parsed_args.long:
            headers += ('Project', 'DHCP', 'Name Servers',
                        'Allocation Pools', 'Host Routes', 'IP Version',
                        'Gateway', 'Service Types', 'Tags')
            columns += ('project_id', 'is_dhcp_enabled', 'dns_nameservers',
                        'allocation_pools', 'host_routes', 'ip_version',
                        'gateway_ip', 'service_types', 'tags')

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetSubnet(command.Command):
    _description = _("Set subnet properties")

    def get_parser(self, prog_name):
        parser = super(SetSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            help=_("Subnet to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("Updated name of the subnet")
        )
        dhcp_enable_group = parser.add_mutually_exclusive_group()
        dhcp_enable_group.add_argument(
            '--dhcp',
            action='store_true',
            default=None,
            help=_("Enable DHCP")
        )
        dhcp_enable_group.add_argument(
            '--no-dhcp',
            action='store_true',
            help=_("Disable DHCP")
        )
        parser.add_argument(
            '--gateway',
            metavar='<gateway>',
            help=_("Specify a gateway for the subnet. The options are: "
                   "<ip-address>: Specific IP address to use as the gateway, "
                   "'none': This subnet will not use a gateway, "
                   "e.g.: --gateway 192.168.9.1, --gateway none.")
        )
        parser.add_argument(
            '--network-segment',
            metavar='<network-segment>',
            help=_("Network segment to associate with this subnet (name or "
                   "ID). It is only allowed to set the segment if the current "
                   "value is `None`, the network must also have only one "
                   "segment and only one subnet can exist on the network.")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set subnet description")
        )
        _tag.add_tag_option_to_parser_for_set(parser, _('subnet'))
        _get_common_parse_arguments(parser, is_create=False)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet(parsed_args.subnet, ignore_missing=False)
        attrs = _get_attrs(self.app.client_manager, parsed_args,
                           is_create=False)
        if 'dns_nameservers' in attrs:
            if not parsed_args.no_dns_nameservers:
                attrs['dns_nameservers'] += obj.dns_nameservers
        elif parsed_args.no_dns_nameservers:
            attrs['dns_nameservers'] = []
        if 'host_routes' in attrs:
            if not parsed_args.no_host_route:
                attrs['host_routes'] += obj.host_routes
        elif parsed_args.no_host_route:
            attrs['host_routes'] = []
        if 'allocation_pools' in attrs:
            if not parsed_args.no_allocation_pool:
                attrs['allocation_pools'] += obj.allocation_pools
        elif parsed_args.no_allocation_pool:
            attrs['allocation_pools'] = []
        if 'service_types' in attrs:
            attrs['service_types'] += obj.service_types
        if attrs:
            client.update_subnet(obj, **attrs)
        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_set(client, obj, parsed_args)
        return


class ShowSubnet(command.ShowOne):
    _description = _("Display subnet details")

    def get_parser(self, prog_name):
        parser = super(ShowSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            help=_("Subnet to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        obj = self.app.client_manager.network.find_subnet(parsed_args.subnet,
                                                          ignore_missing=False)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)


class UnsetSubnet(command.Command):
    _description = _("Unset subnet properties")

    def get_parser(self, prog_name):
        parser = super(UnsetSubnet, self).get_parser(prog_name)
        parser.add_argument(
            '--allocation-pool',
            metavar='start=<ip-address>,end=<ip-address>',
            dest='allocation_pools',
            action=parseractions.MultiKeyValueAction,
            required_keys=['start', 'end'],
            help=_('Allocation pool IP addresses to be removed from this '
                   'subnet e.g.: start=192.168.199.2,end=192.168.199.254 '
                   '(repeat option to unset multiple allocation pools)')
        )
        parser.add_argument(
            '--dns-nameserver',
            metavar='<dns-nameserver>',
            action='append',
            dest='dns_nameservers',
            help=_('DNS server to be removed from this subnet '
                   '(repeat option to unset multiple DNS servers)')
        )
        parser.add_argument(
            '--host-route',
            metavar='destination=<subnet>,gateway=<ip-address>',
            dest='host_routes',
            action=parseractions.MultiKeyValueAction,
            required_keys=['destination', 'gateway'],
            help=_('Route to be removed from this subnet '
                   'e.g.: destination=10.10.0.0/16,gateway=192.168.71.254 '
                   'destination: destination subnet (in CIDR notation) '
                   'gateway: nexthop IP address '
                   '(repeat option to unset multiple host routes)')
        )
        parser.add_argument(
            '--service-type',
            metavar='<service-type>',
            action='append',
            dest='service_types',
            help=_('Service type to be removed from this subnet '
                   'e.g.: network:floatingip_agent_gateway. '
                   'Must be a valid device owner value for a network port '
                   '(repeat option to unset multiple service types)')
        )
        _tag.add_tag_option_to_parser_for_unset(parser, _('subnet'))
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            help=_("Subnet to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet(parsed_args.subnet, ignore_missing=False)

        attrs = {}
        if parsed_args.dns_nameservers:
            attrs['dns_nameservers'] = copy.deepcopy(obj.dns_nameservers)
            _update_arguments(attrs['dns_nameservers'],
                              parsed_args.dns_nameservers,
                              'dns-nameserver')
        if parsed_args.host_routes:
            attrs['host_routes'] = copy.deepcopy(obj.host_routes)
            _update_arguments(
                attrs['host_routes'],
                convert_entries_to_nexthop(parsed_args.host_routes),
                'host-route')
        if parsed_args.allocation_pools:
            attrs['allocation_pools'] = copy.deepcopy(obj.allocation_pools)
            _update_arguments(attrs['allocation_pools'],
                              parsed_args.allocation_pools,
                              'allocation-pool')

        if parsed_args.service_types:
            attrs['service_types'] = copy.deepcopy(obj.service_types)
            _update_arguments(attrs['service_types'],
                              parsed_args.service_types,
                              'service-type')
        if attrs:
            client.update_subnet(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_unset(client, obj, parsed_args)
