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

"""Identity v2 Project action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show
from keystoneclient import exceptions as ksc_exc

from openstackclient.common import parseractions
from openstackclient.common import utils
from openstackclient.i18n import _  # noqa


class CreateProject(show.ShowOne):
    """Create new project"""

    log = logging.getLogger(__name__ + '.CreateProject')

    def get_parser(self, prog_name):
        parser = super(CreateProject, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<project-name>',
            help=_('New project name'),
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
            help=_('Enable project (default)'),
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

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        enabled = True
        if parsed_args.disable:
            enabled = False
        kwargs = {}
        if parsed_args.property:
            kwargs = parsed_args.property.copy()

        try:
            project = identity_client.tenants.create(
                parsed_args.name,
                description=parsed_args.description,
                enabled=enabled,
                **kwargs
            )
        except ksc_exc.Conflict as e:
            if parsed_args.or_show:
                project = utils.find_resource(
                    identity_client.tenants,
                    parsed_args.name,
                )
                self.log.info('Returning existing project %s', project.name)
            else:
                raise e

        # TODO(stevemar): Remove the line below when we support multitenancy
        project._info.pop('parent_id', None)
        return zip(*sorted(six.iteritems(project._info)))


class DeleteProject(command.Command):
    """Delete project(s)"""

    log = logging.getLogger(__name__ + '.DeleteProject')

    def get_parser(self, prog_name):
        parser = super(DeleteProject, self).get_parser(prog_name)
        parser.add_argument(
            'projects',
            metavar='<project>',
            nargs="+",
            help=_('Project(s) to delete (name or ID)'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        for project in parsed_args.projects:
            project_obj = utils.find_resource(
                identity_client.tenants,
                project,
            )
            identity_client.tenants.delete(project_obj.id)
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
            help=_('List additional fields in output'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        if parsed_args.long:
            columns = ('ID', 'Name', 'Description', 'Enabled')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.identity.tenants.list()
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
            help=_('Project to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set project name'),
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
            help=_('Set a project property '
                   '(repeat option to set multiple properties)'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if (not parsed_args.name
                and not parsed_args.description
                and not parsed_args.enable
                and not parsed_args.property
                and not parsed_args.disable):
            return

        project = utils.find_resource(
            identity_client.tenants,
            parsed_args.project,
        )

        kwargs = project._info
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
        if 'id' in kwargs:
            del kwargs['id']
        if 'name' in kwargs:
            # Hack around broken Identity API arg names
            kwargs['tenant_name'] = kwargs['name']
            del kwargs['name']

        identity_client.tenants.update(project.id, **kwargs)
        return


class ShowProject(show.ShowOne):
    """Display project details"""

    log = logging.getLogger(__name__ + '.ShowProject')

    def get_parser(self, prog_name):
        parser = super(ShowProject, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Project to display (name or ID)'))
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        info = {}
        try:
            project = utils.find_resource(
                identity_client.tenants,
                parsed_args.project,
            )
            info.update(project._info)
        except ksc_exc.Forbidden as e:
            auth_ref = self.app.client_manager.auth_ref
            if (
                parsed_args.project == auth_ref.project_id or
                parsed_args.project == auth_ref.project_name
            ):
                # Ask for currently auth'ed project so return it
                info = {
                    'id': auth_ref.project_id,
                    'name': auth_ref.project_name,
                    # True because we don't get this far if it is disabled
                    'enabled': True,
                }
            else:
                raise e

        # TODO(stevemar): Remove the line below when we support multitenancy
        info.pop('parent_id', None)
        return zip(*sorted(six.iteritems(info)))
