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
