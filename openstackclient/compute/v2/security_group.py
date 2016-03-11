#   Copyright 2012 OpenStack Foundation
#   Copyright 2013 Nebula Inc
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

"""Compute v2 Security Group action implementations"""

try:
    from novaclient.v2 import security_group_rules
except ImportError:
    from novaclient.v1_1 import security_group_rules

from openstackclient.common import command
from openstackclient.common import utils


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


class ListSecurityGroupRule(command.Lister):
    """List security group rules"""

    def get_parser(self, prog_name):
        parser = super(ListSecurityGroupRule, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs='?',
            help='List all rules in this security group (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        columns = column_headers = (
            "ID",
            "IP Protocol",
            "IP Range",
            "Port Range",
            "Remote Security Group",
        )

        rules_to_list = []
        if parsed_args.group:
            group = utils.find_resource(
                compute_client.security_groups,
                parsed_args.group,
            )
            rules_to_list = group.rules
        else:
            columns = columns + ('parent_group_id',)
            column_headers = column_headers + ('Security Group',)
            for group in compute_client.security_groups.list():
                rules_to_list.extend(group.rules)

        # Argh, the rules are not Resources...
        rules = []
        for rule in rules_to_list:
            rules.append(security_group_rules.SecurityGroupRule(
                compute_client.security_group_rules,
                _xform_security_group_rule(rule),
            ))

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in rules))
