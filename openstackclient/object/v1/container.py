#   Copyright 2013 Nebula Inc.
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

"""Container v1 action implementations"""

import logging

from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateContainer(command.Lister):
    _description = _("Create new container")

    def get_parser(self, prog_name):
        parser = super(CreateContainer, self).get_parser(prog_name)
        parser.add_argument(
            'containers',
            metavar='<container-name>',
            nargs="+",
            help=_('New container name(s)'),
        )
        return parser

    def take_action(self, parsed_args):

        results = []
        for container in parsed_args.containers:
            if len(container) > 256:
                LOG.warning(
                    _('Container name is %s characters long, the default limit'
                      ' is 256'), len(container))
            data = self.app.client_manager.object_store.container_create(
                container=container,
            )
            results.append(data)

        columns = ("account", "container", "x-trans-id")
        return (columns,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={},
                ) for s in results))


class DeleteContainer(command.Command):
    _description = _("Delete container")

    def get_parser(self, prog_name):
        parser = super(DeleteContainer, self).get_parser(prog_name)
        parser.add_argument(
            '--recursive', '-r',
            action='store_true',
            default=False,
            help=_('Recursively delete objects and container'),
        )
        parser.add_argument(
            'containers',
            metavar='<container>',
            nargs="+",
            help=_('Container(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):

        for container in parsed_args.containers:
            if parsed_args.recursive:
                objs = self.app.client_manager.object_store.object_list(
                    container=container)
                for obj in objs:
                    self.app.client_manager.object_store.object_delete(
                        container=container,
                        object=obj['name'],
                    )
            self.app.client_manager.object_store.container_delete(
                container=container,
            )


class ListContainer(command.Lister):
    _description = _("List containers")

    def get_parser(self, prog_name):
        parser = super(ListContainer, self).get_parser(prog_name)
        parser.add_argument(
            "--prefix",
            metavar="<prefix>",
            help=_("Filter list using <prefix>"),
        )
        parser.add_argument(
            "--marker",
            metavar="<marker>",
            help=_("Anchor for paging"),
        )
        parser.add_argument(
            "--end-marker",
            metavar="<end-marker>",
            help=_("End anchor for paging"),
        )
        parser.add_argument(
            "--limit",
            metavar="<num-containers>",
            type=int,
            help=_("Limit the number of containers returned"),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help=_('List all containers (default is 10000)'),
        )
        return parser

    def take_action(self, parsed_args):

        if parsed_args.long:
            columns = ('Name', 'Bytes', 'Count')
        else:
            columns = ('Name',)

        kwargs = {}
        if parsed_args.prefix:
            kwargs['prefix'] = parsed_args.prefix
        if parsed_args.marker:
            kwargs['marker'] = parsed_args.marker
        if parsed_args.end_marker:
            kwargs['end_marker'] = parsed_args.end_marker
        if parsed_args.limit:
            kwargs['limit'] = parsed_args.limit
        if parsed_args.all:
            kwargs['full_listing'] = True

        data = self.app.client_manager.object_store.container_list(
            **kwargs
        )

        return (columns,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SaveContainer(command.Command):
    _description = _("Save container contents locally")

    def get_parser(self, prog_name):
        parser = super(SaveContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help=_('Container to save'),
        )
        return parser

    def take_action(self, parsed_args):
        self.app.client_manager.object_store.container_save(
            container=parsed_args.container,
        )


class SetContainer(command.Command):
    _description = _("Set container properties")

    def get_parser(self, prog_name):
        parser = super(SetContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help=_('Container to modify'),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            required=True,
            action=parseractions.KeyValueAction,
            help=_("Set a property on this container "
                   "(repeat option to set multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        self.app.client_manager.object_store.container_set(
            parsed_args.container,
            properties=parsed_args.property,
        )


class ShowContainer(command.ShowOne):
    _description = _("Display container details")

    def get_parser(self, prog_name):
        parser = super(ShowContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help=_('Container to display'),
        )
        return parser

    def take_action(self, parsed_args):

        data = self.app.client_manager.object_store.container_show(
            container=parsed_args.container,
        )
        if 'properties' in data:
            data['properties'] = format_columns.DictColumn(data['properties'])

        return zip(*sorted(six.iteritems(data)))


class UnsetContainer(command.Command):
    _description = _("Unset container properties")

    def get_parser(self, prog_name):
        parser = super(UnsetContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help=_('Container to modify'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            required=True,
            action='append',
            default=[],
            help=_('Property to remove from container '
                   '(repeat option to remove multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        self.app.client_manager.object_store.container_unset(
            parsed_args.container,
            properties=parsed_args.property,
        )
