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

from openstackclient.common import command
from openstackclient.common import exceptions
from openstackclient.common import parseractions
from openstackclient.common import utils
from openstackclient.identity import common as identity_common


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


_formatters = {
    'prefixes': utils.format_list,
}


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.prefixes is not None:
        attrs['prefixes'] = parsed_args.prefixes
    if parsed_args.default_prefix_length is not None:
        attrs['default_prefixlen'] = parsed_args.default_prefix_length
    if parsed_args.min_prefix_length is not None:
        attrs['min_prefixlen'] = parsed_args.min_prefix_length
    if parsed_args.max_prefix_length is not None:
        attrs['max_prefixlen'] = parsed_args.max_prefix_length

    # "subnet pool set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    return attrs


def _add_prefix_options(parser):
    parser.add_argument(
        '--pool-prefix',
        metavar='<pool-prefix>',
        dest='prefixes',
        action='append',
        help='Set subnet pool prefixes (in CIDR notation). '
             'Repeat this option to set multiple prefixes.',
    )
    parser.add_argument(
        '--default-prefix-length',
        metavar='<default-prefix-length>',
        action=parseractions.NonNegativeAction,
        help='Set subnet pool default prefix length',
    )
    parser.add_argument(
        '--min-prefix-length',
        metavar='<min-prefix-length>',
        action=parseractions.NonNegativeAction,
        help='Set subnet pool minimum prefix length',
    )
    parser.add_argument(
        '--max-prefix-length',
        metavar='<max-prefix-length>',
        action=parseractions.NonNegativeAction,
        help='Set subnet pool maximum prefix length',
    )


class CreateSubnetPool(command.ShowOne):
    """Create subnet pool"""

    def get_parser(self, prog_name):
        parser = super(CreateSubnetPool, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='Name of the new subnet pool'
        )
        _add_prefix_options(parser)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help="Owner's project (name or ID)",
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        # NeutronServer expects prefixes to be a List
        if "prefixes" not in attrs:
            attrs['prefixes'] = []
        obj = client.create_subnet_pool(**attrs)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)


class DeleteSubnetPool(command.Command):
    """Delete subnet pool"""

    def get_parser(self, prog_name):
        parser = super(DeleteSubnetPool, self).get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar='<subnet-pool>',
            help='Subnet pool to delete (name or ID)'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet_pool(parsed_args.subnet_pool)
        client.delete_subnet_pool(obj)


class ListSubnetPool(command.Lister):
    """List subnet pools"""

    def get_parser(self, prog_name):
        parser = super(ListSubnetPool, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):
        data = self.app.client_manager.network.subnet_pools()

        if parsed_args.long:
            headers = (
                'ID',
                'Name',
                'Prefixes',
                'Default Prefix Length',
                'Address Scope',
            )
            columns = (
                'id',
                'name',
                'prefixes',
                'default_prefixlen',
                'address_scope_id',
            )
        else:
            headers = (
                'ID',
                'Name',
                'Prefixes',
            )
            columns = (
                'id',
                'name',
                'prefixes',
            )

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetSubnetPool(command.Command):
    """Set subnet pool properties"""

    def get_parser(self, prog_name):
        parser = super(SetSubnetPool, self).get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar='<subnet-pool>',
            help='Subnet pool to modify (name or ID)'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Set subnet pool name',
        )
        _add_prefix_options(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet_pool(parsed_args.subnet_pool,
                                      ignore_missing=False)

        attrs = _get_attrs(self.app.client_manager, parsed_args)
        if attrs == {}:
            msg = "Nothing specified to be set"
            raise exceptions.CommandError(msg)

        # Existing prefixes must be a subset of the new prefixes.
        if 'prefixes' in attrs:
            attrs['prefixes'].extend(obj.prefixes)

        client.update_subnet_pool(obj, **attrs)


class ShowSubnetPool(command.ShowOne):
    """Display subnet pool details"""

    def get_parser(self, prog_name):
        parser = super(ShowSubnetPool, self).get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar='<subnet-pool>',
            help='Subnet pool to display (name or ID)'
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet_pool(
            parsed_args.subnet_pool,
            ignore_missing=False
        )
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)
