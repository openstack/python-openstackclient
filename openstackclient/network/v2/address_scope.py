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

"""Address scope action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')

    return tuple(sorted(columns))


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    attrs['name'] = parsed_args.name
    attrs['ip_version'] = parsed_args.ip_version
    if parsed_args.share:
        attrs['shared'] = True
    if parsed_args.no_share:
        attrs['shared'] = False
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    return attrs


class CreateAddressScope(command.ShowOne):
    """Create a new Address Scope"""

    def get_parser(self, prog_name):
        parser = super(CreateAddressScope, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar="<name>",
            help=_("New address scope name")
        )
        parser.add_argument(
            '--ip-version',
            type=int,
            default=4,
            choices=[4, 6],
            help=_("IP version (default is 4)")
        )
        parser.add_argument(
            '--project',
            metavar="<project>",
            help=_("Owner's project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)

        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            help=_('Share the address scope between projects')
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_('Do not share the address scope between projects (default)')
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_address_scope(**attrs)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (columns, data)


class DeleteAddressScope(command.Command):
    """Delete address scope(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteAddressScope, self).get_parser(prog_name)
        parser.add_argument(
            'address_scope',
            metavar="<address-scope>",
            nargs='+',
            help=_("Address scope(s) to delete (name or ID)")
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for scope in parsed_args.address_scope:
            try:
                obj = client.find_address_scope(scope, ignore_missing=False)
                client.delete_address_scope(obj)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete address scope with "
                            "name or ID '%(scope)s': %(e)s"),
                          {'scope': scope, 'e': e})

        if result > 0:
            total = len(parsed_args.address_scope)
            msg = (_("%(result)s of %(total)s address scopes failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListAddressScope(command.Lister):
    """List address scopes"""

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'id',
            'name',
            'ip_version',
            'shared',
            'tenant_id',
        )
        column_headers = (
            'ID',
            'Name',
            'IP Version',
            'Shared',
            'Project',
        )
        data = client.address_scopes()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters={},
                ) for s in data))


class SetAddressScope(command.Command):
    """Set address scope properties"""

    def get_parser(self, prog_name):
        parser = super(SetAddressScope, self).get_parser(prog_name)
        parser.add_argument(
            'address_scope',
            metavar="<address-scope>",
            help=_("Address scope to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help=_('Set address scope name')
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            help=_('Share the address scope between projects')
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_('Do not share the address scope between projects')
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_address_scope(
            parsed_args.address_scope,
            ignore_missing=False)
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.share:
            attrs['shared'] = True
        if parsed_args.no_share:
            attrs['shared'] = False
        client.update_address_scope(obj, **attrs)


class ShowAddressScope(command.ShowOne):
    """Display address scope details"""

    def get_parser(self, prog_name):
        parser = super(ShowAddressScope, self).get_parser(prog_name)
        parser.add_argument(
            'address_scope',
            metavar="<address-scope>",
            help=_("Address scope to display (name or ID)")
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_address_scope(
            parsed_args.address_scope,
            ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (columns, data)
