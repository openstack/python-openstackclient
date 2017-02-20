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
