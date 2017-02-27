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

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import sdk_utils


LOG = logging.getLogger(__name__)


def _format_admin_state(state):
    return 'UP' if state else 'DOWN'


def _format_dns_assignment(dns_assignment):
    return utils.format_list_of_dicts(dns_assignment) \
        if dns_assignment else None

_formatters = {
    'admin_state_up': _format_admin_state,
    'is_admin_state_up': _format_admin_state,
    'allowed_address_pairs': utils.format_list_of_dicts,
    'binding_profile': utils.format_dict,
    'binding_vif_details': utils.format_dict,
    'binding:profile': utils.format_dict,
    'binding:vif_details': utils.format_dict,
    'dns_assignment': _format_dns_assignment,
    'extra_dhcp_opts': utils.format_list_of_dicts,
    'fixed_ips': utils.format_list_of_dicts,
    'security_group_ids': utils.format_list,
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

    # Handle deprecated options
    # NOTE(dtroyer): --device-id and --host-id were deprecated in Mar 2016.
    #                Do not remove before 3.x release or Mar 2017.
    if parsed_args.device_id:
        attrs['device_id'] = parsed_args.device_id
        LOG.warning(_(
            'The --device-id option is deprecated, '
            'please use --device instead.'
        ))
    if parsed_args.host_id:
        attrs['binding:host_id'] = parsed_args.host_id
        LOG.warning(_(
            'The --host-id option is deprecated, '
            'please use --host instead.'
        ))
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if parsed_args.fixed_ip is not None:
        attrs['fixed_ips'] = parsed_args.fixed_ip
    if parsed_args.device:
        attrs['device_id'] = parsed_args.device
    if parsed_args.device_owner is not None:
        attrs['device_owner'] = parsed_args.device_owner
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    if parsed_args.binding_profile is not None:
        attrs['binding:profile'] = parsed_args.binding_profile
    if parsed_args.vnic_type is not None:
        attrs['binding:vnic_type'] = parsed_args.vnic_type
    if parsed_args.host:
        attrs['binding:host_id'] = parsed_args.host

    if parsed_args.dns_name is not None:
        attrs['dns_name'] = parsed_args.dns_name
    # It is possible that name is not updated during 'port set'
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    # The remaining options do not support 'port set' command, so they require
    # additional check
    if 'mac_address' in parsed_args and parsed_args.mac_address is not None:
        attrs['mac_address'] = parsed_args.mac_address
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
    return ips


def _add_updatable_args(parser):
    parser.add_argument(
        '--description',
        metavar='<description>',
        help=_("Description of this port")
    )
    # NOTE(dtroyer): --device-id is deprecated in Mar 2016.  Do not
    #                remove before 3.x release or Mar 2017.
    device_group = parser.add_mutually_exclusive_group()
    device_group.add_argument(
        '--device',
        metavar='<device-id>',
        help=_("Port device ID")
    )
    device_group.add_argument(
        '--device-id',
        metavar='<device-id>',
        help=argparse.SUPPRESS,
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
                 'normal', 'baremetal'],
        help=_("VNIC type for this port (direct | direct-physical | "
               "macvtap | normal | baremetal, default: normal)")
    )
    # NOTE(dtroyer): --host-id is deprecated in Mar 2016.  Do not
    #                remove before 3.x release or Mar 2017.
    host_group = parser.add_mutually_exclusive_group()
    host_group.add_argument(
        '--host',
        metavar='<host-id>',
        help=_("Allocate port on host <host-id> (ID only)")
    )
    host_group.add_argument(
        '--host-id',
        metavar='<host-id>',
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        '--dns-name',
        metavar='dns-name',
        help=_("Set DNS name to this port "
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
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            help=_("Desired IP and/or subnet (name or ID) for this port: "
                   "subnet=<subnet>,ip-address=<ip-address> "
                   "(repeat option to set multiple fixed IP addresses)")
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
        parser.add_argument(
            '--mac-address',
            metavar='<mac-address>',
            help=_("MAC address of this port")
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
        # TODO(singhj): Add support for extended options:
        # qos,dhcp
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
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        _network = client.find_network(parsed_args.network,
                                       ignore_missing=False)
        parsed_args.network = _network.id
        _prepare_fixed_ips(self.app.client_manager, parsed_args)
        attrs = _get_attrs(self.app.client_manager, parsed_args)

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

        obj = client.create_port(**attrs)
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
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            help=_("Desired IP and/or subnet (name or ID) for filtering "
                   "ports: subnet=<subnet>,ip-address=<ip-address> "
                   "(repeat option to set multiple fixed IP addresses)")
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        compute_client = self.app.client_manager.compute
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
            columns += ('security_group_ids', 'device_owner',)
            column_headers += ('Security Groups', 'Device Owner',)
        if parsed_args.device_owner is not None:
            filters['device_owner'] = parsed_args.device_owner
        if parsed_args.router:
            _router = network_client.find_router(parsed_args.router,
                                                 ignore_missing=False)
            filters['device_id'] = _router.id
        if parsed_args.server:
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

        data = network_client.ports(**filters)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
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
            help=_("Desired IP and/or subnet (name or ID) for this port: "
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
            help=_("Clear existing information of binding:profile."
                   "Specify both --binding-profile and --no-binding-profile "
                   "to overwrite the current binding:profile information.")
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
            help=_("Clear existing allowed-address pairs associated"
                   "with this port."
                   "(Specify both --allowed-address and --no-allowed-address"
                   "to overwrite the current allowed-address pairs)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        _prepare_fixed_ips(self.app.client_manager, parsed_args)
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.find_port(parsed_args.port, ignore_missing=False)
        if 'binding:profile' in attrs:
            # Do not modify attrs if both binding_profile/no_binding given
            if not parsed_args.no_binding_profile:
                tmp_binding_profile = copy.deepcopy(obj.binding_profile)
                tmp_binding_profile.update(attrs['binding:profile'])
                attrs['binding:profile'] = tmp_binding_profile
        elif parsed_args.no_binding_profile:
            attrs['binding:profile'] = {}
        if 'fixed_ips' in attrs:
            # When user unsets the fixed_ips, obj.fixed_ips = [{}].
            # Adding the obj.fixed_ips list to attrs['fixed_ips']
            # would therefore add an empty dictionary, while we need
            # to append the attrs['fixed_ips'] iff there is some info
            # in the obj.fixed_ips. Therefore I have opted for this `for` loop
            # Do not modify attrs if fixed_ip/no_fixed_ip given
            if not parsed_args.no_fixed_ip:
                attrs['fixed_ips'] += [ip for ip in obj.fixed_ips if ip]
        elif parsed_args.no_fixed_ip:
            attrs['fixed_ips'] = []

        if parsed_args.security_group:
            attrs['security_group_ids'] = [
                client.find_security_group(sg, ignore_missing=False).id for
                sg in parsed_args.security_group]
            if not parsed_args.no_security_group:
                attrs['security_group_ids'] += obj.security_group_ids

        elif parsed_args.no_security_group:
            attrs['security_group_ids'] = []

        if (parsed_args.allowed_address_pairs and
                parsed_args.no_allowed_address_pair):
            attrs['allowed_address_pairs'] = (
                _convert_address_pairs(parsed_args))

        elif parsed_args.allowed_address_pairs:
            attrs['allowed_address_pairs'] = (
                [addr for addr in obj.allowed_address_pairs if addr] +
                _convert_address_pairs(parsed_args))

        elif parsed_args.no_allowed_address_pair:
            attrs['allowed_address_pairs'] = []

        client.update_port(obj, **attrs)


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
            help=_("Desired IP and/or subnet (name or ID) which should be "
                   "removed from this port: subnet=<subnet>,"
                   "ip-address=<ip-address> (repeat option to unset multiple "
                   "fixed IP addresses)"))

        parser.add_argument(
            '--binding-profile',
            metavar='<binding-profile-key>',
            action='append',
            help=_("Desired key which should be removed from binding:profile"
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
                   "from this port: ip-address=<ip-address> "
                   "[,mac-address=<mac-address>] (repeat option to set "
                   "multiple allowed-address pairs)")
        )

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

        if attrs:
            client.update_port(obj, **attrs)
