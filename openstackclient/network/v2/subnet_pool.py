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

"""Subnet pool action implementations"""

import logging

from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import tags as _tag

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common


LOG = logging.getLogger(__name__)


def _get_columns(item):
    column_map = {
        'default_prefix_length': 'default_prefixlen',
        'is_shared': 'shared',
        'maximum_prefix_length': 'max_prefixlen',
        'minimum_prefix_length': 'min_prefixlen',
    }
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


_formatters = {
    'prefixes': format_columns.ListColumn,
    'tags': format_columns.ListColumn,
}


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    network_client = client_manager.network

    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if parsed_args.prefixes is not None:
        attrs['prefixes'] = parsed_args.prefixes
    if parsed_args.default_prefix_length is not None:
        attrs['default_prefixlen'] = parsed_args.default_prefix_length
    if parsed_args.min_prefix_length is not None:
        attrs['min_prefixlen'] = parsed_args.min_prefix_length
    if parsed_args.max_prefix_length is not None:
        attrs['max_prefixlen'] = parsed_args.max_prefix_length

    if parsed_args.address_scope is not None:
        attrs['address_scope_id'] = network_client.find_address_scope(
            parsed_args.address_scope, ignore_missing=False
        ).id
    if 'no_address_scope' in parsed_args and parsed_args.no_address_scope:
        attrs['address_scope_id'] = None

    if parsed_args.default:
        attrs['is_default'] = True
    if parsed_args.no_default:
        attrs['is_default'] = False

    if 'share' in parsed_args and parsed_args.share:
        attrs['shared'] = True
    if 'no_share' in parsed_args and parsed_args.no_share:
        attrs['shared'] = False

    # "subnet pool set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['project_id'] = project_id

    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description

    if parsed_args.default_quota is not None:
        attrs['default_quota'] = int(parsed_args.default_quota)

    return attrs


def _add_prefix_options(parser, for_create=False):
    parser.add_argument(
        '--pool-prefix',
        metavar='<pool-prefix>',
        dest='prefixes',
        action='append',
        required=for_create,
        help=_(
            "Set subnet pool prefixes (in CIDR notation) "
            "(repeat option to set multiple prefixes)"
        ),
    )
    parser.add_argument(
        '--default-prefix-length',
        metavar='<default-prefix-length>',
        type=int,
        action=parseractions.NonNegativeAction,
        help=_("Set subnet pool default prefix length"),
    )
    parser.add_argument(
        '--min-prefix-length',
        metavar='<min-prefix-length>',
        action=parseractions.NonNegativeAction,
        type=int,
        help=_("Set subnet pool minimum prefix length"),
    )
    parser.add_argument(
        '--max-prefix-length',
        metavar='<max-prefix-length>',
        type=int,
        action=parseractions.NonNegativeAction,
        help=_("Set subnet pool maximum prefix length"),
    )


def _add_default_options(parser):
    default_group = parser.add_mutually_exclusive_group()
    default_group.add_argument(
        '--default',
        action='store_true',
        help=_("Set this as a default subnet pool"),
    )
    default_group.add_argument(
        '--no-default',
        action='store_true',
        help=_("Set this as a non-default subnet pool"),
    )


