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

"""Security Group action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any, cast

from cliff import columns as cliff_columns
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import tags as _tag

from openstackclient import command
from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import utils as network_utils

LOG = logging.getLogger(__name__)


def _format_network_security_group_rules(
    sg_rules: list[dict[str, Any]],
) -> str:
    # For readability and to align with formatting compute security group
    # rules, trim keys with caller known (e.g. security group and tenant ID)
    # or empty values.
    for sg_rule in sg_rules:
        empty_keys = [k for k, v in sg_rule.items() if not v]
        for key in empty_keys:
            sg_rule.pop(key)
        sg_rule.pop('security_group_id', None)
        sg_rule.pop('tenant_id', None)
        sg_rule.pop('project_id', None)
    return utils.format_list_of_dicts(sg_rules) or ""


def _format_compute_security_group_rule(sg_rule: dict[str, Any]) -> str:
    info = network_utils.transform_compute_security_group_rule(sg_rule)
    # Trim parent security group ID since caller has this information.
    info.pop('parent_group_id', None)
    # Trim keys with empty string values.
    keys_to_trim = [
        'ip_protocol',
        'ip_range',
        'port_range',
        'remote_security_group',
    ]
    for key in keys_to_trim:
        if key in info and not info[key]:
            info.pop(key)
    return utils.format_dict(info)


def _format_compute_security_group_rules(
    sg_rules: list[dict[str, Any]],
) -> str:
    rules = []
    for sg_rule in sg_rules:
        rules.append(_format_compute_security_group_rule(sg_rule))
    return utils.format_list(rules, separator='\n') or ""


class NetworkSecurityGroupRulesColumn(cliff_columns.FormattableColumn[Any]):
    def human_readable(self) -> str:
        return _format_network_security_group_rules(self._value)


class ComputeSecurityGroupRulesColumn(cliff_columns.FormattableColumn[Any]):
    def human_readable(self) -> str:
        return _format_compute_security_group_rules(self._value)


_formatters_network = {
    'security_group_rules': NetworkSecurityGroupRulesColumn,
}


_formatters_compute = {
    'rules': ComputeSecurityGroupRulesColumn,
}


def _get_columns(item: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    # We still support Nova managed security groups, where we have tenant_id.
    column_map = {
        'security_group_rules': 'rules',
    }
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class CreateSecurityGroup(command.ShowOne, common.NeutronCommandWithExtraArgs):
    _description = _("Create a new security group")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "name", metavar="<name>", help=_("New security group name")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Security group description"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)"),
        )
        stateful_group = parser.add_mutually_exclusive_group()
        stateful_group.add_argument(
            "--stateful",
            action='store_true',
            default=None,
            help=_("Security group is stateful (default)"),
        )
        stateful_group.add_argument(
            "--stateless",
            action='store_true',
            default=None,
            help=_("Security group is stateless"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        _tag.add_tag_option_to_parser_for_create(parser, _('security group'))
        return parser

    def _get_description(self, parsed_args: argparse.Namespace) -> str:
        if parsed_args.description is not None:
            return cast(str, parsed_args.description)
        else:
            return cast(str, parsed_args.name)

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        # Build the create attributes.
        attrs = {}
        attrs['name'] = parsed_args.name
        attrs['description'] = self._get_description(parsed_args)
        if parsed_args.stateful:
            attrs['stateful'] = True
        if parsed_args.stateless:
            attrs['stateful'] = False
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

        # Create the security group and display the results.
        obj = client.create_security_group(**attrs)
        # tags cannot be set when created, so tags need to be set later.
        _tag.update_tags_for_set(client, obj, parsed_args)
        display_columns, property_columns = _get_columns(obj)
        data = utils.get_item_properties(
            obj, property_columns, formatters=_formatters_network
        )
        return (display_columns, data)


class DeleteSecurityGroup(command.Command):
    _description = _("Delete security group(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs="+",
            help=_("Security group(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        result = 0

        for group in parsed_args.group:
            try:
                obj = client.find_security_group(group, ignore_missing=False)
                client.delete_security_group(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete security group with "
                        "name or ID '%(group)s': %(e)s"
                    ),
                    {'group': group, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.group)
            msg = _("%(result)s of %(total)s groups failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListSecurityGroup(command.Lister):
    _description = _("List security groups")
    FIELDS_TO_RETRIEVE = [
        'id',
        'name',
        'description',
        'project_id',
        'tags',
        'shared',
    ]

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                "List only security groups with the specified project "
                "(name or ID)"
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            '--share',
            action='store_true',
            dest='shared',
            default=None,
            help=_("List only security groups shared between projects"),
        )
        shared_group.add_argument(
            '--no-share',
            action='store_false',
            dest='shared',
            default=None,
            help=_("List only security groups not shared between projects"),
        )

        _tag.add_tag_filtering_option_to_parser(parser, _('security group'))
        pagination.add_marker_pagination_option_to_parser(parser)
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        filters = {}

        if parsed_args.project:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            filters['project_id'] = project_id

        if parsed_args.shared is not None:
            filters['shared'] = parsed_args.shared
        if parsed_args.marker is not None:
            filters['marker'] = parsed_args.marker
        if parsed_args.limit is not None:
            filters['limit'] = parsed_args.limit

        _tag.get_tag_filtering_args(parsed_args, filters)
        data = client.security_groups(
            fields=self.FIELDS_TO_RETRIEVE, **filters
        )

        columns = (
            "id",
            "name",
            "description",
            "project_id",
            "tags",
            "is_shared",
        )
        column_headers = (
            "ID",
            "Name",
            "Description",
            "Project",
            "Tags",
            "Shared",
        )
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )


class SetSecurityGroup(common.NeutronCommandWithExtraArgs):
    _description = _("Set security group properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Security group to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar='<new-name>', help=_("New security group name")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("New security group description"),
        )
        stateful_group = parser.add_mutually_exclusive_group()
        stateful_group.add_argument(
            "--stateful",
            action='store_true',
            default=None,
            help=_("Security group is stateful (default)"),
        )
        stateful_group.add_argument(
            "--stateless",
            action='store_true',
            default=None,
            help=_("Security group is stateless"),
        )
        _tag.add_tag_option_to_parser_for_set(parser, _('security group'))
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        obj = client.find_security_group(
            parsed_args.group, ignore_missing=False
        )
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        if parsed_args.stateful:
            attrs['stateful'] = True
        if parsed_args.stateless:
            attrs['stateful'] = False
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        # NOTE(rtheis): Previous behavior did not raise a CommandError
        # if there were no updates. Maintain this behavior and issue
        # the update.
        client.update_security_group(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_set(client, obj, parsed_args)


class ShowSecurityGroup(command.ShowOne):
    _description = _("Display security group details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Security group to display (name or ID)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        obj = client.find_security_group(
            parsed_args.group, ignore_missing=False
        )
        display_columns, property_columns = _get_columns(obj)
        data = utils.get_item_properties(
            obj, property_columns, formatters=_formatters_network
        )
        return (display_columns, data)


class UnsetSecurityGroup(command.Command):
    _description = _("Unset security group properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar="<group>",
            help=_("Security group to modify (name or ID)"),
        )
        _tag.add_tag_option_to_parser_for_unset(parser, _('security group'))
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        obj = client.find_security_group(
            parsed_args.group, ignore_missing=False
        )

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_unset(client, obj, parsed_args)
