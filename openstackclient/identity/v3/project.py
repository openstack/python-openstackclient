#   Copyright 2012-2013 OpenStack, LLC.
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
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateProject(show.ShowOne):
    """Create project command"""

    log = logging.getLogger(__name__ + '.CreateProject')

    def get_parser(self, prog_name):
        parser = super(CreateProject, self).get_parser(prog_name)
        parser.add_argument(
            'project_name',
            metavar='<project-name>',
            help='New project name')
        parser.add_argument(
            '--domain',
            metavar='<project-domain>',
            help='References the domain name or ID which owns the project')
        parser.add_argument(
            '--description',
            metavar='<project-description>',
            help='New project description')
        # FIXME (stevemar): need to update enabled/disabled as per Dolph's
        # comments in 19999/4
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable project')
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable project')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.domain:
            domain = utils.find_resource(identity_client.domains,
                                         parsed_args.domain).id
        else:
            domain = None

        project = identity_client.projects.create(
            parsed_args.project_name,
            domain=domain,
            description=parsed_args.description,
            enabled=parsed_args.enabled)

        info = {}
        info.update(project._info)
        return zip(*sorted(info.iteritems()))


class DeleteProject(command.Command):
    """Delete project command"""

    log = logging.getLogger(__name__ + '.DeleteProject')

    def get_parser(self, prog_name):
        parser = super(DeleteProject, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help='Name or ID of project to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        project = utils.find_resource(identity_client.projects,
                                      parsed_args.project)
        identity_client.projects.delete(project.id)
        return


class ListProject(lister.Lister):
    """List project command"""

    log = logging.getLogger(__name__ + '.ListProject')

    def get_parser(self, prog_name):
        parser = super(ListProject, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        if parsed_args.long:
            columns = ('ID', 'Name', 'Domain ID', 'Description', 'Enabled')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.identity.projects.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetProject(command.Command):
    """Set project command"""

    log = logging.getLogger(__name__ + '.SetProject')

    def get_parser(self, prog_name):
        parser = super(SetProject, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help='Name or ID of project to change')
        parser.add_argument(
            '--name',
            metavar='<new-project-name>',
            help='New project name')
        parser.add_argument(
            '--domain',
            metavar='<project-domain>',
            help='New domain name or ID that will now own the project')
        parser.add_argument(
            '--description',
            metavar='<project-description>',
            help='New project description')
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable project (default)')
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable project')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        project = utils.find_resource(identity_client.projects,
                                      parsed_args.project)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.domain:
            domain = utils.find_resource(
                identity_client.domains, parsed_args.domain).id
            kwargs['domain'] = domain
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if 'enabled' in parsed_args:
            kwargs['enabled'] = parsed_args.enabled

        if kwargs == {}:
            sys.stdout.write("Project not updated, no arguments present")
            return
        project.update(**kwargs)
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
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        project = utils.find_resource(identity_client.projects,
                                      parsed_args.project)

        info = {}
        info.update(project._info)
        return zip(*sorted(info.iteritems()))
