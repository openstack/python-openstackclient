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

from keystoneauth1 import exceptions as ks_exc
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common
from openstackclient.identity.v3 import tag

LOG = logging.getLogger(__name__)


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
            action=parseractions.KeyValueAction,
            dest='properties',
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
        identity_client = self.app.client_manager.identity

        domain = None
        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain).id

        parent = None
        if parsed_args.parent:
            parent = utils.find_resource(
                identity_client.projects,
                parsed_args.parent,
            ).id

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

        kwargs['tags'] = list(set(parsed_args.tags))

        options = {}
        if parsed_args.immutable is not None:
            options['immutable'] = parsed_args.immutable

        try:
            project = identity_client.projects.create(
                name=parsed_args.name,
                domain=domain,
                parent=parent,
                description=parsed_args.description,
                enabled=parsed_args.enabled,
                options=options,
                **kwargs,
            )
        except ks_exc.Conflict:
            if parsed_args.or_show:
                project = utils.find_resource(
                    identity_client.projects,
                    parsed_args.name,
                    domain_id=domain,
                )
                LOG.info(_('Returning existing project %s'), project.name)
            else:
                raise

        project._info.pop('links')
        return zip(*sorted(project._info.items()))


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
        identity_client = self.app.client_manager.identity

        domain = None
        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
        errors = 0
        for project in parsed_args.projects:
            try:
                if domain is not None:
                    project_obj = utils.find_resource(
                        identity_client.projects, project, domain_id=domain.id
                    )
                else:
                    project_obj = utils.find_resource(
                        identity_client.projects, project
                    )
                identity_client.projects.delete(project_obj.id)
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
        identity_client = self.app.client_manager.identity
        columns: tuple[str, ...] = ('ID', 'Name')
        if parsed_args.long:
            columns += ('Domain ID', 'Description', 'Enabled')
        kwargs = {}

        domain_id = None
        if parsed_args.domain:
            domain_id = common.find_domain(
                identity_client, parsed_args.domain
            ).id
            kwargs['domain'] = domain_id

        if parsed_args.parent:
            parent_id = common.find_project(
                identity_client, parsed_args.parent
            ).id
            kwargs['parent'] = parent_id

        if parsed_args.user:
            if parsed_args.domain:
                user_id = utils.find_resource(
                    identity_client.users,
                    parsed_args.user,
                    domain_id=domain_id,
                ).id
            else:
                user_id = utils.find_resource(
                    identity_client.users, parsed_args.user
                ).id

            kwargs['user'] = user_id

        if parsed_args.is_enabled is not None:
            kwargs['is_enabled'] = parsed_args.is_enabled

        tag.get_tag_filtering_args(parsed_args, kwargs)

        if parsed_args.my_projects:
            # NOTE(adriant): my-projects supersedes all the other filters.
            kwargs = {'user': self.app.client_manager.auth_ref.user_id}

        try:
            data = identity_client.projects.list(**kwargs)
        except ks_exc.Forbidden:
            # NOTE(adriant): if no filters, assume a forbidden is non-admin
            # wanting their own project list.
            if not kwargs:
                user = self.app.client_manager.auth_ref.user_id
                data = identity_client.projects.list(user=user)
            else:
                raise

        if parsed_args.sort:
            data = utils.sort_items(data, parsed_args.sort)

        return (
            columns,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
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
        identity_client = self.app.client_manager.identity

        project = common.find_project(
            identity_client, parsed_args.project, parsed_args.domain
        )

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
        tag.update_tags_in_args(parsed_args, project, kwargs)

        identity_client.projects.update(project.id, **kwargs)


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
        identity_client = self.app.client_manager.identity

        project_str = common._get_token_resource(
            identity_client, 'project', parsed_args.project, parsed_args.domain
        )

        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
            project = utils.find_resource(
                identity_client.projects, project_str, domain_id=domain.id
            )
        else:
            project = utils.find_resource(
                identity_client.projects, project_str
            )

        if parsed_args.parents or parsed_args.children:
            # NOTE(RuiChen): utils.find_resource() can't pass kwargs,
            #                if id query hit the result at first, so call
            #                identity manager.get() with kwargs directly.
            project = identity_client.projects.get(
                project.id,
                parents_as_ids=parsed_args.parents,
                subtree_as_ids=parsed_args.children,
            )

        project._info.pop('links')
        return zip(*sorted(project._info.items()))
