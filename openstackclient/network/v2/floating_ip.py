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

"""IP Floating action implementations"""

import logging

from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import common


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    network_client = client_manager.network

    # Name of a network could be empty string.
    if parsed_args.network is not None:
        network = network_client.find_network(parsed_args.network,
                                              ignore_missing=False)
        attrs['floating_network_id'] = network.id

    if parsed_args.subnet:
        subnet = network_client.find_subnet(parsed_args.subnet,
                                            ignore_missing=False)
        attrs['subnet_id'] = subnet.id

    if parsed_args.port:
        port = network_client.find_port(parsed_args.port,
                                        ignore_missing=False)
        attrs['port_id'] = port.id

    if parsed_args.floating_ip_address:
        attrs['floating_ip_address'] = parsed_args.floating_ip_address

    if parsed_args.fixed_ip_address:
        attrs['fixed_ip_address'] = parsed_args.fixed_ip_address

    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description

    return attrs


class CreateFloatingIP(common.NetworkAndComputeShowOne):
    """Create floating IP"""

    def update_parser_common(self, parser):
        # In Compute v2 network, floating IPs could be allocated from floating
        # IP pools, which are actually external networks. So deprecate the
        # parameter "pool", and use "network" instead.
        parser.add_argument(
            'network',
            metavar='<network>',
            help=_("Network to allocate floating IP from (name or ID)")
        )
        return parser

    def update_parser_network(self, parser):
        parser.add_argument(
            '--subnet',
            metavar='<subnet>',
            help=_("Subnet on which you want to create the floating IP "
                   "(name or ID)")
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_("Port to be associated with the floating IP "
                   "(name or ID)")
        )
        parser.add_argument(
            '--floating-ip-address',
            metavar='<floating-ip-address>',
            dest='floating_ip_address',
            help=_("Floating IP address")
        )
        parser.add_argument(
            '--fixed-ip-address',
            metavar='<fixed-ip-address>',
            dest='fixed_ip_address',
            help=_("Fixed IP address mapped to the floating IP")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set floating IP description')
        )
        return parser

    def take_action_network(self, client, parsed_args):
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_ip(**attrs)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = client.floating_ips.create(parsed_args.network)
        columns = _get_columns(obj._info)
        data = utils.get_dict_properties(obj._info, columns)
        return (columns, data)


class CreateIPFloating(CreateFloatingIP):
    """Create floating IP"""

    # TODO(tangchen): Remove this class and ``ip floating create`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action_network(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip create" instead.'))
        return super(CreateIPFloating, self).take_action_network(
            client, parsed_args)

    def take_action_compute(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip create" instead.'))
        return super(CreateIPFloating, self).take_action_compute(
            client, parsed_args)


class DeleteFloatingIP(common.NetworkAndComputeDelete):
    """Delete floating IP(s)"""

    # Used by base class to find resources in parsed_args.
    resource = 'floating_ip'
    r = None

    def update_parser_common(self, parser):
        parser.add_argument(
            'floating_ip',
            metavar="<floating-ip>",
            nargs="+",
            help=_("Floating IP(s) to delete (IP address or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_ip(self.r, ignore_missing=False)
        client.delete_ip(obj)

    def take_action_compute(self, client, parsed_args):
        obj = utils.find_resource(client.floating_ips, self.r)
        client.floating_ips.delete(obj.id)


class DeleteIPFloating(DeleteFloatingIP):
    """Delete floating IP(s)"""

    # TODO(tangchen): Remove this class and ``ip floating delete`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action_network(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip delete" instead.'))
        return super(DeleteIPFloating, self).take_action_network(
            client, parsed_args)

    def take_action_compute(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip delete" instead.'))
        return super(DeleteIPFloating, self).take_action_compute(
            client, parsed_args)


class ListFloatingIP(common.NetworkAndComputeLister):
    """List floating IP(s)"""

    def take_action_network(self, client, parsed_args):
        columns = (
            'id',
            'floating_ip_address',
            'fixed_ip_address',
            'port_id',
        )
        headers = (
            'ID',
            'Floating IP Address',
            'Fixed IP Address',
            'Port',
        )

        query = {}
        data = client.ips(**query)

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))

    def take_action_compute(self, client, parsed_args):
        columns = (
            'ID',
            'IP',
            'Fixed IP',
            'Instance ID',
            'Pool',
        )
        headers = (
            'ID',
            'Floating IP Address',
            'Fixed IP Address',
            'Server',
            'Pool',
        )

        data = client.floating_ips.list()

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ListIPFloating(ListFloatingIP):
    """List floating IP(s)"""

    # TODO(tangchen): Remove this class and ``ip floating list`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action_network(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip list" instead.'))
        return super(ListIPFloating, self).take_action_network(
            client, parsed_args)

    def take_action_compute(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip list" instead.'))
        return super(ListIPFloating, self).take_action_compute(
            client, parsed_args)


class ShowFloatingIP(common.NetworkAndComputeShowOne):
    """Display floating IP details"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'floating_ip',
            metavar="<floating-ip>",
            help=_("Floating IP to display (IP address or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_ip(parsed_args.floating_ip, ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = utils.find_resource(
            client.floating_ips,
            parsed_args.floating_ip,
        )
        columns = _get_columns(obj._info)
        data = utils.get_dict_properties(obj._info, columns)
        return (columns, data)


class ShowIPFloating(ShowFloatingIP):
    """Display floating IP details"""

    # TODO(tangchen): Remove this class and ``ip floating show`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action_network(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip show" instead.'))
        return super(ShowIPFloating, self).take_action_network(
            client, parsed_args)

    def take_action_compute(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip show" instead.'))
        return super(ShowIPFloating, self).take_action_compute(
            client, parsed_args)
