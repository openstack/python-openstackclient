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

from openstackclient.common import exceptions
from openstackclient.common import parseractions
from openstackclient.common import utils
from openstackclient.network import common
from openstackclient.network import utils as network_utils


def _format_security_group_rule_show(obj):
    data = network_utils.transform_compute_security_group_rule(obj)
    return zip(*sorted(six.iteritems(data)))


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
        # Until then, continue enforcing the compute choices.
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
            default="0.0.0.0/0",
            help="Source IP address block (may use CIDR notation; default: "
                 "0.0.0.0/0)",
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

    def take_action_network(self, client, parsed_args):
        # Get the security group ID to hold the rule.
        security_group_id = client.find_security_group(
            parsed_args.group,
            ignore_missing=False
        ).id

        # Build the create attributes.
        attrs = {}
        # TODO(rtheis): Add --direction option. Until then, continue
        # with the default of 'ingress'.
        attrs['direction'] = 'ingress'
        # TODO(rtheis): Add --ethertype option. Until then, continue
        # with the default of 'IPv4'
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
        else:
            attrs['remote_ip_prefix'] = parsed_args.src_ip
        attrs['security_group_id'] = security_group_id

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
        if parsed_args.src_group is not None:
            parsed_args.src_group = utils.find_resource(
                client.security_groups,
                parsed_args.src_group,
            ).id
        obj = client.security_group_rules.create(
            group.id,
            parsed_args.proto,
            from_port,
            to_port,
            parsed_args.src_ip,
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
