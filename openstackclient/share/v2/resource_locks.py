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

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any
import uuid

from manilaclient.common.apiclient import utils as apiutils
from manilaclient.common import constants
from openstackclient.identity import common as identity_common
from osc_lib import exceptions
from osc_lib import utils as osc_utils

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

LOCK_DETAIL_ATTRIBUTES = [
    'ID',
    'Resource Id',
    'Resource Type',
    'Resource Action',
    'Lock Context',
    'User Id',
    'Project Id',
    'Created At',
    'Updated At',
    'Lock Reason',
]

LOCK_SUMMARY_ATTRIBUTES = [
    'ID',
    'Resource Id',
    'Resource Type',
    'Resource Action',
]

RESOURCE_TYPE_MANAGERS = {
    'share': 'shares',
    'access_rule': 'share_access_rules',
}


# TODO(stephenfin): Move this to osc_lib since it's useful elsewhere (e.g.
# glance)
def is_uuid_like(value: str) -> bool:
    """Returns validation of a value as a UUID.

    :param val: Value to verify
    :type val: string
    :returns: bool

    .. versionchanged:: 1.1.1
       Support non-lowercase UUIDs.
    """
    try:
        formatted_value = (
            value.replace('urn:', '')
            .replace('uuid:', '')
            .strip('{}')
            .replace('-', '')
            .lower()
        )
        return str(uuid.UUID(value)).replace('-', '') == formatted_value
    except (TypeError, ValueError, AttributeError):
        return False


class CreateResourceLock(command.ShowOne):
    """Create a new resource lock."""

    _description = _("Lock a resource action from occurring on a resource")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'resource',
            metavar='<resource_name_or_id>',
            help=_('Name or ID of resource to lock.'),
        )
        parser.add_argument(
            'resource_type',
            metavar='<resource_type>',
            help=_('Type of the resource (e.g.: share, access).'),
        )
        parser.add_argument(
            '--resource-action',
            '--resource_action',
            metavar='<resource_action>',
            default='delete',
            help=_('Action to lock on the resource (default="delete")'),
        )
        parser.add_argument(
            '--lock-reason',
            '--lock_reason',
            '--reason',
            metavar='<lock_reason>',
            help=_('Reason for the resource lock.'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], tuple[Any, ...]]:
        share_client = self.app.client_manager.share
        resource_type = parsed_args.resource_type
        if resource_type not in RESOURCE_TYPE_MANAGERS:
            raise exceptions.CommandError(_("Unsupported resource type"))
        res_manager = RESOURCE_TYPE_MANAGERS[resource_type]

        resource = osc_utils.find_resource(
            getattr(share_client, res_manager), parsed_args.resource
        )
        resource_lock = share_client.resource_locks.create(
            resource.id,
            resource_type,
            parsed_args.resource_action,
            parsed_args.lock_reason,
        )

        resource_lock._info.pop('links', None)

        return self.dict2columns(resource_lock._info)


