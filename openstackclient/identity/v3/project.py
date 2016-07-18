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
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class CreateProject(command.ShowOne):
    """Create new project"""

    def get_parser(self, prog_name):
        parser = super(CreateProject, self).get_parser(prog_name)
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
            help=_('Enable project'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable project'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Add a property to <name> '
                   '(repeat option to set multiple properties)'),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing project'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain = None
        if parsed_args.domain:
            domain = common.find_domain(identity_client,
                                        parsed_args.domain).id

        parent = None
        if parsed_args.parent:
            parent = utils.find_resource(
                identity_client.projects,
                parsed_args.parent,
            ).id

        enabled = True
        if parsed_args.disable:
            enabled = False
        kwargs = {}
        if parsed_args.property:
            kwargs = parsed_args.property.copy()

        try:
            project = identity_client.projects.create(
                name=parsed_args.name,
                domain=domain,
                parent=parent,
                description=parsed_args.description,
                enabled=enabled,
                **kwargs
            )
        except ks_exc.Conflict:
            if parsed_args.or_show:
                project = utils.find_resource(identity_client.projects,
                                              parsed_args.name,
                                              domain_id=domain)
                LOG.info(_('Returning existing project %s'), project.name)
            else:
                raise

        project._info.pop('links')
        return zip(*sorted(six.iteritems(project._info)))


class DeleteProject(command.Command):
    """Delete project(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteProject, self).get_parser(prog_name)
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
        for project in parsed_args.projects:
            if domain is not None:
                project_obj = utils.find_resource(identity_client.projects,
                                                  project,
                                                  domain_id=domain.id)
            else:
                project_obj = utils.find_resource(identity_client.projects,
                                                  project)
            identity_client.projects.delete(project_obj.id)


class ListProject(command.Lister):
    """List projects"""

    def get_parser(self, prog_name):
        parser = super(ListProject, self).get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Filter projects by <domain> (name or ID)'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Filter projects by <user> (name or ID)'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        if parsed_args.long:
            columns = ('ID', 'Name', 'Domain ID', 'Description', 'Enabled')
        else:
            columns = ('ID', 'Name')
        kwargs = {}

        domain_id = None
        if parsed_args.domain:
            domain_id = common.find_domain(identity_client,
                                           parsed_args.domain).id
            kwargs['domain'] = domain_id

        if parsed_args.user:
            if parsed_args.domain:
                user_id = utils.find_resource(identity_client.users,
                                              parsed_args.user,
                                              domain_id=domain_id).id
            else:
                user_id = utils.find_resource(identity_client.users,
                                              parsed_args.user).id

            kwargs['user'] = user_id

        data = identity_client.projects.list(**kwargs)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetProject(command.Command):
    """Set project properties"""

    def get_parser(self, prog_name):
        parser = super(SetProject, self).get_parser(prog_name)
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
            help=_('Enable project'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable project'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on <project> '
                   '(repeat option to set multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        project = common.find_project(identity_client,
                                      parsed_args.project,
                                      parsed_args.domain)

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False
        if parsed_args.property:
            kwargs.update(parsed_args.property)

        identity_client.projects.update(project.id, **kwargs)


class ShowProject(command.ShowOne):
    """Display project details"""

    def get_parser(self, prog_name):
        parser = super(ShowProject, self).get_parser(prog_name)
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

        project_str = common._get_token_resource(identity_client, 'project',
                                                 parsed_args.project)

        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
            project = utils.find_resource(
                identity_client.projects,
                project_str,
                domain_id=domain.id,
                parents_as_list=parsed_args.parents,
                subtree_as_list=parsed_args.children)
        else:
            project = utils.find_resource(
                identity_client.projects,
                project_str,
                parents_as_list=parsed_args.parents,
                subtree_as_list=parsed_args.children)

        if project._info.get('parents'):
            project._info['parents'] = [str(p['project']['id'])
                                        for p in project._info['parents']]
        if project._info.get('subtree'):
            project._info['subtree'] = [str(p['project']['id'])
                                        for p in project._info['subtree']]

        project._info.pop('links')
        return zip(*sorted(six.iteritems(project._info)))
