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

import argparse
from collections.abc import Iterable, Sequence
from typing import Any

from openstack.network.v2 import qos_rule_type as _qos_rule_type
from osc_lib import utils

from openstackclient import command
from openstackclient.common import pagination
from openstackclient.i18n import _


def _get_columns(
    item: _qos_rule_type.QoSRuleType,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
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

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
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
        pagination.add_marker_pagination_option_to_parser(parser)
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], Iterable[tuple[Any, ...]]]:
        client = self.app.client_manager.network
        columns = ('type',)
        column_headers = ('Type',)

        filters = {}
        if parsed_args.marker is not None:
            filters['marker'] = parsed_args.marker
        if parsed_args.limit is not None:
            filters['limit'] = parsed_args.limit
        if parsed_args.max_items is not None:
            filters['max_items'] = parsed_args.max_items
        if parsed_args.all_supported:
            filters['all_supported'] = True
        elif parsed_args.all_rules:
            filters['all_rules'] = True
        data = client.qos_rule_types(**filters)

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

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rule_type',
            metavar="<qos-rule-type-name>",
            help=_("Name of QoS rule type"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        obj = client.get_qos_rule_type(parsed_args.rule_type)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data
