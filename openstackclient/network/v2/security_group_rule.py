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

"""Security Group Rule action implementations"""

import argparse
import logging

from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import sdk_utils
from openstackclient.network import utils as network_utils


LOG = logging.getLogger(__name__)


_formatters = {
    'location': format_columns.DictColumn,
}


def _format_security_group_rule_show(obj):
    data = network_utils.transform_compute_security_group_rule(obj)
    return zip(*sorted(six.iteritems(data)))


def _format_network_port_range(rule):
    # Display port range or ICMP type and code. For example:
    # - ICMP type: 'type=3'
    # - ICMP type and code: 'type=3:code=0'
    # - ICMP code: Not supported
    # - Matching port range: '443:443'
    # - Different port range: '22:24'
    # - Single port: '80:80'
    # - No port range: ''
    port_range = ''
    if _is_icmp_protocol(rule['protocol']):
        if rule['port_range_min']:
            port_range += 'type=' + str(rule['port_range_min'])
        if rule['port_range_max']:
            port_range += ':code=' + str(rule['port_range_max'])
    elif rule['port_range_min'] or rule['port_range_max']:
        port_range_min = str(rule['port_range_min'])
        port_range_max = str(rule['port_range_max'])
        if rule['port_range_min'] is None:
            port_range_min = port_range_max
        if rule['port_range_max'] is None:
            port_range_max = port_range_min
        port_range = port_range_min + ':' + port_range_max
    return port_range


def _format_remote_ip_prefix(rule):
    remote_ip_prefix = rule['remote_ip_prefix']
    if remote_ip_prefix is None:
        ethertype = rule['ether_type']
        if ethertype == 'IPv4':
            remote_ip_prefix = '0.0.0.0/0'
        elif ethertype == 'IPv6':
            remote_ip_prefix = '::/0'
    return remote_ip_prefix


