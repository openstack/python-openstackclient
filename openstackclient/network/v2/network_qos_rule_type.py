# Copyright (c) 2016, Intel Corporation.
# All Rights Reserved.
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

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


def _get_columns(item):
    column_map = {
        "type": "rule_type_name",
        "drivers": "drivers",
    }
    hidden_columns = ["id", "location", "name", 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class ListNetworkQosRuleType(command.Lister):
    _description = _("List QoS rule types")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        supported = parser.add_mutually_exclusive_group()
        supported.add_argument(
            '--all-supported',
            action='store_true',
            help=_(
                "List all the QoS rule types supported by any loaded "
                "mechanism drivers (the union of all sets of supported "
                "rules)"
            ),
        )
        supported.add_argument(
            '--all-rules',
            action='store_true',
            help=_(
                "List all QoS rule types implemented in Neutron QoS driver"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = ('type',)
        column_headers = ('Type',)

        args = {}
        if parsed_args.all_supported:
            args['all_supported'] = True
        elif parsed_args.all_rules:
            args['all_rules'] = True
        data = client.qos_rule_types(**args)

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class ShowNetworkQosRuleType(command.ShowOne):
    _description = _("Show details about supported QoS rule type")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rule_type',
            metavar="<qos-rule-type-name>",
            help=_("Name of QoS rule type"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.get_qos_rule_type(parsed_args.rule_type)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data
