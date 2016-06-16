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

try:
    from novaclient.v2 import security_group_rules as compute_secgroup_rules
except ImportError:
    from novaclient.v1_1 import security_group_rules as compute_secgroup_rules

from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import utils as network_utils


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
    if _is_icmp_protocol(rule.protocol):
        if rule.port_range_min:
            port_range += 'type=' + str(rule.port_range_min)
        if rule.port_range_max:
            port_range += ':code=' + str(rule.port_range_max)
    elif rule.port_range_min or rule.port_range_max:
        port_range_min = str(rule.port_range_min)
        port_range_max = str(rule.port_range_max)
        if rule.port_range_min is None:
            port_range_min = port_range_max
        if rule.port_range_max is None:
            port_range_max = port_range_min
        port_range = port_range_min + ':' + port_range_max
    return port_range


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


def _convert_to_lowercase(string):
    return string.lower()


def _is_icmp_protocol(protocol):
    # NOTE(rtheis): Neutron has deprecated protocol icmpv6.
    # However, while the OSC CLI doesn't document the protocol,
    # the code must still handle it. In addition, handle both
    # protocol names and numbers.
    if protocol in ['icmp', 'icmpv6', 'ipv6-icmp', '1', '58']:
        return True
    else:
        return False


class CreateSecurityGroupRule(common.NetworkAndComputeShowOne):
    """Create a new security group rule"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Create rule in this security group (name or ID)")
        )
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument(
            "--src-ip",
            metavar="<ip-address>",
            help=_("Source IP address block (may use CIDR notation; "
                   "default for IPv4 rule: 0.0.0.0/0)")
        )
        source_group.add_argument(
            "--src-group",
            metavar="<group>",
            help=_("Source security group (name or ID)")
        )
        return parser

    def update_parser_network(self, parser):
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
                   "udp, udplite, vrrp and integer representations [0-255]; "
                   "default: tcp)")
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

    def _get_protocol(self, parsed_args):
        protocol = 'tcp'
        if parsed_args.protocol is not None:
            protocol = parsed_args.protocol
        if parsed_args.proto is not None:
            protocol = parsed_args.proto
        return protocol

    def _is_ipv6_protocol(self, protocol):
        # NOTE(rtheis): Neutron has deprecated protocol icmpv6.
        # However, while the OSC CLI doesn't document the protocol,
        # the code must still handle it. In addition, handle both
        # protocol names and numbers.
        if (protocol.startswith('ipv6-') or
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

        # NOTE(rtheis): A direction must be specified and ingress
        # is the default.
        if parsed_args.ingress or not parsed_args.egress:
            attrs['direction'] = 'ingress'
        if parsed_args.egress:
            attrs['direction'] = 'egress'

        # NOTE(rtheis): Use ethertype specified else default based
        # on IP protocol.
        if parsed_args.ethertype:
            attrs['ethertype'] = parsed_args.ethertype
        elif self._is_ipv6_protocol(attrs['protocol']):
            attrs['ethertype'] = 'IPv6'
        else:
            attrs['ethertype'] = 'IPv4'

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
        if parsed_args.icmp_type:
            attrs['port_range_min'] = parsed_args.icmp_type
        if parsed_args.icmp_code:
            attrs['port_range_max'] = parsed_args.icmp_code

        if parsed_args.src_group is not None:
            attrs['remote_group_id'] = client.find_security_group(
                parsed_args.src_group,
                ignore_missing=False
            ).id
        elif parsed_args.src_ip is not None:
            attrs['remote_ip_prefix'] = parsed_args.src_ip
        elif attrs['ethertype'] == 'IPv4':
            attrs['remote_ip_prefix'] = '0.0.0.0/0'
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
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (columns, data)

    def take_action_compute(self, client, parsed_args):
        group = utils.find_resource(
            client.security_groups,
            parsed_args.group,
        )
        protocol = self._get_protocol(parsed_args)
        if protocol == 'icmp':
            from_port, to_port = -1, -1
        else:
            from_port, to_port = parsed_args.dst_port
        src_ip = None
        if parsed_args.src_group is not None:
            parsed_args.src_group = utils.find_resource(
                client.security_groups,
                parsed_args.src_group,
            ).id
        if parsed_args.src_ip is not None:
            src_ip = parsed_args.src_ip
        else:
            src_ip = '0.0.0.0/0'
        obj = client.security_group_rules.create(
            group.id,
            protocol,
            from_port,
            to_port,
            src_ip,
            parsed_args.src_group,
        )
        return _format_security_group_rule_show(obj._info)


class DeleteSecurityGroupRule(common.NetworkAndComputeDelete):
    """Delete security group rule(s)"""

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
        client.security_group_rules.delete(self.r)


class ListSecurityGroupRule(common.NetworkAndComputeLister):
    """List security group rules"""

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
            'IP Range',
            'Port Range',
        )
        if parsed_args.long:
            column_headers = column_headers + ('Direction', 'Ethertype',)
        column_headers = column_headers + ('Remote Security Group',)
        if parsed_args.group is None:
            column_headers = column_headers + ('Security Group',)
        return column_headers

    def take_action_network(self, client, parsed_args):
        column_headers = self._get_column_headers(parsed_args)
        columns = (
            'id',
            'protocol',
            'remote_ip_prefix',
            'port_range_min',
        )
        if parsed_args.long:
            columns = columns + ('direction', 'ethertype',)
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
        rules = list(client.security_group_rules(**query))

        # Reformat the rules to display a port range instead
        # of just the port range minimum. This maintains
        # output compatibility with compute.
        for rule in rules:
            rule.port_range_min = _format_network_port_range(rule)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in rules))

    def take_action_compute(self, client, parsed_args):
        column_headers = self._get_column_headers(parsed_args)
        columns = (
            "ID",
            "IP Protocol",
            "IP Range",
            "Port Range",
            "Remote Security Group",
        )

        rules_to_list = []
        if parsed_args.group is not None:
            group = utils.find_resource(
                client.security_groups,
                parsed_args.group,
            )
            rules_to_list = group.rules
        else:
            columns = columns + ('parent_group_id',)
            search = {'all_tenants': parsed_args.all_projects}
            for group in client.security_groups.list(search_opts=search):
                rules_to_list.extend(group.rules)

        # NOTE(rtheis): Turn the raw rules into resources.
        rules = []
        for rule in rules_to_list:
            rules.append(compute_secgroup_rules.SecurityGroupRule(
                client.security_group_rules,
                network_utils.transform_compute_security_group_rule(rule),
            ))

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in rules))


class ShowSecurityGroupRule(common.NetworkAndComputeShowOne):
    """Display security group rule details"""

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
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (columns, data)

    def take_action_compute(self, client, parsed_args):
        # NOTE(rtheis): Unfortunately, compute does not have an API
        # to get or list security group rules so parse through the
        # security groups to find all accessible rules in search of
        # the requested rule.
        obj = None
        security_group_rules = []
        for security_group in client.security_groups.list():
            security_group_rules.extend(security_group.rules)
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
