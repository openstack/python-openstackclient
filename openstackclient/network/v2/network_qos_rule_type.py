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

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import sdk_utils


_formatters = {
    'location': format_columns.DictColumn,
}


def _get_columns(item):
    column_map = {
        "type": "rule_type_name",
        "drivers": "drivers",
    }
    invisible_columns = ["id", "name"]
    return sdk_utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, invisible_columns)


class ListNetworkQosRuleType(command.Lister):
    _description = _("List QoS rule types")

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'type',
        )
        column_headers = (
            'Type',
        )
        data = client.qos_rule_types()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters={},
                ) for s in data))


class ShowNetworkQosRuleType(command.ShowOne):
    _description = _("Show details about supported QoS rule type")

    def get_parser(self, prog_name):
        parser = super(ShowNetworkQosRuleType, self).get_parser(prog_name)
        parser.add_argument(
            'rule_type',
            metavar="<qos-rule-type-name>",
            help=_("Name of QoS rule type")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.get_qos_rule_type(parsed_args.rule_type)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return display_columns, data