class DeleteResourceLock(command.Command):
    """Remove one or more resource locks."""

    _description = _("Remove one or more resource locks")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'lock',
            metavar='<lock>',
            nargs='+',
            help=_('ID(s) of the lock(s).'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share
        failure_count = 0

        for lock in parsed_args.lock:
            try:
                lock = apiutils.find_resource(
                    share_client.resource_locks, lock
                )
                lock.delete()
            except Exception as e:
                failure_count += 1
                LOG.error(
                    _("Failed to delete %(lock)s: %(e)s"),
                    {'lock': lock, 'e': e},
                )

        if failure_count > 0:
            raise exceptions.CommandError(
                _("Unable to delete some or all of the specified locks.")
            )


class ListResourceLock(command.Lister):
    """Lists all resource locks."""

    _description = _("Lists all resource locks")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            help=_("Filter resource locks for all projects. (Admin only)."),
        )
        parser.add_argument(
            '--project',
            default=None,
            help=_(
                "Filter resource locks for specific project by name or ID, "
                "combine with --all-projects (Admin only)."
            ),
        )
        parser.add_argument(
            '--user',
            default=None,
            help=_(
                "Filter resource locks for specific user by name or ID, "
                "combine with --all-projects to search across projects "
                "(Admin only)."
            ),
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            default=None,
            help=_('Filter resource locks by ID. Default=None.'),
        )
        parser.add_argument(
            '--resource',
            '--resource-id',
            '--resource_id',
            default=None,
            metavar='<resource-id>',
            dest='resource',
            help=_(
                "Filter resource locks for a resource by ID, specify "
                "--resource-type to look up by name."
            ),
        )
        parser.add_argument(
            '--resource-type',
            '--resource_type',
            default=None,
            metavar='<resource_type>',
            help=_("Filter resource locks by type of resource."),
        )
        parser.add_argument(
            '--resource-action',
            '--resource_action',
            default=None,
            metavar='<resource_action>',
            help=_("Filter resource locks by resource action."),
        )

        parser.add_argument(
            '--lock-context',
            '--lock_context',
            '--context',
            default=None,
            choices=['user', 'admin', 'service'],
            metavar='<lock_context>',
            help=_("Filter resource locks by context."),
        )
        parser.add_argument(
            '--since',
            default=None,
            metavar='<created_since>',
            help=_(
                "Filter resource locks created since given date. "
                "The date format must be conforming to ISO8601. "
            ),
        )
        parser.add_argument(
            '--before',
            default=None,
            metavar='<created_before>',
            help=_(
                "Filter resource locks created before given date. "
                "The date format must be conforming to ISO8601. "
            ),
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            default=None,
            help=_("Number of resource locks to list. (Default=None)"),
        )
        parser.add_argument(
            '--offset',
            metavar="<offset>",
            default=None,
            help=_(
                'Starting position of resource lock records '
                'in a paginated list.'
            ),
        )
        parser.add_argument(
            '--sort-key',
            '--sort_key',
            metavar='<sort_key>',
            type=str,
            default=None,
            choices=constants.RESOURCE_LOCK_SORT_KEY_VALUES,
            help=(
                f'Key to be sorted, available keys are '
                f'{constants.RESOURCE_LOCK_SORT_KEY_VALUES}. Default=None.'
            ),
        )
        parser.add_argument(
            '--sort-dir',
            '--sort_dir',
            metavar='<sort_dir>',
            type=str,
            default=None,
            choices=constants.SORT_DIR_VALUES,
            help=(
                f'Sort direction, available values are '
                f'{constants.SORT_DIR_VALUES}. OPTIONAL: Default=None.'
            ),
        )
        parser.add_argument(
            '--detailed',
            dest='detailed',
            metavar='<0|1>',
            nargs='?',
            type=int,
            const=1,
            default=0,
            help=_("Show detailed information about filtered resource locks."),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        share_client = self.app.client_manager.share
        identity_client = self.app.client_manager.identity

        columns = (
            LOCK_SUMMARY_ATTRIBUTES
            if not parsed_args.detailed
            else LOCK_DETAIL_ATTRIBUTES
        )

        project_id = None
        user_id = None

        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
        if parsed_args.user:
            user_id = identity_common.find_user(
                identity_client, parsed_args.user, parsed_args.user_domain
            ).id
        # set all_projects when using project option
        all_projects = bool(parsed_args.project) or parsed_args.all_projects

        resource_id = parsed_args.resource
        resource_type = parsed_args.resource_type
        if resource_type is not None:
            if resource_type not in RESOURCE_TYPE_MANAGERS:
                raise exceptions.CommandError(_("Unsupported resource type"))
            if resource_id is not None:
                res_manager = RESOURCE_TYPE_MANAGERS[resource_type]
                resource_id = osc_utils.find_resource(
                    getattr(share_client, res_manager), parsed_args.resource
                ).id
        elif resource_id and not is_uuid_like(resource_id):
            raise exceptions.CommandError(
                _("Provide resource ID or specify --resource-type.")
            )

        search_opts = {
            'all_projects': all_projects,
            'project_id': project_id,
            'user_id': user_id,
            'id': parsed_args.id,
            'resource_id': resource_id,
            'resource_type': parsed_args.resource_type,
            'resource_action': parsed_args.resource_action,
            'lock_context': parsed_args.lock_context,
            'created_before': parsed_args.before,
            'created_since': parsed_args.since,
            'limit': parsed_args.limit,
            'offset': parsed_args.offset,
        }

        resource_locks = share_client.resource_locks.list(
            search_opts=search_opts,
            sort_key=parsed_args.sort_key,
            sort_dir=parsed_args.sort_dir,
        )

        return (
            columns,
            (
                osc_utils.get_item_properties(m, columns)
                for m in resource_locks
            ),
        )


class ShowResourceLock(command.ShowOne):
    """Show details about a resource lock."""

    _description = _("Show details about a resource lock")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'lock', metavar='<lock>', help=_('ID of resource lock to show.')
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], tuple[Any, ...]]:
        share_client = self.app.client_manager.share

        resource_lock = apiutils.find_resource(
            share_client.resource_locks, parsed_args.lock
        )

        return (
            LOCK_DETAIL_ATTRIBUTES,
            osc_utils.get_dict_properties(
                resource_lock._info, LOCK_DETAIL_ATTRIBUTES
            ),
        )


class SetResourceLock(command.Command):
    """Set resource lock properties."""

    _description = _("Update resource lock properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'lock', metavar='<lock>', help=_('ID of lock to update.')
        )
        parser.add_argument(
            '--resource-action',
            '--resource_action',
            metavar='<resource_action>',
            help=_('Resource action to set in the resource lock'),
        )
        parser.add_argument(
            '--lock-reason',
            '--lock_reason',
            '--reason',
            dest='lock_reason',
            help=_("Reason for the resource lock"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share

        update_kwargs = {}
        if parsed_args.resource_action is not None:
            update_kwargs['resource_action'] = parsed_args.resource_action
        if parsed_args.lock_reason is not None:
            update_kwargs['lock_reason'] = parsed_args.lock_reason
        if update_kwargs:
            share_client.resource_locks.update(
                parsed_args.lock, **update_kwargs
            )


class UnsetResourceLock(command.Command):
    """Unsets a property on a resource lock."""

    _description = _("Remove resource lock properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'lock', metavar='<lock>', help=_('ID of resource lock to update.')
        )
        parser.add_argument(
            '--lock-reason',
            '--lock_reason',
            '--reason',
            dest='lock_reason',
            action='store_true',
            default=False,
            help=_("Unset the lock reason. (Default=False)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share

        if parsed_args.lock_reason:
            share_client.resource_locks.update(
                parsed_args.lock, lock_reason=None
            )
