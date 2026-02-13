#   Copyright 2012-2013 OpenStack Foundation
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

"""Project action implementations"""

import logging

from openstack import exceptions as sdk_exc
from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common
from openstackclient.identity.v3 import tag

LOG = logging.getLogger(__name__)


def _format_project(project):
    # NOTE(0weng): Projects allow unknown attributes in the body, so extract
    # the column names separately.
    (column_headers, columns) = utils.get_osc_show_columns_for_sdk_resource(
        project,
        {'is_enabled': 'enabled'},
        ['links', 'location', 'parents_as_ids', 'subtree_as_ids'],
    )

    return (
        column_headers,
        utils.get_item_properties(project, columns),
    )


class CreateProject(command.ShowOne):
    _description = _("Create new project")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<project-name>',
            help=_('New project name'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain owning the project (name or ID)'),
        )
        parser.add_argument(
            '--parent',
            metavar='<project>',
            help=_('Parent of the project (name or ID)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Project description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            dest='enabled',
            default=True,
            help=_('Enable project'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_false',
            dest='enabled',
            default=True,
            help=_('Disable project'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            dest='properties',
            action=parseractions.KeyValueAction,
            help=_(
                'Add a property to <name> '
                '(repeat option to set multiple properties)'
            ),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing project'),
        )
        common.add_resource_option_to_parser(parser)
        tag.add_tag_option_to_parser_for_create(parser, _('project'))
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}

        if parsed_args.properties:
            kwargs = parsed_args.properties.copy()

        if 'is_domain' in kwargs.keys():
            if kwargs['is_domain'].lower() == "true":
                kwargs['is_domain'] = True
            elif kwargs['is_domain'].lower() == "false":
                kwargs['is_domain'] = False
            elif kwargs['is_domain'].lower() == "none":
                kwargs['is_domain'] = None

        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.name:
            kwargs['name'] = parsed_args.name

        domain = None
        if parsed_args.domain:
            domain = common.find_domain_id_sdk(
                identity_client, parsed_args.domain
            )
            kwargs['domain_id'] = domain

        if parsed_args.parent:
            kwargs['parent_id'] = common.find_project_id_sdk(
                identity_client,
                parsed_args.parent,
                domain_name_or_id=domain,
            )

        kwargs['is_enabled'] = parsed_args.enabled

        if parsed_args.tags:
            kwargs['tags'] = list(set(parsed_args.tags))

        if parsed_args.immutable is not None:
            kwargs['options'] = {'immutable': parsed_args.immutable}

        try:
            project = identity_client.create_project(
                **kwargs,
            )
        except sdk_exc.ConflictException:
            if parsed_args.or_show:
                if parsed_args.domain:
                    project = identity_client.find_project(
                        parsed_args.name,
                        domain_id=domain,
                        ignore_missing=False,
                    )
                else:
                    project = identity_client.find_project(
                        parsed_args.name, ignore_missing=False
                    )
                LOG.info(_('Returning existing project %s'), project.name)
            else:
                raise

        return _format_project(project)


class DeleteProject(command.Command):
    _description = _(
        "Delete project(s). This command will remove specified "
        "existing project(s) if an active user is authorized to do "
        "this. If there are resources managed by other services "
        "(for example, Nova, Neutron, Cinder) associated with "
        "specified project(s), delete operation will proceed "
        "regardless."
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'projects',
            metavar='<project>',
            nargs="+",
            help=_('Project(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain owning <project> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        errors = 0
        for project in parsed_args.projects:
            try:
                project = common.find_project_id_sdk(
                    identity_client,
                    project,
                    domain_name_or_id=parsed_args.domain,
                    validate_actor_existence=True,
                    validate_domain_actor_existence=False,
                )
                identity_client.delete_project(project)
            except Exception as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to delete project with "
                        "name or ID '%(project)s': %(e)s"
                    ),
                    {'project': project, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.projects)
            msg = _("%(errors)s of %(total)s projects failed to delete.") % {
                'errors': errors,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListProject(command.Lister):
    _description = _("List projects")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Filter projects by <domain> (name or ID)'),
        )
        parser.add_argument(
            '--parent',
            metavar='<parent>',
            help=_('Filter projects whose parent is <parent> (name or ID)'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Filter projects by <user> (name or ID)'),
        )
        parser.add_argument(
            '--my-projects',
            action='store_true',
            help=_(
                'List projects for the authenticated user. '
                'Supersedes other filters.'
            ),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_(
                'Sort output by selected keys and directions (asc or desc) '
                '(default: asc), repeat this option to specify multiple '
                'keys and directions.'
            ),
        )
        parser.add_argument(
            '--enabled',
            action='store_true',
            dest='is_enabled',
            default=None,
            help=_('List only enabled projects'),
        )
        parser.add_argument(
            '--disabled',
            action='store_false',
            dest='is_enabled',
            default=None,
            help=_('List only disabled projects'),
        )
        tag.add_tag_filtering_option_to_parser(parser, _('projects'))
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        column_headers: tuple[str, ...] = ('ID', 'Name')
        if parsed_args.long:
            column_headers += ('Domain ID', 'Description', 'Enabled')

        columns: tuple[str, ...] = ('id', 'name')
        if parsed_args.long:
            columns += ('domain_id', 'description', 'is_enabled')

        kwargs = {}

        domain_id = None
        if parsed_args.domain:
            domain_id = common.find_domain_id_sdk(
                identity_client, parsed_args.domain
            )
            kwargs['domain_id'] = domain_id

        if parsed_args.parent:
            parent_id = common.find_project_id_sdk(
                identity_client,
                parsed_args.parent,
                domain_name_or_id=domain_id,
            )
            kwargs['parent_id'] = parent_id

        user = None
        if parsed_args.user:
            if parsed_args.domain:
                user = common.find_user_id_sdk(
                    identity_client,
                    parsed_args.user,
                    domain_name_or_id=domain_id,
                )
            else:
                user = common.find_user_id_sdk(
                    identity_client,
                    parsed_args.user,
                )

        if parsed_args.is_enabled is not None:
            kwargs['is_enabled'] = parsed_args.is_enabled

        tag.get_tag_filtering_args(parsed_args, kwargs)

        if parsed_args.my_projects:
            # NOTE(adriant): my-projects supersedes all the other filters.
            kwargs = {}
            user = self.app.client_manager.auth_ref.user_id

        if user:
            data = identity_client.user_projects(user, **kwargs)
        else:
            try:
                data = identity_client.projects(**kwargs)
            except sdk_exc.ForbiddenException:
                # NOTE(adriant): if no filters, assume a forbidden is non-admin
                # wanting their own project list.
                if not kwargs:
                    user = self.app.client_manager.auth_ref.user_id
                    data = identity_client.user_projects(user)
                else:
                    raise

        if parsed_args.sort:
            data = utils.sort_items(data, parsed_args.sort)

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class SetProject(command.Command):
    _description = _("Set project properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Project to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set project name'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain owning <project> (name or ID)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set project description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            dest='enabled',
            default=None,
            help=_('Enable project'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_false',
            dest='enabled',
            default=None,
            help=_('Disable project'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            dest='properties',
            action=parseractions.KeyValueAction,
            help=_(
                'Set a property on <project> '
                '(repeat option to set multiple properties)'
            ),
        )
        common.add_resource_option_to_parser(parser)
        tag.add_tag_option_to_parser_for_set(parser, _('project'))
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.enabled is not None:
            kwargs['enabled'] = parsed_args.enabled
        if parsed_args.immutable is not None:
            kwargs['options'] = {'immutable': parsed_args.immutable}
        if parsed_args.properties:
            kwargs.update(parsed_args.properties)

        if parsed_args.domain:
            domain = common.find_domain_id_sdk(
                identity_client,
                parsed_args.domain,
                validate_actor_existence=False,
            )
            project = identity_client.find_project(
                parsed_args.project,
                domain_id=domain,
                ignore_missing=True,
            )
        else:
            project = identity_client.find_project(
                parsed_args.project,
                ignore_missing=True,
            )

        if (
            parsed_args.tags
            or parsed_args.remove_tags
            or parsed_args.clear_tags
        ):
            existing_tags = []
            if project:
                existing_tags = project.tags

            if parsed_args.clear_tags:
                kwargs['tags'] = []
            else:
                existing_tags_set = set(existing_tags)
                if parsed_args.remove_tags:
                    tags = sorted(
                        existing_tags_set - set(parsed_args.remove_tags)
                    )
                if parsed_args.tags:
                    tags = sorted(
                        existing_tags_set.union(set(parsed_args.tags))
                    )
                kwargs['tags'] = tags

        project_id = project.id if project else parsed_args.project

        identity_client.update_project(project_id, **kwargs)


class ShowProject(command.ShowOne):
    _description = _("Display project details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Project to display (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain owning <project> (name or ID)'),
        )
        parser.add_argument(
            '--parents',
            action='store_true',
            default=False,
            help=_('Show the project\'s parents as a list'),
        )
        parser.add_argument(
            '--children',
            action='store_true',
            default=False,
            help=_('Show project\'s subtree (children) as a list'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}

        domain = None
        if parsed_args.domain:
            domain = common.find_domain_id_sdk(
                identity_client, parsed_args.domain
            )

            kwargs['domain_id'] = domain

        # Get project id first; otherwise, find_project() can't find
        # parents/children if only project name was given
        project = common.find_project_id_sdk(
            identity_client,
            parsed_args.project,
            domain_name_or_id=domain,
            validate_actor_existence=False,
            validate_domain_actor_existence=False,
        )

        # Include these options as query parameters if they are provided
        if parsed_args.parents:
            kwargs['parents_as_ids'] = True
        if parsed_args.children:
            kwargs['subtree_as_ids'] = True

        project = identity_client.find_project(
            project, **kwargs, ignore_missing=False
        )

        return _format_project(project)
