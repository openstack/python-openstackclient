#   Copyright 2012-2013 OpenStack Foundation
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

"""Hypervisor action implementations"""

import json
import re

from openstack import exceptions as sdk_exceptions
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _


def _get_hypervisor_columns(item, client):
    column_map = {'name': 'hypervisor_hostname'}
    hidden_columns = ['location', 'servers']

    if sdk_utils.supports_microversion(client, '2.88'):
        hidden_columns.extend(
            [
                'current_workload',
                'disk_available',
                'local_disk_free',
                'local_disk_size',
                'local_disk_used',
                'memory_free',
                'memory_size',
                'memory_used',
                'running_vms',
                'vcpus_used',
                'vcpus',
            ]
        )
    else:
        column_map.update(
            {
                'disk_available': 'disk_available_least',
                'local_disk_free': 'free_disk_gb',
                'local_disk_size': 'local_gb',
                'local_disk_used': 'local_gb_used',
                'memory_free': 'free_ram_mb',
                'memory_used': 'memory_mb_used',
                'memory_size': 'memory_mb',
            }
        )

    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class ListHypervisor(command.Lister):
    _description = _("List hypervisors")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--matching',
            metavar='<hostname>',
            help=_(
                "Filter hypervisors using <hostname> substring"
                "Hypervisor Type and Host IP are not returned "
                "when using microversion 2.52 or lower"
            ),
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        list_opts = {}

        if parsed_args.matching and (parsed_args.marker or parsed_args.limit):
            msg = _('--matching is not compatible with --marker or --limit')
            raise exceptions.CommandError(msg)

        if parsed_args.marker:
            if not sdk_utils.supports_microversion(compute_client, '2.33'):
                msg = _(
                    '--os-compute-api-version 2.33 or greater is required to '
                    'support the --marker option'
                )
                raise exceptions.CommandError(msg)
            list_opts['marker'] = parsed_args.marker

        if parsed_args.limit:
            if not sdk_utils.supports_microversion(compute_client, '2.33'):
                msg = _(
                    '--os-compute-api-version 2.33 or greater is required to '
                    'support the --limit option'
                )
                raise exceptions.CommandError(msg)
            list_opts['limit'] = parsed_args.limit

        if parsed_args.matching:
            list_opts['hypervisor_hostname_pattern'] = parsed_args.matching

        column_headers: tuple[str, ...] = (
            "ID",
            "Hypervisor Hostname",
            "Hypervisor Type",
            "Host IP",
            "State",
        )
        columns: tuple[str, ...] = (
            'id',
            'name',
            'hypervisor_type',
            'host_ip',
            'state',
        )

        if parsed_args.long:
            if not sdk_utils.supports_microversion(compute_client, '2.88'):
                column_headers += (
                    'vCPUs Used',
                    'vCPUs',
                    'Memory MB Used',
                    'Memory MB',
                )
                columns += (
                    'vcpus_used',
                    'vcpus',
                    'memory_used',
                    'memory_size',
                )

        data = compute_client.hypervisors(**list_opts, details=True)

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowHypervisor(command.ShowOne):
    _description = _("Display hypervisor details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "hypervisor",
            metavar="<hypervisor>",
            help=_("Hypervisor to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        hypervisor_id = compute_client.find_hypervisor(
            parsed_args.hypervisor, ignore_missing=False, details=False
        ).id
        hypervisor = compute_client.get_hypervisor(hypervisor_id).copy()

        # Some of the properties in the hypervisor object need to be processed
        # before they get reported to the user. We spend this section
        # extracting the relevant details to be reported by modifying our
        # copy of the hypervisor object.
        aggregates = compute_client.aggregates()
        hypervisor['aggregates'] = list()
        service_details = hypervisor['service_details']

        if aggregates:
            # Hypervisors in nova cells are prefixed by "<cell>@"
            if "@" in service_details['host']:
                cell, service_host = service_details['host'].split('@', 1)
            else:
                cell = None
                service_host = service_details['host']

            if cell:
                # The host aggregates are also prefixed by "<cell>@"
                member_of = [
                    aggregate.name
                    for aggregate in aggregates
                    if cell in aggregate.name
                    and service_host in aggregate.hosts
                ]
            else:
                member_of = [
                    aggregate.name
                    for aggregate in aggregates
                    if service_host in aggregate.hosts
                ]
            hypervisor['aggregates'] = member_of

        try:
            if sdk_utils.supports_microversion(compute_client, '2.88'):
                uptime = hypervisor['uptime'] or ''
                del hypervisor['uptime']
            else:
                del hypervisor['uptime']
                uptime = compute_client.get_hypervisor_uptime(
                    hypervisor['id']
                )['uptime']
            # Extract data from uptime value
            # format: 0 up 0,  0 users,  load average: 0, 0, 0
            # example: 17:37:14 up  2:33,  3 users,
            #          load average: 0.33, 0.36, 0.34
            m = re.match(
                r"\s*(.+)\sup\s+(.+),\s+(.+)\susers?,\s+load average:\s(.+)",
                uptime,
            )
            if m:
                hypervisor['host_time'] = m.group(1)
                hypervisor['uptime'] = m.group(2)
                hypervisor['users'] = m.group(3)
                hypervisor['load_average'] = m.group(4)
        except sdk_exceptions.HttpException as exc:
            if exc.status_code != 501:
                raise

        hypervisor['service_id'] = service_details['id']
        hypervisor['service_host'] = service_details['host']
        del hypervisor['service_details']

        if not sdk_utils.supports_microversion(compute_client, '2.28'):
            # microversion 2.28 transformed this to a JSON blob rather than a
            # string; on earlier fields, do this manually
            hypervisor['cpu_info'] = json.loads(hypervisor['cpu_info'] or '{}')
        display_columns, columns = _get_hypervisor_columns(
            hypervisor, compute_client
        )
        data = utils.get_dict_properties(
            hypervisor,
            columns,
            formatters={
                'cpu_info': format_columns.DictColumn,
            },
        )

        return display_columns, data
