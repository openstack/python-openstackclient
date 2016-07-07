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

from keystoneauth1 import exceptions as ks_exc
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _


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
        except ks_exc.Conflict:
            if parsed_args.or_show:
                project = utils.find_resource(
                    identity_client.tenants,
                    parsed_args.name,
                )
                LOG.info(_('Returning existing project %s'), project.name)
            else:
                raise

        # TODO(stevemar): Remove the line below when we support multitenancy
        project._info.pop('parent_id', None)
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
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        for project in parsed_args.projects:
            project_obj = utils.find_resource(
                identity_client.tenants,
                project,
            )
            identity_client.tenants.delete(project_obj.id)


class ListProject(command.Lister):
    """List projects"""

    def get_parser(self, prog_name):
        parser = super(ListProject, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

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

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

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


class ShowProject(command.ShowOne):
    """Display project details"""

    def get_parser(self, prog_name):
        parser = super(ShowProject, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Project to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        info = {}
        try:
            project = utils.find_resource(
                identity_client.tenants,
                parsed_args.project,
            )
            info.update(project._info)
        except ks_exc.Forbidden:
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
                raise

        # TODO(stevemar): Remove the line below when we support multitenancy
        info.pop('parent_id', None)

        # NOTE(stevemar): Property handling isn't really supported in Keystone
        # and needs a lot of extra handling. Let's reserve the properties that
        # the API has and handle the extra top level properties.
        reserved = ('name', 'id', 'enabled', 'description')
        properties = {}
        for k, v in info.items():
            if k not in reserved:
                # If a key is not in `reserved` it's a property, pop it
                info.pop(k)
                # If a property has been "unset" it's `None`, so don't show it
                if v is not None:
                    properties[k] = v

        info['properties'] = utils.format_dict(properties)
        return zip(*sorted(six.iteritems(info)))


class UnsetProject(command.Command):
    """Unset project properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetProject, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Project to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help=_('Unset a project property '
                   '(repeat option to unset multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        project = utils.find_resource(
            identity_client.tenants,
            parsed_args.project,
        )
        kwargs = project._info
        for key in parsed_args.property:
            if key in kwargs:
                kwargs[key] = None
        identity_client.tenants.update(project.id, **kwargs)
