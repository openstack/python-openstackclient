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

import six

try:
    from novaclient.v2 import security_group_rules as compute_secgroup_rules
except ImportError:
    from novaclient.v1_1 import security_group_rules as compute_secgroup_rules

from openstackclient.common import exceptions
from openstackclient.common import parseractions
from openstackclient.common import utils
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import utils as network_utils


def _format_security_group_rule_show(obj):
    data = network_utils.transform_compute_security_group_rule(obj)
    return zip(*sorted(six.iteritems(data)))


def _format_network_port_range(rule):
    port_range = ''
    if (rule.protocol != 'icmp' and
            (rule.port_range_min or rule.port_range_max)):
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


class CreateSecurityGroupRule(common.NetworkAndComputeShowOne):
    """Create a new security group rule"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Create rule in this security group (name or ID)',
        )
        # TODO(rtheis): Add support for additional protocols for network.
        # Until then, continue enforcing the compute choices. When additional
        # protocols are added, the default ethertype must be determined
        # based on the protocol.
        parser.add_argument(
            "--proto",
            metavar="<proto>",
            default="tcp",
            choices=['icmp', 'tcp', 'udp'],
            type=_convert_to_lowercase,
            help="IP protocol (icmp, tcp, udp; default: tcp)",
        )
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument(
            "--src-ip",
            metavar="<ip-address>",
            help="Source IP address block (may use CIDR notation; "
                 "default for IPv4 rule: 0.0.0.0/0)",
        )
        source_group.add_argument(
            "--src-group",
            metavar="<group>",
            help="Source security group (name or ID)",
        )
        parser.add_argument(
            "--dst-port",
            metavar="<port-range>",
            default=(0, 0),
            action=parseractions.RangeAction,
            help="Destination port, may be a single port or port range: "
                 "137:139 (only required for IP protocols tcp and udp)",
        )
        return parser

    def update_parser_network(self, parser):
        direction_group = parser.add_mutually_exclusive_group()
        direction_group.add_argument(
            '--ingress',
            action='store_true',
            help='Rule applies to incoming network traffic (default)',
        )
        direction_group.add_argument(
            '--egress',
            action='store_true',
            help='Rule applies to outgoing network traffic',
        )
        parser.add_argument(
            '--ethertype',
            metavar='<ethertype>',
            choices=['IPv4', 'IPv6'],
            help='Ethertype of network traffic '
                 '(IPv4, IPv6; default: IPv4)',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help="Owner's project (name or ID)"
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action_network(self, client, parsed_args):
        # Get the security group ID to hold the rule.
        security_group_id = client.find_security_group(
            parsed_args.group,
            ignore_missing=False
        ).id

        # Build the create attributes.
        attrs = {}
        # NOTE(rtheis): A direction must be specified and ingress
        # is the default.
        if parsed_args.ingress or not parsed_args.egress:
            attrs['direction'] = 'ingress'
        if parsed_args.egress:
            attrs['direction'] = 'egress'
        if parsed_args.ethertype:
            attrs['ethertype'] = parsed_args.ethertype
        else:
            # NOTE(rtheis): Default based on protocol is IPv4 for now.
            # Once IPv6 protocols are added, this will need to be updated.
            attrs['ethertype'] = 'IPv4'
        # TODO(rtheis): Add port range support (type and code) for icmp
        # protocol. Until then, continue ignoring the port range.
        if parsed_args.proto != 'icmp':
            attrs['port_range_min'] = parsed_args.dst_port[0]
            attrs['port_range_max'] = parsed_args.dst_port[1]
        attrs['protocol'] = parsed_args.proto
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
        if parsed_args.proto == 'icmp':
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
            parsed_args.proto,
            from_port,
            to_port,
            src_ip,
            parsed_args.src_group,
        )
        return _format_security_group_rule_show(obj._info)


class DeleteSecurityGroupRule(common.NetworkAndComputeCommand):
    """Delete a security group rule"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'rule',
            metavar='<rule>',
            help='Security group rule to delete (ID only)',
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group_rule(parsed_args.rule)
        client.delete_security_group_rule(obj)

    def take_action_compute(self, client, parsed_args):
        client.security_group_rules.delete(parsed_args.rule)


class ListSecurityGroupRule(common.NetworkAndComputeLister):
    """List security group rules"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs='?',
            help='List all rules in this security group (name or ID)',
        )
        return parser

    def _get_column_headers(self, parsed_args):
        column_headers = (
            'ID',
            'IP Protocol',
            'IP Range',
            'Port Range',
            'Remote Security Group',
        )
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
            'remote_group_id',
        )

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
            for group in client.security_groups.list():
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
            help="Security group rule to display (ID only)"
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
            msg = "Could not find security group rule " \
                  "with ID %s" % parsed_args.rule
            raise exceptions.CommandError(msg)

        # NOTE(rtheis): Format security group rule
        return _format_security_group_rule_show(obj)
