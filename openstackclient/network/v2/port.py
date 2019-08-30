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

"""Port action implementations"""

import argparse
import copy
import json
import logging

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import sdk_utils
from openstackclient.network.v2 import _tag


LOG = logging.getLogger(__name__)


class AdminStateColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return 'UP' if self._value else 'DOWN'


_formatters = {
    'admin_state_up': AdminStateColumn,
    'is_admin_state_up': AdminStateColumn,
    'allowed_address_pairs': format_columns.ListDictColumn,
    'binding_profile': format_columns.DictColumn,
    'binding_vif_details': format_columns.DictColumn,
    'binding:profile': format_columns.DictColumn,
    'binding:vif_details': format_columns.DictColumn,
    'dns_assignment': format_columns.ListDictColumn,
    'extra_dhcp_opts': format_columns.ListDictColumn,
    'fixed_ips': format_columns.ListDictColumn,
    'location': format_columns.DictColumn,
    'security_group_ids': format_columns.ListColumn,
    'tags': format_columns.ListColumn,
}


def _get_columns(item):
    column_map = {
        'binding:host_id': 'binding_host_id',
        'binding:profile': 'binding_profile',
        'binding:vif_details': 'binding_vif_details',
        'binding:vif_type': 'binding_vif_type',
        'binding:vnic_type': 'binding_vnic_type',
        'is_admin_state_up': 'admin_state_up',
        'is_port_security_enabled': 'port_security_enabled',
        'tenant_id': 'project_id',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


class JSONKeyValueAction(argparse.Action):
    """A custom action to parse arguments as JSON or key=value pairs

    Ensures that ``dest`` is a dict
    """

    def __call__(self, parser, namespace, values, option_string=None):

        # Make sure we have an empty dict rather than None
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, {})

        # Try to load JSON first before falling back to <key>=<value>.
        current_dest = getattr(namespace, self.dest)
        try:
            current_dest.update(json.loads(values))
        except ValueError as e:
            if '=' in values:
                current_dest.update([values.split('=', 1)])
            else:
                msg = _("Expected '<key>=<value>' or JSON data for option "
                        "%(option)s, but encountered JSON parsing error: "
                        "%(error)s") % {"option": option_string, "error": e}
                raise argparse.ArgumentTypeError(msg)


def _get_attrs(client_manager, parsed_args):
    attrs = {}

    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if parsed_args.device:
        attrs['device_id'] = parsed_args.device
    if parsed_args.device_owner is not None:
        attrs['device_owner'] = parsed_args.device_owner
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    if parsed_args.vnic_type is not None:
        attrs['binding:vnic_type'] = parsed_args.vnic_type
    if parsed_args.host:
        attrs['binding:host_id'] = parsed_args.host
    if parsed_args.mac_address is not None:
        attrs['mac_address'] = parsed_args.mac_address

    if parsed_args.dns_domain is not None:
        attrs['dns_domain'] = parsed_args.dns_domain
    if parsed_args.dns_name is not None:
        attrs['dns_name'] = parsed_args.dns_name
    # It is possible that name is not updated during 'port set'
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    # The remaining options do not support 'port set' command, so they require
    # additional check
    if 'network' in parsed_args and parsed_args.network is not None:
        attrs['network_id'] = parsed_args.network
    if 'project' in parsed_args and parsed_args.project is not None:
        # TODO(singhj): since 'project' logic is common among
        # router, network, port etc., maybe move it to a common file.
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    if parsed_args.disable_port_security:
        attrs['port_security_enabled'] = False

    if parsed_args.enable_port_security:
        attrs['port_security_enabled'] = True

    if 'no_qos_policy' in parsed_args and parsed_args.no_qos_policy:
        attrs['qos_policy_id'] = None

    if parsed_args.qos_policy:
        attrs['qos_policy_id'] = client_manager.network.find_qos_policy(
            parsed_args.qos_policy, ignore_missing=False).id

    if ('enable_uplink_status_propagation' in parsed_args and
            parsed_args.enable_uplink_status_propagation):
        attrs['propagate_uplink_status'] = True
    if ('disable_uplink_status_propagation' in parsed_args and
            parsed_args.disable_uplink_status_propagation):
        attrs['propagate_uplink_status'] = False

    return attrs


