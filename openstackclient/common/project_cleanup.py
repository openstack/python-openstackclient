#   Copyright 2020 OpenStack Foundation
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

import getpass
import logging
import os
import queue
import typing as ty

from cliff.formatters import table
from osc_lib.command import command

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)


def ask_user_yesno(msg):
    """Ask user Y/N question

    :param str msg: question text
    :return bool: User choice
    """
    while True:
        answer = getpass.getpass('{} [{}]: '.format(msg, 'y/n'))
        if answer in ('y', 'Y', 'yes'):
            return True
        elif answer in ('n', 'N', 'no'):
            return False


class ProjectCleanup(command.Command):
    _description = _("Clean resources associated with a project")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        action_group = parser.add_mutually_exclusive_group()
        action_group.add_argument(
            '--dry-run',
            action='store_true',
            help=_("List a project's resources but do not delete them"),
        )
        action_group.add_argument(
            '--auto-approve',
            action='store_true',
            help=_("Delete resources without asking for confirmation"),
        )
        project_group = parser.add_mutually_exclusive_group(required=True)
        project_group.add_argument(
            '--auth-project',
            action='store_true',
            help=_('Delete resources of the project used to authenticate'),
        )
        project_group.add_argument(
            '--project',
            metavar='<project>',
            help=_('Project to clean (name or ID)'),
        )
        parser.add_argument(
            '--created-before',
            metavar='<YYYY-MM-DDTHH24:MI:SS>',
            help=_('Only delete resources created before the given time'),
        )
        parser.add_argument(
            '--updated-before',
            metavar='<YYYY-MM-DDTHH24:MI:SS>',
            help=_('Only delete resources updated before the given time'),
        )
        parser.add_argument(
            '--skip-resource',
            metavar='<resource>',
            help='Skip cleanup of specific resource (repeat if necessary)',
            action='append',
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        sdk = self.app.client_manager.sdk_connection

        if parsed_args.auth_project:
            project_connect = sdk
        elif parsed_args.project:
            project = sdk.identity.find_project(
                name_or_id=parsed_args.project, ignore_missing=False
            )
            project_connect = sdk.connect_as_project(project)

        if project_connect:
            status_queue: queue.Queue[ty.Any] = queue.Queue()
            parsed_args.max_width = int(
                os.environ.get('CLIFF_MAX_TERM_WIDTH', 0)
            )
            parsed_args.fit_width = bool(
                int(os.environ.get('CLIFF_FIT_WIDTH', 0))
            )
            parsed_args.print_empty = False
            table_fmt = table.TableFormatter()

            self.log.info('Searching resources...')

            filters = {}
            if parsed_args.created_before:
                filters['created_at'] = parsed_args.created_before

            if parsed_args.updated_before:
                filters['updated_at'] = parsed_args.updated_before

            project_connect.project_cleanup(
                dry_run=True,
                status_queue=status_queue,
                filters=filters,
                skip_resources=parsed_args.skip_resource,
            )

            data = []
            while not status_queue.empty():
                resource = status_queue.get_nowait()
                data.append(
                    (type(resource).__name__, resource.id, resource.name)
                )
                status_queue.task_done()
            status_queue.join()
            table_fmt.emit_list(
                ('Type', 'ID', 'Name'), data, self.app.stdout, parsed_args
            )

            if parsed_args.dry_run:
                return

            if not parsed_args.auto_approve:
                if not ask_user_yesno(
                    _("These resources will be deleted. Are you sure")
                ):
                    return

            self.log.warning(_('Deleting resources'))

            project_connect.project_cleanup(
                dry_run=False,
                status_queue=status_queue,
                filters=filters,
                skip_resources=parsed_args.skip_resource,
            )
