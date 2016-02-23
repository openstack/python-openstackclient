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
from openstackclient.common import utils
from openstackclient.network import common


def _xform_security_group_rule(sgroup):
    info = {}
    info.update(sgroup)
    from_port = info.pop('from_port')
    to_port = info.pop('to_port')
    if isinstance(from_port, int) and isinstance(to_port, int):
        port_range = {'port_range': "%u:%u" % (from_port, to_port)}
    elif from_port is None and to_port is None:
        port_range = {'port_range': ""}
    else:
        port_range = {'port_range': "%s:%s" % (from_port, to_port)}
    info.update(port_range)
    if 'cidr' in info['ip_range']:
        info['ip_range'] = info['ip_range']['cidr']
    else:
        info['ip_range'] = ''
    if info['ip_protocol'] is None:
        info['ip_protocol'] = ''
    elif info['ip_protocol'].lower() == 'icmp':
        info['port_range'] = ''
    group = info.pop('group')
    if 'name' in group:
        info['remote_security_group'] = group['name']
    else:
        info['remote_security_group'] = ''
    return info


def _format_security_group_rule_show(obj):
    data = _xform_security_group_rule(obj)
    return zip(*sorted(six.iteritems(data)))


def _get_columns(item):
    columns = item.keys()
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


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
