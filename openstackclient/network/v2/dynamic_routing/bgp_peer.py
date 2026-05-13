#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

from osc_lib.cli import identity as identity_utils
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import utils as network_utils


MIN_AS_NUM = 1
MAX_AS_NUM = 4294967295


def _get_attrs(client_manager, parsed_args):
    attrs = {}

    # Validate password
    if 'auth_type' in parsed_args:
        if parsed_args.auth_type != 'none':
            if 'password' not in parsed_args or parsed_args.password is None:
                raise exceptions.CommandError(
                    _('Must provide password if auth-type is specified.')
                )
        if (
            parsed_args.auth_type == 'none'
            and parsed_args.password is not None
        ):
            raise exceptions.CommandError(
                _('Must provide auth-type if password is specified.')
            )
        attrs['auth_type'] = parsed_args.auth_type

    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if 'remote_as' in parsed_args:
        attrs['remote_as'] = parsed_args.remote_as
    if 'peer_ip' in parsed_args:
        attrs['peer_ip'] = parsed_args.peer_ip
    if 'password' in parsed_args:
        attrs['password'] = parsed_args.password

    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id
    return attrs


class CreateBgpPeer(command.ShowOne):
    _description = _("Create a BGP peer")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help=_("Name of the BGP peer to create")
        )
        parser.add_argument(
            '--peer-ip',
            metavar='<peer-ip-address>',
            required=True,
            help=_("Peer IP address"),
        )
        parser.add_argument(
            '--remote-as',
            required=True,
            metavar='<peer-remote-as>',
            help=_(
                "Peer AS number. (Integer in [%(min_val)s, %(max_val)s] "
                "is allowed)"
            )
            % {
                'min_val': MIN_AS_NUM,
                'max_val': MAX_AS_NUM,
            },
        )
        parser.add_argument(
            '--auth-type',
            metavar='<peer-auth-type>',
            choices=['none', 'md5'],
            type=network_utils.convert_to_lowercase,
            default='none',
            help=_(
                "Authentication algorithm. Supported algorithms: "
                "none (default), md5"
            ),
        )
        parser.add_argument(
            '--password',
            metavar='<auth-password>',
            help=_("Authentication password"),
        )
        identity_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_bgp_peer(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, {}, ['location', 'tenant_id']
        )
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteBgpPeer(command.Command):
    _description = _("Delete a BGP peer")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_peer',
            metavar="<bgp-peer>",
            help=_("BGP peer to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_bgp_peer(
            parsed_args.bgp_peer, ignore_missing=False
        ).id
        client.delete_bgp_peer(id)


class ListBgpPeer(command.Lister):
    _description = _("List BGP peers")

    def take_action(self, parsed_args):
        data = self.app.client_manager.network.bgp_peers(retrieve_all=True)
        headers = ('ID', 'Name', 'Peer IP', 'Remote AS')
        columns = ('id', 'name', 'peer_ip', 'remote_as')
        return (
            headers,
            (
                utils.get_dict_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )


class SetBgpPeer(command.Command):
    _description = _("Update a BGP peer")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('--name', help=_("Updated name of the BGP peer"))
        parser.add_argument(
            '--password',
            metavar='<auth-password>',
            help=_("Updated authentication password"),
        )
        parser.add_argument(
            'bgp_peer',
            metavar="<bgp-peer>",
            help=_("BGP peer to update (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_bgp_peer(
            parsed_args.bgp_peer, ignore_missing=False
        ).id
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        client.update_bgp_peer(id, **attrs)


class ShowBgpPeer(command.ShowOne):
    _description = _("Show information for a BGP peer")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_peer',
            metavar="<bgp-peer>",
            help=_("BGP peer to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_bgp_peer(parsed_args.bgp_peer, ignore_missing=False)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, {}, ['location', 'tenant_id']
        )
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data