def _get_columns(item):
    column_map = {
        'tenant_id': 'project_id',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


def _convert_to_lowercase(string):
    return string.lower()


def _convert_ipvx_case(string):
    if string.lower() == 'ipv4':
        return 'IPv4'
    if string.lower() == 'ipv6':
        return 'IPv6'
    return string


def _is_icmp_protocol(protocol):
    # NOTE(rtheis): Neutron has deprecated protocol icmpv6.
    # However, while the OSC CLI doesn't document the protocol,
    # the code must still handle it. In addition, handle both
    # protocol names and numbers.
    if protocol in ['icmp', 'icmpv6', 'ipv6-icmp', '1', '58']:
        return True
    else:
        return False


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateSecurityGroupRule(common.NetworkAndComputeShowOne):
    _description = _("Create a new security group rule")

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Create rule in this security group (name or ID)")
        )
        remote_group = parser.add_mutually_exclusive_group()
        remote_group.add_argument(
            "--remote-ip",
            metavar="<ip-address>",
            help=_("Remote IP address block (may use CIDR notation; "
                   "default for IPv4 rule: 0.0.0.0/0, "
                   "default for IPv6 rule: ::/0)"),
        )
        remote_group.add_argument(
            "--remote-group",
            metavar="<group>",
            help=_("Remote security group (name or ID)"),
        )
        return parser

    def update_parser_network(self, parser):
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set security group rule description")
        )
        parser.add_argument(
            '--dst-port',
            metavar='<port-range>',
            action=parseractions.RangeAction,
            help=_("Destination port, may be a single port or a starting and "
                   "ending port range: 137:139. Required for IP protocols TCP "
                   "and UDP. Ignored for ICMP IP protocols.")
        )
        parser.add_argument(
            '--icmp-type',
            metavar='<icmp-type>',
            type=int,
            help=_("ICMP type for ICMP IP protocols")
        )
        parser.add_argument(
            '--icmp-code',
            metavar='<icmp-code>',
            type=int,
            help=_("ICMP code for ICMP IP protocols")
        )
        # NOTE(rtheis): Support either protocol option name for now.
        # However, consider deprecating and then removing --proto in
        # a future release.
        protocol_group = parser.add_mutually_exclusive_group()
        protocol_group.add_argument(
            '--protocol',
            metavar='<protocol>',
            type=_convert_to_lowercase,
            help=_("IP protocol (ah, dccp, egp, esp, gre, icmp, igmp, "
                   "ipv6-encap, ipv6-frag, ipv6-icmp, ipv6-nonxt, "
                   "ipv6-opts, ipv6-route, ospf, pgm, rsvp, sctp, tcp, "
                   "udp, udplite, vrrp and integer representations [0-255] "
                   "or any; default: any (all protocols))")
        )
        protocol_group.add_argument(
            '--proto',
            metavar='<proto>',
            type=_convert_to_lowercase,
            help=argparse.SUPPRESS
        )
        direction_group = parser.add_mutually_exclusive_group()
        direction_group.add_argument(
            '--ingress',
            action='store_true',
            help=_("Rule applies to incoming network traffic (default)")
        )
        direction_group.add_argument(
            '--egress',
            action='store_true',
            help=_("Rule applies to outgoing network traffic")
        )
        parser.add_argument(
            '--ethertype',
            metavar='<ethertype>',
            choices=['IPv4', 'IPv6'],
            type=_convert_ipvx_case,
            help=_("Ethertype of network traffic "
                   "(IPv4, IPv6; default: based on IP protocol)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def update_parser_compute(self, parser):
        parser.add_argument(
            '--dst-port',
            metavar='<port-range>',
            default=(0, 0),
            action=parseractions.RangeAction,
            help=_("Destination port, may be a single port or a starting and "
                   "ending port range: 137:139. Required for IP protocols TCP "
                   "and UDP. Ignored for ICMP IP protocols.")
        )
        # NOTE(rtheis): Support either protocol option name for now.
        # However, consider deprecating and then removing --proto in
        # a future release.
        protocol_group = parser.add_mutually_exclusive_group()
        protocol_group.add_argument(
            '--protocol',
            metavar='<protocol>',
            choices=['icmp', 'tcp', 'udp'],
            type=_convert_to_lowercase,
            help=_("IP protocol (icmp, tcp, udp; default: tcp)")
        )
        protocol_group.add_argument(
            '--proto',
            metavar='<proto>',
            choices=['icmp', 'tcp', 'udp'],
            type=_convert_to_lowercase,
            help=argparse.SUPPRESS
        )
        return parser

    def _get_protocol(self, parsed_args, default_protocol='any'):
        protocol = default_protocol
        if parsed_args.protocol is not None:
            protocol = parsed_args.protocol
        if parsed_args.proto is not None:
            protocol = parsed_args.proto
        if protocol == 'any':
            protocol = None
        return protocol

    def _get_ethertype(self, parsed_args, protocol):
        ethertype = 'IPv4'
        if parsed_args.ethertype is not None:
            ethertype = parsed_args.ethertype
        elif self._is_ipv6_protocol(protocol):
            ethertype = 'IPv6'
        return ethertype

    def _is_ipv6_protocol(self, protocol):
        # NOTE(rtheis): Neutron has deprecated protocol icmpv6.
        # However, while the OSC CLI doesn't document the protocol,
        # the code must still handle it. In addition, handle both
        # protocol names and numbers.
        if (protocol is not None and protocol.startswith('ipv6-') or
                protocol in ['icmpv6', '41', '43', '44', '58', '59', '60']):
            return True
        else:
            return False

    def take_action_network(self, client, parsed_args):
        # Get the security group ID to hold the rule.
        security_group_id = client.find_security_group(
            parsed_args.group,
            ignore_missing=False
        ).id

        # Build the create attributes.
        attrs = {}
        attrs['protocol'] = self._get_protocol(parsed_args)

        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description

        # NOTE(rtheis): A direction must be specified and ingress
        # is the default.
        if parsed_args.ingress or not parsed_args.egress:
            attrs['direction'] = 'ingress'
        if parsed_args.egress:
            attrs['direction'] = 'egress'

        # NOTE(rtheis): Use ethertype specified else default based
        # on IP protocol.
        attrs['ethertype'] = self._get_ethertype(parsed_args,
                                                 attrs['protocol'])

        # NOTE(rtheis): Validate the port range and ICMP type and code.
        # It would be ideal if argparse could do this.
        if parsed_args.dst_port and (parsed_args.icmp_type or
                                     parsed_args.icmp_code):
            msg = _('Argument --dst-port not allowed with arguments '
                    '--icmp-type and --icmp-code')
            raise exceptions.CommandError(msg)
        if parsed_args.icmp_type is None and parsed_args.icmp_code is not None:
            msg = _('Argument --icmp-type required with argument --icmp-code')
            raise exceptions.CommandError(msg)
        is_icmp_protocol = _is_icmp_protocol(attrs['protocol'])
        if not is_icmp_protocol and (parsed_args.icmp_type or
                                     parsed_args.icmp_code):
            msg = _('ICMP IP protocol required with arguments '
                    '--icmp-type and --icmp-code')
            raise exceptions.CommandError(msg)
        # NOTE(rtheis): For backwards compatibility, continue ignoring
        # the destination port range when an ICMP IP protocol is specified.
        if parsed_args.dst_port and not is_icmp_protocol:
            attrs['port_range_min'] = parsed_args.dst_port[0]
            attrs['port_range_max'] = parsed_args.dst_port[1]
        if parsed_args.icmp_type is not None and parsed_args.icmp_type >= 0:
            attrs['port_range_min'] = parsed_args.icmp_type
        if parsed_args.icmp_code is not None and parsed_args.icmp_code >= 0:
            attrs['port_range_max'] = parsed_args.icmp_code

        if parsed_args.remote_group is not None:
            attrs['remote_group_id'] = client.find_security_group(
                parsed_args.remote_group,
                ignore_missing=False
            ).id
        elif parsed_args.remote_ip is not None:
            attrs['remote_ip_prefix'] = parsed_args.remote_ip
        elif attrs['ethertype'] == 'IPv4':
            attrs['remote_ip_prefix'] = '0.0.0.0/0'
        elif attrs['ethertype'] == 'IPv6':
            attrs['remote_ip_prefix'] = '::/0'
        attrs['security_group_id'] = security_group_id
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['tenant_id'] = project_id

        # Create and show the security group rule.
        obj = client.create_security_group_rule(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        group = client.api.security_group_find(parsed_args.group)
        protocol = self._get_protocol(parsed_args, default_protocol='tcp')
        if protocol == 'icmp':
            from_port, to_port = -1, -1
        else:
            from_port, to_port = parsed_args.dst_port

        remote_ip = None
        if parsed_args.remote_group is not None:
            parsed_args.remote_group = client.api.security_group_find(
                parsed_args.remote_group,
            )['id']
        if parsed_args.remote_ip is not None:
            remote_ip = parsed_args.remote_ip
        else:
            remote_ip = '0.0.0.0/0'

        obj = client.api.security_group_rule_create(
            security_group_id=group['id'],
            ip_protocol=protocol,
            from_port=from_port,
            to_port=to_port,
            remote_ip=remote_ip,
            remote_group=parsed_args.remote_group,
        )
        return _format_security_group_rule_show(obj)


class DeleteSecurityGroupRule(common.NetworkAndComputeDelete):
    _description = _("Delete security group rule(s)")

    # Used by base class to find resources in parsed_args.
    resource = 'rule'
    r = None

    def update_parser_common(self, parser):
        parser.add_argument(
            'rule',
            metavar='<rule>',
            nargs="+",
            help=_("Security group rule(s) to delete (ID only)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group_rule(
            self.r, ignore_missing=False)
        client.delete_security_group_rule(obj)

    def take_action_compute(self, client, parsed_args):
        client.api.security_group_rule_delete(self.r)


class ListSecurityGroupRule(common.NetworkAndComputeLister):
    _description = _("List security group rules")

    def _format_network_security_group_rule(self, rule):
        """Transform the SDK SecurityGroupRule object to a dict

        The SDK object gets in the way of reformatting columns...
        Create port_range column from port_range_min and port_range_max
        """
        rule = rule.to_dict()
        rule['port_range'] = _format_network_port_range(rule)
        rule['remote_ip_prefix'] = _format_remote_ip_prefix(rule)
        return rule

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs='?',
            help=_("List all rules in this security group (name or ID)")
        )
        return parser

    def update_parser_network(self, parser):
        # Accept but hide the argument for consistency with compute.
        # Network will always return all projects for an admin.
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            type=_convert_to_lowercase,
            help=_("List rules by the IP protocol ("
                   "ah, dhcp, egp, esp, gre, icmp, igmp, "
                   "ipv6-encap, ipv6-frag, ipv6-icmp, ipv6-nonxt, "
                   "ipv6-opts, ipv6-route, ospf, pgm, rsvp, sctp, tcp, "
                   "udp, udplite, vrrp and integer representations [0-255] "
                   "or any; default: any (all protocols))")
        )
        parser.add_argument(
            '--ethertype',
            metavar='<ethertype>',
            type=_convert_to_lowercase,
            help=_("List rules by the Ethertype (IPv4 or IPv6)")
        )
        direction_group = parser.add_mutually_exclusive_group()
        direction_group.add_argument(
            '--ingress',
            action='store_true',
            help=_("List rules applied to incoming network traffic")
        )
        direction_group.add_argument(
            '--egress',
            action='store_true',
            help=_("List rules applied to outgoing network traffic")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def update_parser_compute(self, parser):
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_("Display information from all projects (admin only)")
        )
        # Accept but hide the argument for consistency with network.
        # There are no additional fields to display at this time.
        parser.add_argument(
            '--long',
            action='store_false',
            default=False,
            help=argparse.SUPPRESS
        )
        return parser

    def _get_column_headers(self, parsed_args):
        column_headers = (
            'ID',
            'IP Protocol',
            'Ethertype',
            'IP Range',
            'Port Range',
        )
        if parsed_args.long:
            column_headers = column_headers + ('Direction',)
        column_headers = column_headers + ('Remote Security Group',)
        if parsed_args.group is None:
            column_headers = column_headers + ('Security Group',)
        return column_headers

    def take_action_network(self, client, parsed_args):
        column_headers = self._get_column_headers(parsed_args)
        columns = (
            'id',
            'protocol',
            'ether_type',
            'remote_ip_prefix',
            'port_range',
        )
        if parsed_args.long:
            columns = columns + ('direction',)
        columns = columns + ('remote_group_id',)

        # Get the security group rules using the requested query.
        query = {}
        if parsed_args.group is not None:
            # NOTE(rtheis): Unfortunately, the security group resource
            # does not contain security group rules resources. So use
            # the security group ID in a query to get the resources.
            security_group_id = client.find_security_group(
                parsed_args.group,
                ignore_missing=False
            ).id
            query = {'security_group_id': security_group_id}
        else:
            columns = columns + ('security_group_id',)

        if parsed_args.ingress:
            query['direction'] = 'ingress'
        if parsed_args.egress:
            query['direction'] = 'egress'
        if parsed_args.protocol is not None:
            query['protocol'] = parsed_args.protocol

        rules = [
            self._format_network_security_group_rule(r)
            for r in client.security_group_rules(**query)
        ]

        return (column_headers,
                (utils.get_dict_properties(
                    s, columns,
                ) for s in rules))

    def take_action_compute(self, client, parsed_args):
        column_headers = self._get_column_headers(parsed_args)
        columns = (
            "ID",
            "IP Protocol",
            "Ethertype",
            "IP Range",
            "Port Range",
            "Remote Security Group",
        )

        rules_to_list = []
        if parsed_args.group is not None:
            group = client.api.security_group_find(
                parsed_args.group,
            )
            rules_to_list = group['rules']
        else:
            columns = columns + ('parent_group_id',)
            search = {'all_tenants': parsed_args.all_projects}
            for group in client.api.security_group_list(search_opts=search):
                rules_to_list.extend(group['rules'])

        # NOTE(rtheis): Turn the raw rules into resources.
        rules = []
        for rule in rules_to_list:
            rules.append(
                network_utils.transform_compute_security_group_rule(rule),
            )
            # rules.append(compute_secgroup_rules.SecurityGroupRule(
            #     client.security_group_rules,
            #     network_utils.transform_compute_security_group_rule(rule),
            # ))

        return (column_headers,
                (utils.get_dict_properties(
                    s, columns,
                ) for s in rules))


class ShowSecurityGroupRule(common.NetworkAndComputeShowOne):
    _description = _("Display security group rule details")

    def update_parser_common(self, parser):
        parser.add_argument(
            'rule',
            metavar="<rule>",
            help=_("Security group rule to display (ID only)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group_rule(parsed_args.rule,
                                              ignore_missing=False)
        # necessary for old rules that have None in this field
        if not obj['remote_ip_prefix']:
            obj['remote_ip_prefix'] = _format_remote_ip_prefix(obj)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        # NOTE(rtheis): Unfortunately, compute does not have an API
        # to get or list security group rules so parse through the
        # security groups to find all accessible rules in search of
        # the requested rule.
        obj = None
        security_group_rules = []
        for security_group in client.api.security_group_list():
            security_group_rules.extend(security_group['rules'])
        for security_group_rule in security_group_rules:
            if parsed_args.rule == str(security_group_rule.get('id')):
                obj = security_group_rule
                break

        if obj is None:
            msg = _("Could not find security group rule "
                    "with ID '%s'") % parsed_args.rule
            raise exceptions.CommandError(msg)

        # NOTE(rtheis): Format security group rule
        return _format_security_group_rule_show(obj)