def _prepare_fixed_ips(client_manager, parsed_args):
    """Fix and properly format fixed_ip option.

    Appropriately convert any subnet names to their respective ids.
    Convert fixed_ips in parsed args to be in valid dictionary format:
    {'subnet': 'foo'}.
    """
    client = client_manager.network
    ips = []

    if parsed_args.fixed_ip:
        for ip_spec in parsed_args.fixed_ip:
            if 'subnet' in ip_spec:
                subnet_name_id = ip_spec['subnet']
                if subnet_name_id:
                    _subnet = client.find_subnet(subnet_name_id,
                                                 ignore_missing=False)
                    ip_spec['subnet_id'] = _subnet.id
                    del ip_spec['subnet']

            if 'ip-address' in ip_spec:
                ip_spec['ip_address'] = ip_spec['ip-address']
                del ip_spec['ip-address']

            ips.append(ip_spec)

    if ips:
        parsed_args.fixed_ip = ips


def _prepare_filter_fixed_ips(client_manager, parsed_args):
    """Fix and properly format fixed_ip option for filtering.

    Appropriately convert any subnet names to their respective ids.
    Convert fixed_ips in parsed args to be in valid list format for filter:
    ['subnet_id=foo'].
    """
    client = client_manager.network
    ips = []

    for ip_spec in parsed_args.fixed_ip:
        if 'subnet' in ip_spec:
            subnet_name_id = ip_spec['subnet']
            if subnet_name_id:
                _subnet = client.find_subnet(subnet_name_id,
                                             ignore_missing=False)
                ips.append('subnet_id=%s' % _subnet.id)

        if 'ip-address' in ip_spec:
            ips.append('ip_address=%s' % ip_spec['ip-address'])

        if 'ip-substring' in ip_spec:
            ips.append('ip_address_substr=%s' % ip_spec['ip-substring'])
    return ips


def _add_updatable_args(parser):
    parser.add_argument(
        '--description',
        metavar='<description>',
        help=_("Description of this port")
    )
    parser.add_argument(
        '--device',
        metavar='<device-id>',
        help=_("Port device ID")
    )
    parser.add_argument(
        '--mac-address',
        metavar='<mac-address>',
        help=_("MAC address of this port (admin only)")
    )
    parser.add_argument(
        '--device-owner',
        metavar='<device-owner>',
        help=_("Device owner of this port. This is the entity that uses "
               "the port (for example, network:dhcp).")
    )
    parser.add_argument(
        '--vnic-type',
        metavar='<vnic-type>',
        choices=['direct', 'direct-physical', 'macvtap',
                 'normal', 'baremetal', 'virtio-forwarder'],
        help=_("VNIC type for this port (direct | direct-physical | "
               "macvtap | normal | baremetal | virtio-forwarder, "
               "default: normal)")
    )
    parser.add_argument(
        '--host',
        metavar='<host-id>',
        help=_("Allocate port on host <host-id> (ID only)")
    )
    parser.add_argument(
        '--dns-domain',
        metavar='dns-domain',
        help=_("Set DNS domain to this port "
               "(requires dns_domain extension for ports)")
    )
    parser.add_argument(
        '--dns-name',
        metavar='<dns-name>',
        help=_("Set DNS name for this port "
               "(requires DNS integration extension)")
    )


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
def _convert_address_pairs(parsed_args):
    ops = []
    for opt in parsed_args.allowed_address_pairs:
        addr = {}
        addr['ip_address'] = opt['ip-address']
        if 'mac-address' in opt:
            addr['mac_address'] = opt['mac-address']
        ops.append(addr)
    return ops


