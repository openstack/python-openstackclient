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

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateNetworkSegment(command.ShowOne):
    """Create new network segment"""

    def get_parser(self, prog_name):
        parser = super(CreateNetworkSegment, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('New network segment name')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Network segment description'),
        )
        parser.add_argument(
            '--physical-network',
            metavar='<physical-network>',
            help=_('Physical network name of this network segment'),
        )
        parser.add_argument(
            '--segment',
            metavar='<segment>',
            type=int,
            help=_('Segment identifier for this network segment which is '
                   'based on the network type, VLAN ID for vlan network '
                   'type and tunnel ID for geneve, gre and vxlan network '
                   'types'),
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            required=True,
            help=_('Network this network segment belongs to (name or ID)'),
        )
        parser.add_argument(
            '--network-type',
            metavar='<network-type>',
            choices=['flat', 'geneve', 'gre', 'local', 'vlan', 'vxlan'],
            required=True,
            help=_('Network type of this network segment '
                   '(flat, geneve, gre, local, vlan or vxlan)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        attrs['name'] = parsed_args.name
        attrs['network_id'] = client.find_network(parsed_args.network,
                                                  ignore_missing=False).id
        attrs['network_type'] = parsed_args.network_type
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        if parsed_args.physical_network is not None:
            attrs['physical_network'] = parsed_args.physical_network
        if parsed_args.segment is not None:
            attrs['segmentation_id'] = parsed_args.segment
        obj = client.create_segment(**attrs)
        columns = tuple(sorted(obj.keys()))
        data = utils.get_item_properties(obj, columns)
        return (columns, data)


class DeleteNetworkSegment(command.Command):
    """Delete network segment(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteNetworkSegment, self).get_parser(prog_name)
        parser.add_argument(
            'network_segment',
            metavar='<network-segment>',
            nargs='+',
            help=_('Network segment(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        result = 0
        for network_segment in parsed_args.network_segment:
            try:
                obj = client.find_segment(network_segment,
                                          ignore_missing=False)
                client.delete_segment(obj)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete network segment with "
                            "ID '%(network_segment)s': %(e)s")
                          % {'network_segment': network_segment, 'e': e})

        if result > 0:
            total = len(parsed_args.network_segment)
            msg = (_("%(result)s of %(total)s network segments failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListNetworkSegment(command.Lister):
    """List network segments"""

    def get_parser(self, prog_name):
        parser = super(ListNetworkSegment, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            help=_('List network segments that belong to this '
                   'network (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        filters = {}
        if parsed_args.network:
            _network = network_client.find_network(
                parsed_args.network,
                ignore_missing=False
            )
            filters = {'network_id': _network.id}
        data = network_client.segments(**filters)

        headers = (
            'ID',
            'Name',
            'Network',
            'Network Type',
            'Segment',
        )
        columns = (
            'id',
            'name',
            'network_id',
            'network_type',
            'segmentation_id',
        )
        if parsed_args.long:
            headers = headers + (
                'Physical Network',
            )
            columns = columns + (
                'physical_network',
            )

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetNetworkSegment(command.Command):
    """Set network segment properties"""

    def get_parser(self, prog_name):
        parser = super(SetNetworkSegment, self).get_parser(prog_name)
        parser.add_argument(
            'network_segment',
            metavar='<network-segment>',
            help=_('Network segment to modify (name or ID)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set network segment description'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set network segment name'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_segment(parsed_args.network_segment,
                                  ignore_missing=False)
        attrs = {}
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        client.update_segment(obj, **attrs)


class ShowNetworkSegment(command.ShowOne):
    """Display network segment details"""

    def get_parser(self, prog_name):
        parser = super(ShowNetworkSegment, self).get_parser(prog_name)
        parser.add_argument(
            'network_segment',
            metavar='<network-segment>',
            help=_('Network segment to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_segment(
            parsed_args.network_segment,
            ignore_missing=False
        )
        columns = tuple(sorted(obj.keys()))
        data = utils.get_item_properties(obj, columns)
        return (columns, data)
