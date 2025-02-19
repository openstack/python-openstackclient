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

"""Default Security Group Rule action implementations"""

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import common
from openstackclient.network import utils as network_utils

LOG = logging.getLogger(__name__)


def _get_columns(item):
    hidden_columns = ['location', 'name', 'revision_number']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class CreateDefaultSecurityGroupRule(
    command.ShowOne, common.NeutronCommandWithExtraArgs
):
    """Add a new security group rule to the default security group template.

    These rules will be applied to the default security groups created for any
    new project. They will not be applied to any existing default security
    groups.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set default security group rule description"),
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
            help=_("Rule will apply to incoming network traffic (default)"),
        )
        direction_group.add_argument(
            '--egress',
            action='store_true',
            help=_("Rule will apply to outgoing network traffic"),
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
            help=_("Remote security group (ID)"),
        )
        remote_group.add_argument(
            "--remote-address-group",
            metavar="<group>",
            help=_("Remote address group (ID)"),
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
                "ipv66-encap, ipv6-frag, ipv6-icmp, ipv6-nonxt, ipv6-opts, "
                "ipv6-route, ospf, pgm, rsvp, sctp, tcp, udp, udplite, vrrp "
                "and integer representations [0-255] or any; "
                "default: any (all protocols))"
            ),
        )
        parser.add_argument(
            '--for-default-sg',
            action='store_true',
            default=False,
            help=_(
                "Set this default security group rule to be used in all "
                "default security groups created automatically for each "
                "project"
            ),
        )
        parser.add_argument(
            '--for-custom-sg',
            action='store_true',
            default=False,
            help=_(
                "Set this default security group rule to be used in all "
                "custom security groups created manually by users"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.sdk_connection.network
        # Build the create attributes.
        attrs = {}
        attrs['protocol'] = network_utils.get_protocol(parsed_args)

        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description

        # NOTE: A direction must be specified and ingress
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
            attrs['remote_group_id'] = parsed_args.remote_group
        elif parsed_args.remote_address_group is not None:
            attrs['remote_address_group_id'] = parsed_args.remote_address_group
        elif parsed_args.remote_ip is not None:
            attrs['remote_ip_prefix'] = parsed_args.remote_ip
        elif attrs['ethertype'] == 'IPv4':
            attrs['remote_ip_prefix'] = '0.0.0.0/0'
        elif attrs['ethertype'] == 'IPv6':
            attrs['remote_ip_prefix'] = '::/0'

        attrs['used_in_default_sg'] = parsed_args.for_default_sg
        attrs['used_in_non_default_sg'] = parsed_args.for_custom_sg

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        # Create and show the security group rule.
        obj = client.create_default_security_group_rule(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)


class DeleteDefaultSecurityGroupRule(command.Command):
    """Remove security group rule(s) from the default security group template.

    These rules will not longer be applied to the default security groups
    created for any new project. They will not be removed from any existing
    default security groups.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rule',
            metavar='<rule>',
            nargs="+",
            help=_("Default security group rule(s) to delete (ID only)"),
        )
        return parser

    def take_action(self, parsed_args):
        result = 0
        client = self.app.client_manager.sdk_connection.network
        for r in parsed_args.rule:
            try:
                obj = client.find_default_security_group_rule(
                    r, ignore_missing=False
                )
                client.delete_default_security_group_rule(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete default SG rule with "
                        "ID '%(rule_id)s': %(e)s"
                    ),
                    {'rule_id': r, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.rule)
            msg = _(
                "%(result)s of %(total)s default rules failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListDefaultSecurityGroupRule(command.Lister):
    """List security group rules used for new default security groups.

    This shows the rules that will be added to any new default security groups
    created. These rules may differ for the rules present on existing default
    security groups.
    """

    def _format_network_security_group_rule(self, rule):
        """Transform the SDK DefaultSecurityGroupRule object to a dict

        The SDK object gets in the way of reformatting columns...
        Create port_range column from port_range_min and port_range_max
        """
        rule = rule.to_dict()
        rule['port_range'] = network_utils.format_network_port_range(rule)
        rule['remote_ip_prefix'] = network_utils.format_remote_ip_prefix(rule)
        return rule

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            type=network_utils.convert_to_lowercase,
            help=_(
                "List rules by the IP protocol (ah, dhcp, egp, esp, gre, "
                "icmp, igmp, ipv6-encap, ipv6-frag, ipv6-icmp, "
                "ipv6-nonxt, ipv6-opts, ipv6-route, ospf, pgm, rsvp, "
                "sctp, tcp, udp, udplite, vrrp and integer "
                "representations [0-255] or any; "
                "default: any (all protocols))"
            ),
        )
        parser.add_argument(
            '--ethertype',
            metavar='<ethertype>',
            type=network_utils.convert_to_lowercase,
            help=_("List default rules by the Ethertype (IPv4 or IPv6)"),
        )
        direction_group = parser.add_mutually_exclusive_group()
        direction_group.add_argument(
            '--ingress',
            action='store_true',
            help=_(
                "List default rules which will be applied to incoming "
                "network traffic"
            ),
        )
        direction_group.add_argument(
            '--egress',
            action='store_true',
            help=_(
                "List default rules which will be applied to outgoing "
                "network traffic"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.sdk_connection.network
        column_headers = (
            'ID',
            'IP Protocol',
            'Ethertype',
            'IP Range',
            'Port Range',
            'Direction',
            'Remote Security Group',
            'Remote Address Group',
            'Used in default Security Group',
            'Used in custom Security Group',
        )
        columns = (
            'id',
            'protocol',
            'ether_type',
            'remote_ip_prefix',
            'port_range',
            'direction',
            'remote_group_id',
            'remote_address_group_id',
            'used_in_default_sg',
            'used_in_non_default_sg',
        )

        # Get the security group rules using the requested query.
        query = {}
        if parsed_args.ingress:
            query['direction'] = 'ingress'
        if parsed_args.egress:
            query['direction'] = 'egress'
        if parsed_args.protocol is not None:
            query['protocol'] = parsed_args.protocol

        rules = [
            self._format_network_security_group_rule(r)
            for r in client.default_security_group_rules(**query)
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


class ShowDefaultSecurityGroupRule(command.ShowOne):
    """Show a security group rule used for new default security groups.

    This shows a rule that will be added to any new default security groups
    created. This rule may not be present on existing default security groups.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rule',
            metavar="<rule>",
            help=_("Default security group rule to display (ID only)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.sdk_connection.network
        obj = client.find_default_security_group_rule(
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
