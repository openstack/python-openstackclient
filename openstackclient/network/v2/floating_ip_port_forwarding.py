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

"""Floating IP Port Forwarding action implementations"""

import logging
import typing as ty

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import common

LOG = logging.getLogger(__name__)


def validate_ports_diff(ports):
    if len(ports) == 0:
        return 0

    ports_diff = ports[-1] - ports[0]
    if ports_diff < 0:
        msg = _(
            "The last number in port range must be"
            " greater or equal to the first"
        )
        raise exceptions.CommandError(msg)
    return ports_diff


def validate_ports_match(internal_ports, external_ports):
    internal_ports_diff = validate_ports_diff(internal_ports)
    external_ports_diff = validate_ports_diff(external_ports)

    if internal_ports_diff != 0 and internal_ports_diff != external_ports_diff:
        msg = _(
            "The relation between internal and external ports does not "
            "match the pattern 1:N and N:N"
        )
        raise exceptions.CommandError(msg)


def validate_and_assign_port_ranges(parsed_args, attrs):
    internal_port_range = parsed_args.internal_protocol_port
    external_port_range = parsed_args.external_protocol_port
    external_ports = internal_ports = []
    if external_port_range:
        external_ports = list(map(int, str(external_port_range).split(':')))
    if internal_port_range:
        internal_ports = list(map(int, str(internal_port_range).split(':')))

    validate_ports_match(internal_ports, external_ports)

    for port in external_ports + internal_ports:
        validate_port(port)

    if internal_port_range:
        if ':' in internal_port_range:
            attrs['internal_port_range'] = internal_port_range
        else:
            attrs['internal_port'] = int(internal_port_range)

    if external_port_range:
        if ':' in external_port_range:
            attrs['external_port_range'] = external_port_range
        else:
            attrs['external_port'] = int(external_port_range)


def validate_port(port):
    if port <= 0 or port > 65535:
        msg = _("The port number range is <1-65535>")
        raise exceptions.CommandError(msg)


def _get_columns(item):
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class CreateFloatingIPPortForwarding(
    command.ShowOne, common.NeutronCommandWithExtraArgs
):
    _description = _("Create floating IP port forwarding")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--internal-ip-address',
            required=True,
            metavar='<internal-ip-address>',
            help=_(
                "The fixed IPv4 address of the network "
                "port associated to the floating IP port forwarding"
            ),
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            required=True,
            help=_(
                "The name or ID of the network port associated "
                "to the floating IP port forwarding"
            ),
        )
        parser.add_argument(
            '--internal-protocol-port',
            metavar='<port-number>',
            required=True,
            help=_(
                "The protocol port number "
                "of the network port fixed IPv4 address "
                "associated to the floating IP port forwarding"
            ),
        )
        parser.add_argument(
            '--external-protocol-port',
            metavar='<port-number>',
            required=True,
            help=_(
                "The protocol port number of "
                "the port forwarding's floating IP address"
            ),
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            required=True,
            help=_(
                "The protocol used in the floating IP "
                "port forwarding, for instance: TCP, UDP"
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                "Text to describe/contextualize the use of the "
                "port forwarding configuration"
            ),
        )
        parser.add_argument(
            'floating_ip',
            metavar='<floating-ip>',
            help=_(
                "Floating IP that the port forwarding belongs to "
                "(IP address or ID)"
            ),
        )

        return parser

    def take_action(self, parsed_args):
        attrs: dict[str, ty.Any] = {}
        client = self.app.client_manager.network
        floating_ip = client.find_ip(
            parsed_args.floating_ip,
            ignore_missing=False,
        )

        validate_and_assign_port_ranges(parsed_args, attrs)

        if parsed_args.port:
            port = client.find_port(parsed_args.port, ignore_missing=False)
            attrs['internal_port_id'] = port.id
        attrs['internal_ip_address'] = parsed_args.internal_ip_address
        attrs['protocol'] = parsed_args.protocol

        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        obj = client.create_floating_ip_port_forwarding(
            floating_ip.id, **attrs
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)


