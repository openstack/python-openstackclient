#   Copyright 2016 Huawei, Inc. All rights reserved.
#
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

"""Compute v2 Server Group action implementations"""

import logging

from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


_formatters = {
    'member_ids': format_columns.ListColumn,
    'policies': format_columns.ListColumn,
    'rules': format_columns.DictColumn,
}


def _get_server_group_columns(item, client):
    column_map = {'member_ids': 'members'}
    hidden_columns = ['metadata', 'location']

    if sdk_utils.supports_microversion(client, '2.64'):
        hidden_columns.append('policies')
    else:
        hidden_columns.append('policy')
        hidden_columns.append('rules')

    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class CreateServerGroup(command.ShowOne):
    _description = _("Create a new server group.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New server group name"),
        )
        parser.add_argument(
            '--policy',
            metavar='<policy>',
            choices=[
                'affinity',
                'anti-affinity',
                'soft-affinity',
                'soft-anti-affinity',
            ],
            default='affinity',
            help=_(
                "Add a policy to <name> "
                "Specify --os-compute-api-version 2.15 or higher for the "
                "'soft-affinity' or 'soft-anti-affinity' policy."
            ),
        )
        parser.add_argument(
            '--rule',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            default={},
            dest='rules',
            help=_(
                "A rule for the policy. Currently, only the "
                "'max_server_per_host' rule is supported for the "
                "'anti-affinity' policy."
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        if parsed_args.policy in ('soft-affinity', 'soft-anti-affinity'):
            if not sdk_utils.supports_microversion(compute_client, '2.15'):
                msg = _(
                    '--os-compute-api-version 2.15 or greater is required to '
                    'support the %s policy'
                )
                raise exceptions.CommandError(msg % parsed_args.policy)

        if parsed_args.rules:
            if not sdk_utils.supports_microversion(compute_client, '2.64'):
                msg = _(
                    '--os-compute-api-version 2.64 or greater is required to '
                    'support the --rule option'
                )
                raise exceptions.CommandError(msg)

        if not sdk_utils.supports_microversion(compute_client, '2.64'):
            kwargs = {
                'name': parsed_args.name,
                'policies': [parsed_args.policy],
            }
        else:
            kwargs = {
                'name': parsed_args.name,
                'policy': parsed_args.policy,
            }

            if parsed_args.rules:
                kwargs['rules'] = parsed_args.rules

        server_group = compute_client.create_server_group(**kwargs)

        display_columns, columns = _get_server_group_columns(
            server_group,
            compute_client,
        )
        data = utils.get_item_properties(
            server_group,
            columns,
            formatters=_formatters,
        )
        return display_columns, data


class DeleteServerGroup(command.Command):
    _description = _("Delete existing server group(s).")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server_group',
            metavar='<server-group>',
            nargs='+',
            help=_("server group(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for group in parsed_args.server_group:
            try:
                group_obj = compute_client.find_server_group(
                    group, ignore_missing=False
                )
                compute_client.delete_server_group(group_obj.id)
            # Catch all exceptions in order to avoid to block the next deleting
            except Exception as e:
                result += 1
                LOG.error(e)

        if result > 0:
            total = len(parsed_args.server_group)
            msg = _("%(result)s of %(total)s server groups failed to delete.")
            raise exceptions.CommandError(
                msg % {"result": result, "total": total}
            )


class ListServerGroup(command.Lister):
    _description = _("List all server groups.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_("Display information from all projects (admin only)"),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        # TODO(stephenfin): This should really be a --marker option, but alas
        # the API doesn't support that for some reason
        pagination.add_offset_pagination_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        kwargs = {}

        if parsed_args.all_projects:
            kwargs['all_projects'] = parsed_args.all_projects

        if parsed_args.offset:
            kwargs['offset'] = parsed_args.offset

        if parsed_args.limit:
            kwargs['limit'] = parsed_args.limit

        data = compute_client.server_groups(**kwargs)

        policy_key = 'Policies'
        if sdk_utils.supports_microversion(compute_client, '2.64'):
            policy_key = 'Policy'

        columns: tuple[str, ...] = (
            'id',
            'name',
            policy_key.lower(),
        )
        column_headers: tuple[str, ...] = (
            'ID',
            'Name',
            policy_key,
        )
        if parsed_args.long:
            columns += (
                'member_ids',
                'project_id',
                'user_id',
            )
            column_headers += (
                'Members',
                'Project Id',
                'User Id',
            )

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters=_formatters,
                )
                for s in data
            ),
        )


class ShowServerGroup(command.ShowOne):
    _description = _("Display server group details.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server_group',
            metavar='<server-group>',
            help=_("server group to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        group = compute_client.find_server_group(
            parsed_args.server_group, ignore_missing=False
        )
        display_columns, columns = _get_server_group_columns(
            group,
            compute_client,
        )
        data = utils.get_item_properties(
            group, columns, formatters=_formatters
        )
        return display_columns, data
