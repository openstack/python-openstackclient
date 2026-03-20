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

"""Security Group Rule action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import utils as network_utils

LOG = logging.getLogger(__name__)


def _get_columns(item: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    hidden_columns = ['location', 'name', 'tenant_id', 'tags']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateSecurityGroupRule(
    command.ShowOne, common.NeutronCommandWithExtraArgs
):
    _description = _("Create a new security group rule")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Create rule in this security group (name or ID)"),
        )
        remote_group = parser.add_mutually_exclusive_group()
        remote_group.add_argument(
            "--remote-ip",
            metavar="<ip-address>",
            help=_(
                "Remote IP address block (may use CIDR notation; "
                "default for IPv4 rule: 0.0.0.0/0, "
                "default for IPv6 rule: ::/0)"
            ),
        )
        remote_group.add_argument(
            "--remote-group",
            metavar="<group>",
            help=_("Remote security group (name or ID)"),
        )
        remote_group.add_argument(
            "--remote-address-group",
            metavar="<group>",
            help=_("Remote address group (name or ID)"),
        )
        parser.add_argument(
            '--dst-port',
            metavar='<port-range>',
            action=parseractions.RangeAction,
            help=_(
                "Destination port, may be a single port or a starting and "
                "ending port range: 137:139. Required for IP protocols TCP "
                "and UDP. Ignored for ICMP IP protocols."
            ),
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            type=network_utils.convert_to_lowercase,
            help=_(
                "IP protocol (ah, dccp, egp, esp, gre, icmp, igmp, "
                "ipv6-encap, ipv6-frag, ipv6-icmp, ipv6-nonxt, ipv6-opts, "
                "ipv6-route, ospf, pgm, rsvp, sctp, tcp, udp, udplite, vrrp "
                "and integer representations [0-255] or any; "
                "default: any (all protocols))"
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set security group rule description"),
        )
        parser.add_argument(
            '--icmp-type',
            metavar='<icmp-type>',
            type=int,
            help=_("ICMP type for ICMP IP protocols"),
        )
        parser.add_argument(
            '--icmp-code',
            metavar='<icmp-code>',
            type=int,
            help=_("ICMP code for ICMP IP protocols"),
        )
        direction_group = parser.add_mutually_exclusive_group()
        direction_group.add_argument(
            '--ingress',
            action='store_true',
            help=_("Rule applies to incoming network traffic (default)"),
        )
        direction_group.add_argument(
            '--egress',
            action='store_true',
            help=_("Rule applies to outgoing network traffic"),
        )
        parser.add_argument(
            '--ethertype',
            metavar='<ethertype>',
            choices=['IPv4', 'IPv6'],
            type=network_utils.convert_ipvx_case,
            help=_(
                "Ethertype of network traffic "
                "(IPv4, IPv6; default: based on IP protocol)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        # Get the security group ID to hold the rule.
        security_group_id = client.find_security_group(
            parsed_args.group, ignore_missing=False
        ).id

        # Build the create attributes.
        attrs = {}
        attrs['protocol'] = network_utils.get_protocol(parsed_args)

        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description

        # NOTE(rtheis): A direction must be specified and ingress
        # is the default.
        if parsed_args.ingress or not parsed_args.egress:
            attrs['direction'] = 'ingress'
        if parsed_args.egress:
            attrs['direction'] = 'egress'

        # NOTE(rtheis): Use ethertype specified else default based
        # on IP protocol.
        attrs['ethertype'] = network_utils.get_ethertype(
            parsed_args, attrs['protocol']
        )

        # NOTE(rtheis): Validate the port range and ICMP type and code.
        # It would be ideal if argparse could do this.
        if parsed_args.dst_port and (
            parsed_args.icmp_type or parsed_args.icmp_code
        ):
            msg = _(
                'Argument --dst-port not allowed with arguments '
                '--icmp-type and --icmp-code'
            )
            raise exceptions.CommandError(msg)
        if parsed_args.icmp_type is None and parsed_args.icmp_code is not None:
            msg = _('Argument --icmp-type required with argument --icmp-code')
            raise exceptions.CommandError(msg)
        is_icmp_protocol = network_utils.is_icmp_protocol(attrs['protocol'])
        if not is_icmp_protocol and (
            parsed_args.icmp_type or parsed_args.icmp_code
        ):
            msg = _(
                'ICMP IP protocol required with arguments '
                '--icmp-type and --icmp-code'
            )
            raise exceptions.CommandError(msg)
        # NOTE(rtheis): For backwards compatibility, continue ignoring
        # the destination port range when an ICMP IP protocol is specified.
        if parsed_args.dst_port and not is_icmp_protocol:
            attrs['port_range_min'] = parsed_args.dst_port[0]
            attrs['port_range_max'] = parsed_args.dst_port[1]
        if parsed_args.icmp_type is not None and parsed_args.icmp_type >= 0:
            attrs['port_range_min'] = parsed_args.icmp_type
        if parsed_args.icmp_code is not None and parsed_args.icmp_code >= 0:
            attrs['port_range_max'] = parsed_args.icmp_code

        if parsed_args.remote_group is not None:
            attrs['remote_group_id'] = client.find_security_group(
                parsed_args.remote_group, ignore_missing=False
            ).id
        elif parsed_args.remote_address_group is not None:
            attrs['remote_address_group_id'] = client.find_address_group(
                parsed_args.remote_address_group, ignore_missing=False
            ).id
        elif parsed_args.remote_ip is not None:
            attrs['remote_ip_prefix'] = parsed_args.remote_ip
        elif attrs['ethertype'] == 'IPv4':
            attrs['remote_ip_prefix'] = '0.0.0.0/0'
        elif attrs['ethertype'] == 'IPv6':
            attrs['remote_ip_prefix'] = '::/0'
        attrs['security_group_id'] = security_group_id
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['project_id'] = project_id

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        # Create and show the security group rule.
        obj = client.create_security_group_rule(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)


class DeleteSecurityGroupRule(command.Command):
    _description = _("Delete security group rule(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rule',
            metavar='<rule>',
            nargs="+",
            help=_("Security group rule(s) to delete (ID only)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        result = 0

        for rule in parsed_args.rule:
            try:
                obj = client.find_security_group_rule(
                    rule, ignore_missing=False
                )
                client.delete_security_group_rule(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete security group rule with "
                        "name or ID '%(rule)s': %(e)s"
                    ),
                    {'rule': rule, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.rule)
            msg = _("%(result)s of %(total)s rules failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListSecurityGroupRule(command.Lister):
    _description = _("List security group rules")

    def _format_network_security_group_rule(self, rule: Any) -> dict[str, Any]:
        """Transform the SDK SecurityGroupRule object to a dict

        The SDK object gets in the way of reformatting columns...
        Create port_range column from port_range_min and port_range_max
        """
        data: dict[str, Any] = rule.to_dict()
        data['port_range'] = network_utils.format_network_port_range(data)
        data['remote_ip_prefix'] = network_utils.format_remote_ip_prefix(data)
        return data

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs='?',
            help=_("List all rules in this security group (name or ID)"),
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            type=network_utils.convert_to_lowercase,
            help=_(
                "List only rules with the specified IP protocol "
                "(ah, dhcp, egp, esp, gre, icmp, igmp, ipv6-encap, "
                "ipv6-frag, ipv6-icmp, ipv6-nonxt, ipv6-opts, ipv6-route, "
                "ospf, pgm, rsvp, sctp, tcp, udp, udplite, vrrp and integer "
                "representations [0-255] or any; "
                "default: any (all protocols))"
            ),
        )
        parser.add_argument(
            '--ethertype',
            metavar='<ethertype>',
            type=network_utils.convert_to_lowercase,
            help=_(
                "List only rules with the specified Ethertype (IPv4 or IPv6)"
            ),
        )
        direction_group = parser.add_mutually_exclusive_group()
        direction_group.add_argument(
            '--ingress',
            action='store_true',
            help=_("List only rules applied to incoming network traffic"),
        )
        direction_group.add_argument(
            '--egress',
            action='store_true',
            help=_("List only rules applied to outgoing network traffic"),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("**Deprecated** This argument is no longer needed"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List only rules with the specified project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def _get_column_headers(
        self, parsed_args: argparse.Namespace
    ) -> tuple[str, ...]:
        column_headers: tuple[str, ...] = (
            'ID',
            'IP Protocol',
            'Ethertype',
            'IP Range',
            'Port Range',
            'Direction',
            'Remote Security Group',
            'Remote Address Group',
        )
        if parsed_args.group is None:
            column_headers += ('Security Group',)
        return column_headers

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        if parsed_args.long:
            msg = _(
                "The --long option has been deprecated and is no longer needed"
            )
            self.log.warning(msg)

        column_headers = self._get_column_headers(parsed_args)
        columns: tuple[str, ...] = (
            'id',
            'protocol',
            'ether_type',
            'remote_ip_prefix',
            'port_range',
            'direction',
            'remote_group_id',
            'remote_address_group_id',
        )

        # Get the security group rules using the requested query.
        query = {}
        if parsed_args.group is not None:
            # NOTE(rtheis): Unfortunately, the security group resource
            # does not contain security group rules resources. So use
            # the security group ID in a query to get the resources.
            security_group_id = client.find_security_group(
                parsed_args.group, ignore_missing=False
            ).id
            query = {'security_group_id': security_group_id}
        else:
            columns += ('security_group_id',)

        if parsed_args.ingress:
            query['direction'] = 'ingress'
        if parsed_args.egress:
            query['direction'] = 'egress'
        if parsed_args.protocol is not None:
            query['protocol'] = parsed_args.protocol
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            query['project_id'] = project_id

        rules = [
            self._format_network_security_group_rule(r)
            for r in client.security_group_rules(**query)
        ]

        return (
            column_headers,
            (
                utils.get_dict_properties(
                    s,
                    columns,
                )
                for s in rules
            ),
        )


class ShowSecurityGroupRule(command.ShowOne):
    _description = _("Display security group rule details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rule',
            metavar="<rule>",
            help=_("Security group rule to display (ID only)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        obj = client.find_security_group_rule(
            parsed_args.rule, ignore_missing=False
        )
        # necessary for old rules that have None in this field
        if not obj['remote_ip_prefix']:
            obj['remote_ip_prefix'] = network_utils.format_remote_ip_prefix(
                obj
            )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)
