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

import argparse
import logging
from collections.abc import Iterable, Sequence
from typing import Any

from manilaclient.common.apiclient import utils as apiutils
from osc_lib import exceptions
from osc_lib import utils as oscutils

from openstackclient import command
from openstackclient.common import envvars
from openstackclient.i18n import _
from openstackclient.share import utils

LOG = logging.getLogger(__name__)

ATTRIBUTES = [
    'id',
    'name',
    'share_types',
    'visibility',
    'is_default',
    'group_specs',
]


class CreateShareGroupType(command.ShowOne):
    """Create new share group type."""

    _description = _("Create new share group type")

    log = logging.getLogger(__name__ + ".CreateShareGroupType")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar="<name>",
            default=None,
            help=_('Share group type name'),
        )
        parser.add_argument(
            "share_types",
            metavar="<share-types>",
            nargs="+",
            default=None,
            help=_(
                "List of share type names or IDs. Example:"
                " my-share-type-1 my-share-type-2"
            ),
        )
        parser.add_argument(
            "--group-specs",
            type=str,
            nargs='*',
            metavar='<key=value>',
            default=None,
            help=_(
                "Share Group type extra specs by key and value."
                " OPTIONAL: Default=None. Example:"
                " --group-specs consistent_snapshot_support=host."
            ),
        )
        parser.add_argument(
            '--public',
            metavar="<public>",
            default=True,
            help=_('Make type accessible to the public (default true).'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], tuple[Any, ...]]:
        share_client = self.app.client_manager.share

        kwargs = {'name': parsed_args.name}

        share_types_list = []
        for share_type in parsed_args.share_types:
            try:
                share_type_obj = apiutils.find_resource(
                    share_client.share_types, share_type
                )

                share_types_list.append(share_type_obj.name)
            except Exception as e:
                msg = _(
                    "Failed to find the share type with name or ID "
                    "'%(share_type)s': %(e)s"
                )
                raise exceptions.CommandError(
                    msg % {'share_type': share_type, 'e': e}
                )

        kwargs['share_types'] = share_types_list

        if parsed_args.public:
            kwargs['is_public'] = envvars.bool_from_str(parsed_args.public)

        group_specs: dict[str, Any] = {}
        if parsed_args.group_specs:
            for item in parsed_args.group_specs:
                group_specs = utils.extract_group_specs(group_specs, [item])

        kwargs['group_specs'] = group_specs

        share_group_type = share_client.share_group_types.create(**kwargs)

        formatter = parsed_args.formatter

        formatted_group_type = utils.format_share_group_type(
            share_group_type, formatter
        )

        return (
            ATTRIBUTES,
            oscutils.get_dict_properties(formatted_group_type, ATTRIBUTES),
        )


