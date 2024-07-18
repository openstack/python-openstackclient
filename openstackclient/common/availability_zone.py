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

"""Availability Zone action implementations"""

import copy
import logging

from openstack import exceptions as sdk_exceptions
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _xform_compute_availability_zone(az, include_extra):
    result = []
    zone_info = {
        'zone_name': az.name,
        'zone_status': (
            'available' if az.state['available'] else 'not available'
        ),
    }

    if not include_extra:
        result.append(zone_info)
        return result

    if az.hosts:
        for host, services in az.hosts.items():
            host_info = copy.deepcopy(zone_info)
            host_info['host_name'] = host

            for svc, state in services.items():
                info = copy.deepcopy(host_info)
                info['service_name'] = svc
                info['service_status'] = '{} {} {}'.format(
                    'enabled' if state['active'] else 'disabled',
                    ':-)' if state['available'] else 'XXX',
                    state['updated_at'],
                )
                result.append(info)
    else:
        zone_info['host_name'] = ''
        zone_info['service_name'] = ''
        zone_info['service_status'] = ''
        result.append(zone_info)
    return result


def _xform_volume_availability_zone(az):
    result = []
    zone_info = {
        'zone_name': az.name,
        'zone_status': (
            'available' if az.state['available'] else 'not available'
        ),
    }
    result.append(zone_info)
    return result


def _xform_network_availability_zone(az):
    result = []
    zone_info = {}
    zone_info['zone_name'] = az.name
    zone_info['zone_status'] = az.state
    if 'unavailable' == zone_info['zone_status']:
        zone_info['zone_status'] = 'not available'
    zone_info['zone_resource'] = az.resource
    result.append(zone_info)
    return result


class ListAvailabilityZone(command.Lister):
    _description = _("List availability zones and their status")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--compute',
            action='store_true',
            default=False,
            help=_('List compute availability zones'),
        )
        parser.add_argument(
            '--network',
            action='store_true',
            default=False,
            help=_('List network availability zones'),
        )
        parser.add_argument(
            '--volume',
            action='store_true',
            default=False,
            help=_('List volume availability zones'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def _get_compute_availability_zones(self, parsed_args):
        compute_client = self.app.client_manager.compute
        try:
            data = list(compute_client.availability_zones(details=True))
        except sdk_exceptions.ForbiddenException:  # policy doesn't allow
            try:
                data = compute_client.availability_zones(details=False)
            except Exception:
                raise

        result = []
        for zone in data:
            result += _xform_compute_availability_zone(zone, parsed_args.long)
        return result

    def _get_volume_availability_zones(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume
        data = []
        try:
            data = list(volume_client.availability_zones())
        except Exception as e:
            LOG.debug('Volume availability zone exception: %s', e)
            if parsed_args.volume:
                message = _(
                    "Availability zones list not supported by "
                    "Block Storage API"
                )
                LOG.warning(message)

        result = []
        for zone in data:
            result += _xform_volume_availability_zone(zone)
        return result

    def _get_network_availability_zones(self, parsed_args):
        network_client = self.app.client_manager.network
        try:
            # Verify that the extension exists.
            network_client.find_extension(
                'Availability Zone', ignore_missing=False
            )
        except Exception as e:
            LOG.debug('Network availability zone exception: ', e)
            if parsed_args.network:
                message = _(
                    "Availability zones list not supported by Network API"
                )
                LOG.warning(message)
            return []

        result = []
        for zone in network_client.availability_zones():
            result += _xform_network_availability_zone(zone)
        return result

    def take_action(self, parsed_args):
        columns: tuple[str, ...] = ('Zone Name', 'Zone Status')
        if parsed_args.long:
            columns += (
                'Zone Resource',
                'Host Name',
                'Service Name',
                'Service Status',
            )

        # Show everything by default.
        show_all = (
            not parsed_args.compute
            and not parsed_args.volume
            and not parsed_args.network
        )

        result = []
        if parsed_args.compute or show_all:
            result += self._get_compute_availability_zones(parsed_args)
        if parsed_args.volume or show_all:
            result += self._get_volume_availability_zones(parsed_args)
        if parsed_args.network or show_all:
            result += self._get_network_availability_zones(parsed_args)

        return (
            columns,
            (utils.get_dict_properties(s, columns) for s in result),
        )
