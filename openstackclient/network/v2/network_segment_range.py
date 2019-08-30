# Copyright (c) 2019, Intel Corporation.
# All Rights Reserved.
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

"""Network segment action implementations"""

import itertools
import logging

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import sdk_utils


LOG = logging.getLogger(__name__)

_formatters = {
    'location': format_columns.DictColumn,
}


def _get_columns(item):
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, {})


def _get_ranges(item):
    item = [int(i) if isinstance(i, six.string_types) else i for i in item]
    for a, b in itertools.groupby(enumerate(item), lambda xy: xy[1] - xy[0]):
        b = list(b)
        yield "%s-%s" % (b[0][1], b[-1][1]) if b[0][1] != b[-1][1] else \
            str(b[0][1])


def _hack_tuple_value_update_by_index(tup, index, value):
    lot = list(tup)
    lot[index] = value
    return tuple(lot)


def _is_prop_empty(columns, props, prop_name):
    return True if not props[columns.index(prop_name)] else False


def _exchange_dict_keys_with_values(orig_dict):
    updated_dict = dict()
    for k, v in six.iteritems(orig_dict):
        k = [k]
        if not updated_dict.get(v):
            updated_dict[v] = k
        else:
            updated_dict[v].extend(k)
    return updated_dict


def _update_available_from_props(columns, props):
    index_available = columns.index('available')
    props = _hack_tuple_value_update_by_index(
        props, index_available, list(_get_ranges(props[index_available])))
    return props


def _update_used_from_props(columns, props):
    index_used = columns.index('used')
    updated_used = _exchange_dict_keys_with_values(props[index_used])
    for k, v in six.iteritems(updated_used):
        updated_used[k] = list(_get_ranges(v))
    props = _hack_tuple_value_update_by_index(
        props, index_used, updated_used)
    return props


def _update_additional_fields_from_props(columns, props):
    props = _update_available_from_props(columns, props)
    props = _update_used_from_props(columns, props)
    return props