class DeleteFloatingIPPortForwarding(command.Command):
    _description = _("Delete floating IP port forwarding")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'floating_ip',
            metavar='<floating-ip>',
            help=_(
                "Floating IP that the port forwarding belongs to "
                "(IP address or ID)"
            ),
        )
        parser.add_argument(
            'port_forwarding_id',
            nargs="+",
            metavar="<port-forwarding-id>",
            help=_("The ID of the floating IP port forwarding(s) to delete"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        floating_ip = client.find_ip(
            parsed_args.floating_ip,
            ignore_missing=False,
        )
        result = 0

        for port_forwarding_id in parsed_args.port_forwarding_id:
            try:
                client.delete_floating_ip_port_forwarding(
                    floating_ip.id,
                    port_forwarding_id,
                    ignore_missing=False,
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete floating IP port forwarding "
                        "'%(port_forwarding_id)s': %(e)s"
                    ),
                    {'port_forwarding_id': port_forwarding_id, 'e': e},
                )
        if result > 0:
            total = len(parsed_args.port_forwarding_id)
            msg = _(
                "%(result)s of %(total)s Port forwarding failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListFloatingIPPortForwarding(command.Lister):
    _description = _("List floating IP port forwarding")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'floating_ip',
            metavar='<floating-ip>',
            help=_(
                "Floating IP that the port forwarding belongs to "
                "(IP address or ID)"
            ),
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_(
                "Filter the list result by the ID or name of "
                "the internal network port"
            ),
        )
        parser.add_argument(
            '--external-protocol-port',
            metavar='<port-number>',
            dest='external_protocol_port',
            help=_(
                "Filter the list result by the "
                "protocol port number of the floating IP"
            ),
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            help=_("Filter the list result by the port protocol"),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'id',
            'internal_port_id',
            'internal_ip_address',
            'internal_port',
            'internal_port_range',
            'external_port',
            'external_port_range',
            'protocol',
            'description',
        )
        headers = (
            'ID',
            'Internal Port ID',
            'Internal IP Address',
            'Internal Port',
            'Internal Port Range',
            'External Port',
            'External Port Range',
            'Protocol',
            'Description',
        )

        query = {}

        if parsed_args.port:
            port = client.find_port(parsed_args.port, ignore_missing=False)
            query['internal_port_id'] = port.id
        external_port = parsed_args.external_protocol_port
        if external_port:
            if ':' in external_port:
                query['external_port_range'] = external_port
            else:
                query['external_port'] = int(
                    parsed_args.external_protocol_port
                )
        if parsed_args.protocol is not None:
            query['protocol'] = parsed_args.protocol

        obj = client.find_ip(
            parsed_args.floating_ip,
            ignore_missing=False,
        )

        data = client.floating_ip_port_forwardings(obj, **query)

        return (
            headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class SetFloatingIPPortForwarding(common.NeutronCommandWithExtraArgs):
    _description = _("Set floating IP Port Forwarding Properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'floating_ip',
            metavar='<floating-ip>',
            help=_(
                "Floating IP that the port forwarding belongs to "
                "(IP address or ID)"
            ),
        )
        parser.add_argument(
            'port_forwarding_id',
            metavar='<port-forwarding-id>',
            help=_("The ID of the floating IP port forwarding"),
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_(
                "The ID of the network port associated to "
                "the floating IP port forwarding"
            ),
        )
        parser.add_argument(
            '--internal-ip-address',
            metavar='<internal-ip-address>',
            help=_(
                "The fixed IPv4 address of the network port "
                "associated to the floating IP port forwarding"
            ),
        )
        parser.add_argument(
            '--internal-protocol-port',
            metavar='<port-number>',
            help=_(
                "The TCP/UDP/other protocol port number of the "
                "network port fixed IPv4 address associated to "
                "the floating IP port forwarding"
            ),
        )
        parser.add_argument(
            '--external-protocol-port',
            metavar='<port-number>',
            help=_(
                "The TCP/UDP/other protocol port number of the "
                "port forwarding's floating IP address"
            ),
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            choices=['tcp', 'udp'],
            help=_("The IP protocol used in the floating IP port forwarding"),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                "Text to describe/contextualize the use of "
                "the port forwarding configuration"
            ),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        floating_ip = client.find_ip(
            parsed_args.floating_ip,
            ignore_missing=False,
        )

        attrs = {}
        if parsed_args.port:
            port = client.find_port(parsed_args.port, ignore_missing=False)
            attrs['internal_port_id'] = port.id

        if parsed_args.internal_ip_address:
            attrs['internal_ip_address'] = parsed_args.internal_ip_address

        validate_and_assign_port_ranges(parsed_args, attrs)

        if parsed_args.protocol:
            attrs['protocol'] = parsed_args.protocol

        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        client.update_floating_ip_port_forwarding(
            floating_ip.id, parsed_args.port_forwarding_id, **attrs
        )


class ShowFloatingIPPortForwarding(command.ShowOne):
    _description = _("Display floating IP Port Forwarding details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'floating_ip',
            metavar='<floating-ip>',
            help=_(
                "Floating IP that the port forwarding belongs to "
                "(IP address or ID)"
            ),
        )
        parser.add_argument(
            'port_forwarding_id',
            metavar="<port-forwarding-id>",
            help=_("The ID of the floating IP port forwarding"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        floating_ip = client.find_ip(
            parsed_args.floating_ip,
            ignore_missing=False,
        )
        obj = client.find_floating_ip_port_forwarding(
            floating_ip,
            parsed_args.port_forwarding_id,
            ignore_missing=False,
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)
