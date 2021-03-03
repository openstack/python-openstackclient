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

from novaclient import api_versions
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


_formatters = {
    'members': format_columns.ListColumn,
    'policies': format_columns.ListColumn,
    'rules': format_columns.DictColumn,
}


def _get_columns(info):
    columns = list(info.keys())
    if 'metadata' in columns:
        # NOTE(RuiChen): The metadata of server group is always empty since API
        #                compatible, so hide it in order to avoid confusion.
        columns.remove('metadata')
    return tuple(sorted(columns))


class CreateServerGroup(command.ShowOne):
    _description = _("Create a new server group.")

    def get_parser(self, prog_name):
        parser = super(CreateServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New server group name")
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
        info = {}

        if parsed_args.policy in ('soft-affinity', 'soft-anti-affinity'):
            if compute_client.api_version < api_versions.APIVersion('2.15'):
                msg = _(
                    '--os-compute-api-version 2.15 or greater is required to '
                    'support the %s policy'
                )
                raise exceptions.CommandError(msg % parsed_args.policy)

        if parsed_args.rules:
            if compute_client.api_version < api_versions.APIVersion('2.64'):
                msg = _(
                    '--os-compute-api-version 2.64 or greater is required to '
                    'support the --rule option'
                )
                raise exceptions.CommandError(msg)

        if compute_client.api_version < api_versions.APIVersion('2.64'):
            kwargs = {'policies': [parsed_args.policy]}
        else:
            kwargs = {
                'policy': parsed_args.policy,
                'rules': parsed_args.rules or None,
            }

        server_group = compute_client.server_groups.create(
            name=parsed_args.name, **kwargs)

        info.update(server_group._info)

        columns = _get_columns(info)
        data = utils.get_dict_properties(
            info, columns, formatters=_formatters)
        return columns, data


class DeleteServerGroup(command.Command):
    _description = _("Delete existing server group(s).")

    def get_parser(self, prog_name):
        parser = super(DeleteServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server_group',
            metavar='<server-group>',
            nargs='+',
            help=_("server group(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for group in parsed_args.server_group:
            try:
                group_obj = utils.find_resource(compute_client.server_groups,
                                                group)
                compute_client.server_groups.delete(group_obj.id)
            # Catch all exceptions in order to avoid to block the next deleting
            except Exception as e:
                result += 1
                LOG.error(e)

        if result > 0:
            total = len(parsed_args.server_group)
            msg = _("%(result)s of %(total)s server groups failed to delete.")
            raise exceptions.CommandError(
                msg % {"result": result,
                       "total": total}
            )


class ListServerGroup(command.Lister):
    _description = _("List all server groups.")

    def get_parser(self, prog_name):
        parser = super(ListServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_("Display information from all projects (admin only)")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        # TODO(stephenfin): This should really be a --marker option, but alas
        # the API doesn't support that for some reason
        parser.add_argument(
            '--offset',
            metavar='<offset>',
            type=int,
            default=None,
            help=_(
                'Index from which to start listing servers. This should '
                'typically be a factor of --limit. Display all servers groups '
                'if not specified.'
            ),
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            default=None,
            help=_(
                "Maximum number of server groups to display. "
                "If limit is greater than 'osapi_max_limit' option of Nova "
                "API, 'osapi_max_limit' will be used instead."
            ),
        )
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

        data = compute_client.server_groups.list(**kwargs)

        policy_key = 'Policies'
        if compute_client.api_version >= api_versions.APIVersion("2.64"):
            policy_key = 'Policy'

        columns = (
            'id',
            'name',
            policy_key.lower(),
        )
        column_headers = (
            'ID',
            'Name',
            policy_key,
        )
        if parsed_args.long:
            columns += (
                'members',
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
                    s, columns, formatters=_formatters,
                ) for s in data
            ),
        )


class ShowServerGroup(command.ShowOne):
    _description = _("Display server group details.")

    def get_parser(self, prog_name):
        parser = super(ShowServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server_group',
            metavar='<server-group>',
            help=_("server group to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        group = utils.find_resource(compute_client.server_groups,
                                    parsed_args.server_group)
        info = {}
        info.update(group._info)
        columns = _get_columns(info)
        data = utils.get_dict_properties(
            info, columns, formatters=_formatters)
        return columns, data
