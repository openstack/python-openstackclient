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
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import parseractions
from openstackclient.common import utils


class CreateProject(show.ShowOne):
    """Create new project"""

    log = logging.getLogger(__name__ + '.CreateProject')

    def get_parser(self, prog_name):
        parser = super(CreateProject, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<project-name>',
            help='New project name',
        )
        parser.add_argument(
            '--domain',
            metavar='<project-domain>',
            help='Domain owning the project (name or ID)',
        )
        parser.add_argument(
            '--description',
            metavar='<project-description>',
            help='New project description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable project',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable project',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add for this project '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.domain:
            domain = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            ).id
        else:
            domain = None

        enabled = True
        if parsed_args.disable:
            enabled = False
        kwargs = {}
        if parsed_args.property:
            kwargs = parsed_args.property.copy()

        project = identity_client.projects.create(
            name=parsed_args.name,
            domain=domain,
            description=parsed_args.description,
            enabled=enabled,
            **kwargs
        )

        info = {}
        info.update(project._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteProject(command.Command):
    """Delete project"""

    log = logging.getLogger(__name__ + '.DeleteProject')

    def get_parser(self, prog_name):
        parser = super(DeleteProject, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help='Project to delete (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        project = utils.find_resource(
            identity_client.projects,
            parsed_args.project,
        )

        identity_client.projects.delete(project.id)
        return


class ListProject(lister.Lister):
    """List projects"""

    log = logging.getLogger(__name__ + '.ListProject')

    def get_parser(self, prog_name):
        parser = super(ListProject, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--domain',
            metavar='<project-domain>',
            help='Filter by a specific domain',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        if parsed_args.long:
            columns = ('ID', 'Name', 'Domain ID', 'Description', 'Enabled')
        else:
            columns = ('ID', 'Name')
        kwargs = {}
        if parsed_args.domain:
            kwargs['domain'] = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            ).id
        data = identity_client.projects.list(**kwargs)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetProject(command.Command):
    """Set project properties"""

    log = logging.getLogger(__name__ + '.SetProject')

    def get_parser(self, prog_name):
        parser = super(SetProject, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help='Project to change (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<new-project-name>',
            help='New project name',
        )
        parser.add_argument(
            '--domain',
            metavar='<project-domain>',
            help='New domain owning the project (name or ID)',
        )
        parser.add_argument(
            '--description',
            metavar='<project-description>',
            help='New project description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable project',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable project',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add for this project '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if (not parsed_args.name
                and not parsed_args.description
                and not parsed_args.domain
                and not parsed_args.enable
                and not parsed_args.property
                and not parsed_args.disable):
            return

        project = utils.find_resource(
            identity_client.projects,
            parsed_args.project,
        )

        kwargs = project._info
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.domain:
            kwargs['domain'] = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            ).id
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False
        if parsed_args.property:
            kwargs.update(parsed_args.property)
        if 'id' in kwargs:
            del kwargs['id']
        if 'domain_id' in kwargs:
            # Hack around broken Identity API arg names
            kwargs.update(
                {'domain': kwargs.pop('domain_id')}
            )

        identity_client.projects.update(project.id, **kwargs)
        return


class ShowProject(show.ShowOne):
    """Show project command"""

    log = logging.getLogger(__name__ + '.ShowProject')

    def get_parser(self, prog_name):
        parser = super(ShowProject, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help='Name or ID of project to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        project = utils.find_resource(identity_client.projects,
                                      parsed_args.project)

        info = {}
        info.update(project._info)
        return zip(*sorted(six.iteritems(info)))
