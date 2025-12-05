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
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common

LOG = logging.getLogger(__name__)


class ShareGroupTypeAccessAllow(command.Command):
    """Allow a project to access a share group type."""

    _description = _(
        "Allow a project to access a share group type (Admin only)."
    )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group_type',
            metavar="<share-group-type>",
            help=_("Share group type name or ID to allow access to."),
        )
        parser.add_argument(
            'projects',
            metavar="<project>",
            nargs="+",
            help=_("Project Name or ID to add share group type access for."),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share
        identity_client = self.app.client_manager.identity
        result = 0

        share_group_type = apiutils.find_resource(
            share_client.share_group_types, parsed_args.share_group_type
        )

        for project in parsed_args.projects:
            try:
                project_obj = identity_common.find_project(
                    identity_client, project, parsed_args.project_domain
                )

                share_client.share_group_type_access.add_project_access(
                    share_group_type, project_obj.id
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to allow access for project '%(project)s' "
                        "to share group type with name or ID "
                        "'%(share_group_type)s': %(e)s"
                    ),
                    {
                        'project': project,
                        'share_group_type': share_group_type,
                        'e': e,
                    },
                )

        if result > 0:
            total = len(parsed_args.projects)
            msg = _(
                "Failed to allow access to %(result)s of %(total)s projects"
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListShareGroupTypeAccess(command.Lister):
    """Get access list for share group type."""

    _description = _("Get access list for share group type (Admin only).")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group_type',
            metavar="<share-group-type>",
            help=_("Filter results by share group type name or ID."),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        share_client = self.app.client_manager.share

        share_group_type = apiutils.find_resource(
            share_client.share_group_types, parsed_args.share_group_type
        )

        if share_group_type._info.get('is_public'):
            raise exceptions.CommandError(
                'Forbidden to get access list for public share group type.'
            )

        data = share_client.share_group_type_access.list(share_group_type)

        columns = ['Project ID']
        values = (oscutils.get_item_properties(s, columns) for s in data)

        return (columns, values)


class ShareGroupTypeAccessDeny(command.Command):
    """Deny a project to access a share group type."""

    _description = _(
        "Deny a project to access a share group type (Admin only)."
    )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group_type',
            metavar="<share-group-type>",
            help=_("Share group type name or ID to deny access from"),
        )
        parser.add_argument(
            'projects',
            metavar="<project>",
            nargs="+",
            help=_(
                "Project Name(s) or ID(s) to deny share group type access for."
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share
        identity_client = self.app.client_manager.identity
        result = 0

        share_group_type = apiutils.find_resource(
            share_client.share_group_types, parsed_args.share_group_type
        )

        for project in parsed_args.projects:
            try:
                project_obj = identity_common.find_project(
                    identity_client, project, parsed_args.project_domain
                )

                share_client.share_group_type_access.remove_project_access(
                    share_group_type, project_obj.id
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to deny access for project '%(project)s' "
                        "to share group type with name or ID "
                        "'%(share_group_type)s': %(e)s"
                    ),
                    {
                        'project': project,
                        'share_group_type': share_group_type,
                        'e': e,
                    },
                )

        if result > 0:
            total = len(parsed_args.projects)
            msg = _(
                "Failed to deny access to %(result)s of %(total)s projects"
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)