def _convert_extra_dhcp_options(parsed_args):
    dhcp_options = []
    for opt in parsed_args.extra_dhcp_options:
        option = {}
        option['opt_name'] = opt['name']
        if 'value' in opt:
            option['opt_value'] = opt['value']
        if 'ip-version' in opt:
            option['ip_version'] = opt['ip-version']
        dhcp_options.append(option)
    return dhcp_options


class CreatePort(command.ShowOne):
    _description = _("Create a new port")

    def get_parser(self, prog_name):
        parser = super(CreatePort, self).get_parser(prog_name)

        parser.add_argument(
            '--network',
            metavar='<network>',
            required=True,
            help=_("Network this port belongs to (name or ID)")
        )
        _add_updatable_args(parser)
        fixed_ip = parser.add_mutually_exclusive_group()
        fixed_ip.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            help=_("Desired IP and/or subnet for this port (name or ID): "
                   "subnet=<subnet>,ip-address=<ip-address> "
                   "(repeat option to set multiple fixed IP addresses)")
        )
        fixed_ip.add_argument(
            '--no-fixed-ip',
            action='store_true',
            help=_("No IP or subnet for this port.")
        )
        parser.add_argument(
            '--binding-profile',
            metavar='<binding-profile>',
            action=JSONKeyValueAction,
            help=_("Custom data to be passed as binding:profile. Data may "
                   "be passed as <key>=<value> or JSON. "
                   "(repeat option to set multiple binding:profile data)")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help=_("Enable port (default)")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable port")
        )
        uplink_status_group = parser.add_mutually_exclusive_group()
        uplink_status_group.add_argument(
            '--enable-uplink-status-propagation',
            action='store_true',
            help=_("Enable uplink status propagate")
        )
        uplink_status_group.add_argument(
            '--disable-uplink-status-propagation',
            action='store_true',
            help=_("Disable uplink status propagate (default)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("Name of this port")
        )
        parser.add_argument(
            '--extra-dhcp-option',
            metavar='name=<name>[,value=<value>,ip-version={4,6}]',
            default=[],
            action=parseractions.MultiKeyValueCommaAction,
            dest='extra_dhcp_options',
            required_keys=['name'],
            optional_keys=['value', "ip-version"],
            help=_('Extra DHCP options to be assigned to this port: '
                   'name=<name>[,value=<value>,ip-version={4,6}] '
                   '(repeat option to set multiple extra DHCP options)'))

        secgroups = parser.add_mutually_exclusive_group()
        secgroups.add_argument(
            '--security-group',
            metavar='<security-group>',
            action='append',
            dest='security_group',
            help=_("Security group to associate with this port (name or ID) "
                   "(repeat option to set multiple security groups)")
        )
        secgroups.add_argument(
            '--no-security-group',
            dest='no_security_group',
            action='store_true',
            help=_("Associate no security groups with this port")
        )
        parser.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("Attach QoS policy to this port (name or ID)")
        )
        port_security = parser.add_mutually_exclusive_group()
        port_security.add_argument(
            '--enable-port-security',
            action='store_true',
            help=_("Enable port security for this port (Default)")
        )
        port_security.add_argument(
            '--disable-port-security',
            action='store_true',
            help=_("Disable port security for this port")
        )
        parser.add_argument(
            '--allowed-address',
            metavar='ip-address=<ip-address>[,mac-address=<mac-address>]',
            action=parseractions.MultiKeyValueAction,
            dest='allowed_address_pairs',
            required_keys=['ip-address'],
            optional_keys=['mac-address'],
            help=_("Add allowed-address pair associated with this port: "
                   "ip-address=<ip-address>[,mac-address=<mac-address>] "
                   "(repeat option to set multiple allowed-address pairs)")
        )
        _tag.add_tag_option_to_parser_for_create(parser, _('port'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        _network = client.find_network(parsed_args.network,
                                       ignore_missing=False)
        parsed_args.network = _network.id
        _prepare_fixed_ips(self.app.client_manager, parsed_args)
        attrs = _get_attrs(self.app.client_manager, parsed_args)

        if parsed_args.binding_profile is not None:
            attrs['binding:profile'] = parsed_args.binding_profile

        if parsed_args.fixed_ip:
            attrs['fixed_ips'] = parsed_args.fixed_ip
        elif parsed_args.no_fixed_ip:
            attrs['fixed_ips'] = []

        if parsed_args.security_group:
            attrs['security_group_ids'] = [client.find_security_group(
                                           sg, ignore_missing=False).id
                                           for sg in
                                           parsed_args.security_group]
        elif parsed_args.no_security_group:
            attrs['security_group_ids'] = []

        if parsed_args.allowed_address_pairs:
            attrs['allowed_address_pairs'] = (
                _convert_address_pairs(parsed_args))

        if parsed_args.extra_dhcp_options:
            attrs["extra_dhcp_opts"] = _convert_extra_dhcp_options(parsed_args)

        if parsed_args.qos_policy:
            attrs['qos_policy_id'] = client.find_qos_policy(
                parsed_args.qos_policy, ignore_missing=False).id
        with common.check_missing_extension_if_error(
                self.app.client_manager.network, attrs):
            obj = client.create_port(**attrs)

        # tags cannot be set when created, so tags need to be set later.
        _tag.update_tags_for_set(client, obj, parsed_args)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        return (display_columns, data)


class DeletePort(command.Command):
    _description = _("Delete port(s)")

    def get_parser(self, prog_name):
        parser = super(DeletePort, self).get_parser(prog_name)
        parser.add_argument(
            'port',
            metavar="<port>",
            nargs="+",
            help=_("Port(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for port in parsed_args.port:
            try:
                obj = client.find_port(port, ignore_missing=False)
                client.delete_port(obj)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete port with "
                            "name or ID '%(port)s': %(e)s"),
                          {'port': port, 'e': e})

        if result > 0:
            total = len(parsed_args.port)
            msg = (_("%(result)s of %(total)s ports failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


# TODO(abhiraut): Use only the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListPort(command.Lister):
    _description = _("List ports")

    def get_parser(self, prog_name):
        parser = super(ListPort, self).get_parser(prog_name)
        parser.add_argument(
            '--device-owner',
            metavar='<device-owner>',
            help=_("List only ports with the specified device owner. "
                   "This is the entity that uses the port (for example, "
                   "network:dhcp).")
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            help=_("List only ports connected to this network (name or ID)"))
        device_group = parser.add_mutually_exclusive_group()
        device_group.add_argument(
            '--router',
            metavar='<router>',
            dest='router',
            help=_("List only ports attached to this router (name or ID)")
        )
        device_group.add_argument(
            '--server',
            metavar='<server>',
            help=_("List only ports attached to this server (name or ID)"),
        )
        device_group.add_argument(
            '--device-id',
            metavar='<device-id>',
            help=_("List only ports with the specified device ID")
        )
        parser.add_argument(
            '--mac-address',
            metavar='<mac-address>',
            help=_("List only ports with this MAC address")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List ports according to their project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--fixed-ip',
            metavar=('subnet=<subnet>,ip-address=<ip-address>,'
                     'ip-substring=<ip-substring>'),
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address', 'ip-substring'],
            help=_("Desired IP and/or subnet for filtering ports "
                   "(name or ID): subnet=<subnet>,ip-address=<ip-address>,"
                   "ip-substring=<ip-substring> "
                   "(repeat option to set multiple fixed IP addresses)"),
        )
        _tag.add_tag_filtering_option_to_parser(parser, _('ports'))
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        identity_client = self.app.client_manager.identity

        columns = (
            'id',
            'name',
            'mac_address',
            'fixed_ips',
            'status',
        )
        column_headers = (
            'ID',
            'Name',
            'MAC Address',
            'Fixed IP Addresses',
            'Status',
        )

        filters = {}
        if parsed_args.long:
            columns += ('security_group_ids', 'device_owner', 'tags')
            column_headers += ('Security Groups', 'Device Owner', 'Tags')
        if parsed_args.device_owner is not None:
            filters['device_owner'] = parsed_args.device_owner
        if parsed_args.device_id is not None:
            filters['device_id'] = parsed_args.device_id
        if parsed_args.router:
            _router = network_client.find_router(parsed_args.router,
                                                 ignore_missing=False)
            filters['device_id'] = _router.id
        if parsed_args.server:
            compute_client = self.app.client_manager.compute
            server = utils.find_resource(compute_client.servers,
                                         parsed_args.server)
            filters['device_id'] = server.id
        if parsed_args.network:
            network = network_client.find_network(parsed_args.network,
                                                  ignore_missing=False)
            filters['network_id'] = network.id
        if parsed_args.mac_address:
            filters['mac_address'] = parsed_args.mac_address
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            filters['tenant_id'] = project_id
            filters['project_id'] = project_id
        if parsed_args.fixed_ip:
            filters['fixed_ips'] = _prepare_filter_fixed_ips(
                self.app.client_manager, parsed_args)

        _tag.get_tag_filtering_args(parsed_args, filters)

        data = network_client.ports(**filters)

        headers, attrs = utils.calculate_header_and_attrs(
            column_headers, columns, parsed_args)
        return (headers,
                (utils.get_item_properties(
                    s, attrs,
                    formatters=_formatters,
                ) for s in data))


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetPort(command.Command):
    _description = _("Set port properties")

    def get_parser(self, prog_name):
        parser = super(SetPort, self).get_parser(prog_name)
        _add_updatable_args(parser)
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=None,
            help=_("Enable port")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable port")
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help=_("Set port name")
        )
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            help=_("Desired IP and/or subnet for this port (name or ID): "
                   "subnet=<subnet>,ip-address=<ip-address> "
                   "(repeat option to set multiple fixed IP addresses)")
        )
        parser.add_argument(
            '--no-fixed-ip',
            action='store_true',
            help=_("Clear existing information of fixed IP addresses."
                   "Specify both --fixed-ip and --no-fixed-ip "
                   "to overwrite the current fixed IP addresses.")
        )
        parser.add_argument(
            '--binding-profile',
            metavar='<binding-profile>',
            action=JSONKeyValueAction,
            help=_("Custom data to be passed as binding:profile. Data may "
                   "be passed as <key>=<value> or JSON. "
                   "(repeat option to set multiple binding:profile data)")
        )
        parser.add_argument(
            '--no-binding-profile',
            action='store_true',
            help=_("Clear existing information of binding:profile. "
                   "Specify both --binding-profile and --no-binding-profile "
                   "to overwrite the current binding:profile information.")
        )
        parser.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("Attach QoS policy to this port (name or ID)")
        )
        parser.add_argument(
            'port',
            metavar="<port>",
            help=_("Port to modify (name or ID)")
        )
        parser.add_argument(
            '--security-group',
            metavar='<security-group>',
            action='append',
            dest='security_group',
            help=_("Security group to associate with this port (name or ID) "
                   "(repeat option to set multiple security groups)")
        )
        parser.add_argument(
            '--no-security-group',
            dest='no_security_group',
            action='store_true',
            help=_("Clear existing security groups associated with this port")
        )
        port_security = parser.add_mutually_exclusive_group()
        port_security.add_argument(
            '--enable-port-security',
            action='store_true',
            help=_("Enable port security for this port")
        )
        port_security.add_argument(
            '--disable-port-security',
            action='store_true',
            help=_("Disable port security for this port")
        )
        parser.add_argument(
            '--allowed-address',
            metavar='ip-address=<ip-address>[,mac-address=<mac-address>]',
            action=parseractions.MultiKeyValueAction,
            dest='allowed_address_pairs',
            required_keys=['ip-address'],
            optional_keys=['mac-address'],
            help=_("Add allowed-address pair associated with this port: "
                   "ip-address=<ip-address>[,mac-address=<mac-address>] "
                   "(repeat option to set multiple allowed-address pairs)")
        )
        parser.add_argument(
            '--no-allowed-address',
            dest='no_allowed_address_pair',
            action='store_true',
            help=_("Clear existing allowed-address pairs associated "
                   "with this port. "
                   "(Specify both --allowed-address and --no-allowed-address "
                   "to overwrite the current allowed-address pairs)")
        )
        parser.add_argument(
            '--data-plane-status',
            metavar='<status>',
            choices=['ACTIVE', 'DOWN'],
            help=_("Set data plane status of this port (ACTIVE | DOWN). "
                   "Unset it to None with the 'port unset' command "
                   "(requires data plane status extension)")
        )
        _tag.add_tag_option_to_parser_for_set(parser, _('port'))

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        _prepare_fixed_ips(self.app.client_manager, parsed_args)
        obj = client.find_port(parsed_args.port, ignore_missing=False)
        attrs = _get_attrs(self.app.client_manager, parsed_args)

        if parsed_args.no_binding_profile:
            attrs['binding:profile'] = {}
        if parsed_args.binding_profile:
            if 'binding:profile' not in attrs:
                attrs['binding:profile'] = copy.deepcopy(obj.binding_profile)
            attrs['binding:profile'].update(parsed_args.binding_profile)

        if parsed_args.no_fixed_ip:
            attrs['fixed_ips'] = []
        if parsed_args.fixed_ip:
            if 'fixed_ips' not in attrs:
                # obj.fixed_ips = [{}] if no fixed IPs are set.
                # Only append this to attrs['fixed_ips'] if actual fixed
                # IPs are present to avoid adding an empty dict.
                attrs['fixed_ips'] = [ip for ip in obj.fixed_ips if ip]
            attrs['fixed_ips'].extend(parsed_args.fixed_ip)

        if parsed_args.no_security_group:
            attrs['security_group_ids'] = []
        if parsed_args.security_group:
            if 'security_group_ids' not in attrs:
                # NOTE(dtroyer): Get existing security groups, iterate the
                #                list to force a new list object to be
                #                created and make sure the SDK Resource
                #                marks the attribute 'dirty'.
                attrs['security_group_ids'] = [
                    id for id in obj.security_group_ids
                ]
            attrs['security_group_ids'].extend(
                client.find_security_group(sg, ignore_missing=False).id
                for sg in parsed_args.security_group
            )

        if parsed_args.no_allowed_address_pair:
            attrs['allowed_address_pairs'] = []
        if parsed_args.allowed_address_pairs:
            if 'allowed_address_pairs' not in attrs:
                attrs['allowed_address_pairs'] = (
                    [addr for addr in obj.allowed_address_pairs if addr]
                )
            attrs['allowed_address_pairs'].extend(
                _convert_address_pairs(parsed_args)
            )
        if parsed_args.data_plane_status:
            attrs['data_plane_status'] = parsed_args.data_plane_status

        if attrs:
            with common.check_missing_extension_if_error(
                    self.app.client_manager.network, attrs):
                client.update_port(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_set(client, obj, parsed_args)


class ShowPort(command.ShowOne):
    _description = _("Display port details")

    def get_parser(self, prog_name):
        parser = super(ShowPort, self).get_parser(prog_name)
        parser.add_argument(
            'port',
            metavar="<port>",
            help=_("Port to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_port(parsed_args.port, ignore_missing=False)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class UnsetPort(command.Command):
    _description = _("Unset port properties")

    def get_parser(self, prog_name):
        parser = super(UnsetPort, self).get_parser(prog_name)
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            help=_("Desired IP and/or subnet which should be "
                   "removed from this port (name or ID): subnet=<subnet>,"
                   "ip-address=<ip-address> (repeat option to unset multiple "
                   "fixed IP addresses)"))

        parser.add_argument(
            '--binding-profile',
            metavar='<binding-profile-key>',
            action='append',
            help=_("Desired key which should be removed from binding:profile "
                   "(repeat option to unset multiple binding:profile data)"))
        parser.add_argument(
            '--security-group',
            metavar='<security-group>',
            action='append',
            dest='security_group_ids',
            help=_("Security group which should be removed this port (name "
                   "or ID) (repeat option to unset multiple security groups)")
        )

        parser.add_argument(
            'port',
            metavar="<port>",
            help=_("Port to modify (name or ID)")
        )
        parser.add_argument(
            '--allowed-address',
            metavar='ip-address=<ip-address>[,mac-address=<mac-address>]',
            action=parseractions.MultiKeyValueAction,
            dest='allowed_address_pairs',
            required_keys=['ip-address'],
            optional_keys=['mac-address'],
            help=_("Desired allowed-address pair which should be removed "
                   "from this port: ip-address=<ip-address>"
                   "[,mac-address=<mac-address>] (repeat option to unset "
                   "multiple allowed-address pairs)")
        )
        parser.add_argument(
            '--qos-policy',
            action='store_true',
            default=False,
            help=_("Remove the QoS policy attached to the port")
        )
        parser.add_argument(
            '--data-plane-status',
            action='store_true',
            help=_("Clear existing information of data plane status")
        )

        _tag.add_tag_option_to_parser_for_unset(parser, _('port'))

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_port(parsed_args.port, ignore_missing=False)
        # SDK ignores update() if it receives a modified obj and attrs
        # To handle the same tmp_obj is created in all take_action of
        # Unset* classes
        tmp_fixed_ips = copy.deepcopy(obj.fixed_ips)
        tmp_binding_profile = copy.deepcopy(obj.binding_profile)
        tmp_secgroups = copy.deepcopy(obj.security_group_ids)
        tmp_addr_pairs = copy.deepcopy(obj.allowed_address_pairs)
        _prepare_fixed_ips(self.app.client_manager, parsed_args)
        attrs = {}
        if parsed_args.fixed_ip:
            try:
                for ip in parsed_args.fixed_ip:
                    tmp_fixed_ips.remove(ip)
            except ValueError:
                msg = _("Port does not contain fixed-ip %s") % ip
                raise exceptions.CommandError(msg)
            attrs['fixed_ips'] = tmp_fixed_ips
        if parsed_args.binding_profile:
            try:
                for key in parsed_args.binding_profile:
                    del tmp_binding_profile[key]
            except KeyError:
                msg = _("Port does not contain binding-profile %s") % key
                raise exceptions.CommandError(msg)
            attrs['binding:profile'] = tmp_binding_profile
        if parsed_args.security_group_ids:
            try:
                for sg in parsed_args.security_group_ids:
                    sg_id = client.find_security_group(
                        sg, ignore_missing=False).id
                    tmp_secgroups.remove(sg_id)
            except ValueError:
                msg = _("Port does not contain security group %s") % sg
                raise exceptions.CommandError(msg)
            attrs['security_group_ids'] = tmp_secgroups
        if parsed_args.allowed_address_pairs:
            try:
                for addr in _convert_address_pairs(parsed_args):
                    tmp_addr_pairs.remove(addr)
            except ValueError:
                msg = _("Port does not contain allowed-address-pair %s") % addr
                raise exceptions.CommandError(msg)
            attrs['allowed_address_pairs'] = tmp_addr_pairs
        if parsed_args.qos_policy:
            attrs['qos_policy_id'] = None
        if parsed_args.data_plane_status:
            attrs['data_plane_status'] = None

        if attrs:
            client.update_port(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_unset(client, obj, parsed_args)
