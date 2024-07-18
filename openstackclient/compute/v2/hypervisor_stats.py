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

"""Hypervisor Stats action implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


def _get_hypervisor_stat_columns(item):
    column_map = {
        # NOTE(gtema): If we decide to use SDK names - empty this
        'disk_available': 'disk_available_least',
        'local_disk_free': 'free_disk_gb',
        'local_disk_size': 'local_gb',
        'local_disk_used': 'local_gb_used',
        'memory_free': 'free_ram_mb',
        'memory_size': 'memory_mb',
        'memory_used': 'memory_mb_used',
    }
    hidden_columns = ['id', 'links', 'location', 'name']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class ShowHypervisorStats(command.ShowOne):
    _description = _("Display hypervisor stats details")

    def take_action(self, parsed_args):
        # The command is deprecated since it is being dropped in Nova.
        self.log.warning(_("This command is deprecated."))
        compute_client = self.app.client_manager.compute
        # We do API request directly cause this deprecated method is not and
        # will not be supported by OpenStackSDK.
        response = compute_client.get(
            '/os-hypervisors/statistics', microversion='2.1'
        )
        hypervisor_stats = response.json().get('hypervisor_statistics')

        display_columns, columns = _get_hypervisor_stat_columns(
            hypervisor_stats
        )
        data = utils.get_dict_properties(hypervisor_stats, columns)
        return (display_columns, data)