# TODO(rtheis): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateSubnetPool(command.ShowOne, common.NeutronCommandWithExtraArgs):
    _description = _("Create subnet pool")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help=_("Name of the new subnet pool")
        )
        _add_prefix_options(parser, for_create=True)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--address-scope',
            metavar='<address-scope>',
            help=_(
                "Set address scope associated with the subnet pool "
                "(name or ID), prefixes must be unique across address "
                "scopes"
            ),
        )
        _add_default_options(parser)
        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            '--share',
            action='store_true',
            help=_("Set this subnet pool as shared"),
        )
        shared_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("Set this subnet pool as not shared"),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set subnet pool description"),
        )
        parser.add_argument(
            '--default-quota',
            type=int,
            metavar='<num-ip-addresses>',
            help=_(
                "Set default per-project quota for this subnet pool "
                "as the number of IP addresses that can be allocated "
                "from the subnet pool"
            ),
        )
        _tag.add_tag_option_to_parser_for_create(parser, _('subnet pool'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        # NeutronServer expects prefixes to be a List
        if "prefixes" not in attrs:
            attrs['prefixes'] = []
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        obj = client.create_subnet_pool(**attrs)
        # tags cannot be set when created, so tags need to be set later.
        _tag.update_tags_for_set(client, obj, parsed_args)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)


class DeleteSubnetPool(command.Command):
    _description = _("Delete subnet pool(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar='<subnet-pool>',
            nargs='+',
            help=_("Subnet pool(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for pool in parsed_args.subnet_pool:
            try:
                obj = client.find_subnet_pool(pool, ignore_missing=False)
                client.delete_subnet_pool(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete subnet pool with "
                        "name or ID '%(pool)s': %(e)s"
                    ),
                    {'pool': pool, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.subnet_pool)
            msg = _(
                "%(result)s of %(total)s subnet pools failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


# TODO(rtheis): Use only the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListSubnetPool(command.Lister):
    _description = _("List subnet pools")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            '--share',
            action='store_true',
            help=_("List subnet pools shared between projects"),
        )
        shared_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("List subnet pools not shared between projects"),
        )
        default_group = parser.add_mutually_exclusive_group()
        default_group.add_argument(
            '--default',
            action='store_true',
            help=_(
                "List subnet pools used as the default external subnet pool"
            ),
        )
        default_group.add_argument(
            '--no-default',
            action='store_true',
            help=_(
                "List subnet pools not used as the default external "
                "subnet pool"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                "List subnet pools according to their project (name or ID)"
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("List only subnet pools of given name in output"),
        )
        parser.add_argument(
            '--address-scope',
            metavar='<address-scope>',
            help=_(
                "List only subnet pools of given address scope "
                "in output (name or ID)"
            ),
        )
        _tag.add_tag_filtering_option_to_parser(parser, _('subnet pools'))
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        network_client = self.app.client_manager.network
        filters = {}
        if parsed_args.share:
            filters['shared'] = True
            filters['is_shared'] = True
        elif parsed_args.no_share:
            filters['shared'] = False
            filters['is_shared'] = False
        if parsed_args.default:
            filters['is_default'] = True
        elif parsed_args.no_default:
            filters['is_default'] = False
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            filters['project_id'] = project_id
        if parsed_args.name is not None:
            filters['name'] = parsed_args.name
        if parsed_args.address_scope:
            address_scope = network_client.find_address_scope(
                parsed_args.address_scope, ignore_missing=False
            )
            filters['address_scope_id'] = address_scope.id
        _tag.get_tag_filtering_args(parsed_args, filters)
        data = network_client.subnet_pools(**filters)

        headers: tuple[str, ...] = ('ID', 'Name', 'Prefixes')
        columns: tuple[str, ...] = ('id', 'name', 'prefixes')
        if parsed_args.long:
            headers += (
                'Default Prefix Length',
                'Address Scope',
                'Default Subnet Pool',
                'Shared',
                'Tags',
            )
            columns += (
                'default_prefix_length',
                'address_scope_id',
                'is_default',
                'is_shared',
                'tags',
            )

        return (
            headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters=_formatters,
                )
                for s in data
            ),
        )


# TODO(rtheis): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetSubnetPool(common.NeutronCommandWithExtraArgs):
    _description = _("Set subnet pool properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar='<subnet-pool>',
            help=_("Subnet pool to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar='<name>', help=_("Set subnet pool name")
        )
        _add_prefix_options(parser)
        address_scope_group = parser.add_mutually_exclusive_group()
        address_scope_group.add_argument(
            '--address-scope',
            metavar='<address-scope>',
            help=_(
                "Set address scope associated with the subnet pool "
                "(name or ID), prefixes must be unique across address "
                "scopes"
            ),
        )
        address_scope_group.add_argument(
            '--no-address-scope',
            action='store_true',
            help=_("Remove address scope associated with the subnet pool"),
        )
        _add_default_options(parser)
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set subnet pool description"),
        )
        parser.add_argument(
            '--default-quota',
            type=int,
            metavar='<num-ip-addresses>',
            help=_(
                "Set default per-project quota for this subnet pool "
                "as the number of IP addresses that can be allocated "
                "from the subnet pool"
            ),
        )
        _tag.add_tag_option_to_parser_for_set(parser, _('subnet pool'))

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet_pool(
            parsed_args.subnet_pool, ignore_missing=False
        )

        attrs = _get_attrs(self.app.client_manager, parsed_args)

        # Existing prefixes must be a subset of the new prefixes.
        if 'prefixes' in attrs:
            attrs['prefixes'].extend(obj.prefixes)

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        if attrs:
            client.update_subnet_pool(obj, **attrs)
        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_set(client, obj, parsed_args)


class ShowSubnetPool(command.ShowOne):
    _description = _("Display subnet pool details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar='<subnet-pool>',
            help=_("Subnet pool to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet_pool(
            parsed_args.subnet_pool, ignore_missing=False
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)


class UnsetSubnetPool(command.Command):
    _description = _("Unset subnet pool properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar="<subnet-pool>",
            help=_("Subnet pool to modify (name or ID)"),
        )
        _tag.add_tag_option_to_parser_for_unset(parser, _('subnet pool'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet_pool(
            parsed_args.subnet_pool, ignore_missing=False
        )
        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_unset(client, obj, parsed_args)