class DeleteShareGroupType(command.Command):
    """Delete a share group type."""

    _description = _("Delete a share group type")

    log = logging.getLogger(__name__ + ".DeleteShareGroupType")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group_types',
            metavar="<share-group-types>",
            nargs="+",
            help=_("Name or ID of the share group type(s) to delete"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share
        result = 0

        for share_group_type in parsed_args.share_group_types:
            try:
                share_group_type_obj = apiutils.find_resource(
                    share_client.share_group_types, share_group_type
                )

                share_client.share_group_types.delete(share_group_type_obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete share group type with "
                        "name or ID '%(share_group_type)s': %(e)s"
                    ),
                    {'share_group_type': share_group_type, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.share_group_types)
            msg = _(
                "%(result)s of %(total)s share group types failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListShareGroupType(command.Lister):
    """List Share Group Types."""

    _description = _("List share types")

    log = logging.getLogger(__name__ + ".ListShareGroupType")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help=_(
                'Display all share group types whether public or private. '
                'Default=False. (Admin only)'
            ),
        )
        parser.add_argument(
            '--group-specs',
            type=str,
            nargs='*',
            metavar='<key=value>',
            default=None,
            help=_('Filter share group types with group specs (key=value).'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        share_client = self.app.client_manager.share

        search_opts = {}
        if parsed_args.group_specs:
            search_opts = {
                'group_specs': utils.extract_group_specs(
                    extra_specs={}, specs_to_add=parsed_args.group_specs
                )
            }

        formatter = parsed_args.formatter

        share_group_types = share_client.share_group_types.list(
            search_opts=search_opts, show_all=parsed_args.all
        )

        formatted_types = []
        for share_group_type in share_group_types:
            formatted_types.append(
                utils.format_share_group_type(share_group_type, formatter)
            )

        column_headers = utils.format_column_headers(ATTRIBUTES)
        values = (
            oscutils.get_dict_properties(sgt, ATTRIBUTES)
            for sgt in formatted_types
        )

        return (column_headers, values)


class ShowShareGroupType(command.ShowOne):
    """Show Share Group Types."""

    _description = _("Show share group types")

    log = logging.getLogger(__name__ + ".ShowShareGroupType")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group_type',
            metavar="<share-group-type>",
            help=_("Name or ID of the share group type to show"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], tuple[Any, ...]]:
        share_client = self.app.client_manager.share

        share_group_type = apiutils.find_resource(
            share_client.share_group_types, parsed_args.share_group_type
        )

        share_group_type_obj = share_client.share_group_types.get(
            share_group_type
        )

        formatter = parsed_args.formatter

        formatted_group_type = utils.format_share_group_type(
            share_group_type_obj, formatter
        )

        return (
            ATTRIBUTES,
            oscutils.get_dict_properties(formatted_group_type, ATTRIBUTES),
        )


class SetShareGroupType(command.Command):
    """Set share type properties."""

    _description = _("Set share group type properties")

    log = logging.getLogger(__name__ + ".SetShareGroupType")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group_type',
            metavar="<share-group-type>",
            help=_("Name or ID of the share group type to modify"),
        )
        parser.add_argument(
            "--group-specs",
            type=str,
            nargs='*',
            metavar='<key=value>',
            default=None,
            help=_(
                "Extra specs key and value of share group type that will be"
                " used for share type creation. OPTIONAL: Default=None."
                " Example: --group-specs consistent-snapshot-support=True"
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share

        try:
            share_group_type_obj = apiutils.find_resource(
                share_client.share_group_types, parsed_args.share_group_type
            )
        except Exception as e:
            msg = _(
                "Failed to find the share group type with "
                "name or ID '%(share_group_type)s': %(e)s"
            )
            raise exceptions.CommandError(
                msg
                % {'share_group_type': parsed_args.share_group_type, 'e': e}
            )

        if parsed_args.group_specs:
            group_specs = utils.extract_group_specs(
                extra_specs={}, specs_to_add=parsed_args.group_specs
            )
            try:
                share_group_type_obj.set_keys(group_specs)
            except Exception as e:
                raise exceptions.CommandError(
                    f"Failed to set share group type key: {e}"
                )


class UnsetShareGroupType(command.Command):
    """Unset share group type extra specs."""

    _description = _("Unset share group type extra specs")

    log = logging.getLogger(__name__ + ".UnsetShareGroupType")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group_type',
            metavar="<share-group-type>",
            help=_("Name or ID of the share grouptype to modify"),
        )
        parser.add_argument(
            'group_specs',
            metavar='<key>',
            nargs='+',
            help=_('Remove group specs from this share group type'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share

        try:
            share_group_type_obj = apiutils.find_resource(
                share_client.share_group_types, parsed_args.share_group_type
            )
        except Exception as e:
            msg = _(
                "Failed to find the share group type with "
                "name or ID '%(share_group_type)s': %(e)s"
            )
            raise exceptions.CommandError(
                msg
                % {'share_group_type': parsed_args.share_group_type, 'e': e}
            )

        if parsed_args.group_specs:
            try:
                share_group_type_obj.unset_keys(parsed_args.group_specs)
            except Exception as e:
                raise exceptions.CommandError(
                    f"Failed to remove share type group extra spec: {e}"
                )