class CreateNetworkSegmentRange(command.ShowOne):
    _description = _("Create new network segment range")

    def get_parser(self, prog_name):
        parser = super(CreateNetworkSegmentRange, self).get_parser(prog_name)
        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            "--private",
            dest="private",
            action="store_true",
            help=_('Network segment range is assigned specifically to the '
                   'project'),
        )
        shared_group.add_argument(
            "--shared",
            dest="shared",
            action="store_true",
            help=_('Network segment range is shared with other projects'),
        )
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of new network segment range')
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Network segment range owner (name or ID). Optional when '
                   'the segment range is shared'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--network-type',
            metavar='<network-type>',
            choices=['geneve', 'gre', 'vlan', 'vxlan'],
            required=True,
            help=_('Network type of this network segment range '
                   '(geneve, gre, vlan or vxlan)'),
        )
        parser.add_argument(
            '--physical-network',
            metavar='<physical-network-name>',
            help=_('Physical network name of this network segment range'),
        )
        parser.add_argument(
            '--minimum',
            metavar='<minimum-segmentation-id>',
            type=int,
            required=True,
            help=_('Minimum segment identifier for this network segment '
                   'range which is based on the network type, VLAN ID for '
                   'vlan network type and tunnel ID for geneve, gre and vxlan '
                   'network types'),
        )
        parser.add_argument(
            '--maximum',
            metavar='<maximum-segmentation-id>',
            type=int,
            required=True,
            help=_('Maximum segment identifier for this network segment '
                   'range which is based on the network type, VLAN ID for '
                   'vlan network type and tunnel ID for geneve, gre and vxlan '
                   'network types'),
        )

        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        try:
            # Verify that the extension exists.
            network_client.find_extension('network-segment-range',
                                          ignore_missing=False)
        except Exception as e:
            msg = (_('Network segment range create not supported by '
                     'Network API: %(e)s') % {'e': e})
            raise exceptions.CommandError(msg)

        identity_client = self.app.client_manager.identity

        if not parsed_args.private and parsed_args.project:
            msg = _("--project is only allowed with --private")
            raise exceptions.CommandError(msg)

        if (parsed_args.network_type.lower() != 'vlan' and
                parsed_args.physical_network):
            msg = _("--physical-network is only allowed with --network-type "
                    "vlan")
            raise exceptions.CommandError(msg)

        attrs = {}
        if parsed_args.shared or parsed_args.private:
            attrs['shared'] = parsed_args.shared
        else:
            # default to be ``shared`` if not specified
            attrs['shared'] = True
        attrs['network_type'] = parsed_args.network_type
        attrs['minimum'] = parsed_args.minimum
        attrs['maximum'] = parsed_args.maximum
        if parsed_args.name:
            attrs['name'] = parsed_args.name

        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            if project_id:
                attrs['project_id'] = project_id
            else:
                msg = (_("Failed to create the network segment range for "
                         "project %(project_id)s") % parsed_args.project_id)
                raise exceptions.CommandError(msg)
        elif not attrs['shared']:
            # default to the current project if no project specified and shared
            # is not specified.
            # Get the project id from the current auth.
            attrs['project_id'] = self.app.client_manager.auth_ref.project_id

        if parsed_args.physical_network:
            attrs['physical_network'] = parsed_args.physical_network
        obj = network_client.create_network_segment_range(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        data = _update_additional_fields_from_props(columns, props=data)
        return (display_columns, data)


class DeleteNetworkSegmentRange(command.Command):
    _description = _("Delete network segment range(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteNetworkSegmentRange, self).get_parser(prog_name)
        parser.add_argument(
            'network_segment_range',
            metavar='<network-segment-range>',
            nargs='+',
            help=_('Network segment range(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        try:
            # Verify that the extension exists.
            network_client.find_extension('network-segment-range',
                                          ignore_missing=False)
        except Exception as e:
            msg = (_('Network segment range delete not supported by '
                     'Network API: %(e)s') % {'e': e})
            raise exceptions.CommandError(msg)

        result = 0
        for network_segment_range in parsed_args.network_segment_range:
            try:
                obj = network_client.find_network_segment_range(
                    network_segment_range, ignore_missing=False)
                network_client.delete_network_segment_range(obj)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete network segment range with "
                            "ID '%(network_segment_range)s': %(e)s"),
                          {'network_segment_range': network_segment_range,
                           'e': e})

        if result > 0:
            total = len(parsed_args.network_segment_range)
            msg = (_("%(result)s of %(total)s network segment ranges failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListNetworkSegmentRange(command.Lister):
    _description = _("List network segment ranges")

    def get_parser(self, prog_name):
        parser = super(ListNetworkSegmentRange, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_('List additional fields in output'),
        )
        used_group = parser.add_mutually_exclusive_group()
        used_group.add_argument(
            '--used',
            action='store_true',
            help=_('List network segment ranges that have segments in use'),
        )
        used_group.add_argument(
            '--unused',
            action='store_true',
            help=_('List network segment ranges that have segments '
                   'not in use'),
        )
        available_group = parser.add_mutually_exclusive_group()
        available_group.add_argument(
            '--available',
            action='store_true',
            help=_('List network segment ranges that have available segments'),
        )
        available_group.add_argument(
            '--unavailable',
            action='store_true',
            help=_('List network segment ranges without available segments'),
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        try:
            # Verify that the extension exists.
            network_client.find_extension('network-segment-range',
                                          ignore_missing=False)
        except Exception as e:
            msg = (_('Network segment ranges list not supported by '
                     'Network API: %(e)s') % {'e': e})
            raise exceptions.CommandError(msg)

        filters = {}
        data = network_client.network_segment_ranges(**filters)

        headers = (
            'ID',
            'Name',
            'Default',
            'Shared',
            'Project ID',
            'Network Type',
            'Physical Network',
            'Minimum ID',
            'Maximum ID'
        )
        columns = (
            'id',
            'name',
            'default',
            'shared',
            'project_id',
            'network_type',
            'physical_network',
            'minimum',
            'maximum',
        )
        if parsed_args.available or parsed_args.unavailable or \
                parsed_args.used or parsed_args.unused:
            # If one of `--available`, `--unavailable`, `--used`,
            # `--unused` is specified, we assume that additional fields
            # should be listed in output.
            parsed_args.long = True
        if parsed_args.long:
            headers = headers + (
                'Used',
                'Available',
            )
            columns = columns + (
                'used',
                'available',
            )

        display_props = tuple()
        for s in data:
            props = utils.get_item_properties(s, columns)
            if parsed_args.available and \
                    _is_prop_empty(columns, props, 'available') or \
               parsed_args.unavailable and \
                    not _is_prop_empty(columns, props, 'available') or \
               parsed_args.used and _is_prop_empty(columns, props, 'used') or \
               parsed_args.unused and \
                    not _is_prop_empty(columns, props, 'used'):
                continue
            if parsed_args.long:
                props = _update_additional_fields_from_props(columns, props)
            display_props += (props,)

        return headers, display_props


class SetNetworkSegmentRange(command.Command):
    _description = _("Set network segment range properties")

    def get_parser(self, prog_name):
        parser = super(SetNetworkSegmentRange, self).get_parser(prog_name)
        parser.add_argument(
            'network_segment_range',
            metavar='<network-segment-range>',
            help=_('Network segment range to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set network segment name'),
        )
        parser.add_argument(
            '--minimum',
            metavar='<minimum-segmentation-id>',
            type=int,
            help=_('Set network segment range minimum segment identifier'),
        )
        parser.add_argument(
            '--maximum',
            metavar='<maximum-segmentation-id>',
            type=int,
            help=_('Set network segment range maximum segment identifier'),
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        try:
            # Verify that the extension exists.
            network_client.find_extension('network-segment-range',
                                          ignore_missing=False)
        except Exception as e:
            msg = (_('Network segment range set not supported by '
                     'Network API: %(e)s') % {'e': e})
            raise exceptions.CommandError(msg)

        if (parsed_args.minimum and not parsed_args.maximum) or \
                (parsed_args.maximum and not parsed_args.minimum):
            msg = _("--minimum and --maximum are both required")
            raise exceptions.CommandError(msg)

        obj = network_client.find_network_segment_range(
            parsed_args.network_segment_range, ignore_missing=False)
        attrs = {}
        if parsed_args.name:
            attrs['name'] = parsed_args.name
        if parsed_args.minimum:
            attrs['minimum'] = parsed_args.minimum
        if parsed_args.maximum:
            attrs['maximum'] = parsed_args.maximum
        network_client.update_network_segment_range(obj, **attrs)


class ShowNetworkSegmentRange(command.ShowOne):
    _description = _("Display network segment range details")

    def get_parser(self, prog_name):
        parser = super(ShowNetworkSegmentRange, self).get_parser(prog_name)
        parser.add_argument(
            'network_segment_range',
            metavar='<network-segment-range>',
            help=_('Network segment range to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        try:
            # Verify that the extension exists.
            network_client.find_extension('network-segment-range',
                                          ignore_missing=False)
        except Exception as e:
            msg = (_('Network segment range show not supported by '
                     'Network API: %(e)s') % {'e': e})
            raise exceptions.CommandError(msg)

        obj = network_client.find_network_segment_range(
            parsed_args.network_segment_range,
            ignore_missing=False
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        data = _update_additional_fields_from_props(columns, props=data)
        return (display_columns, data)
