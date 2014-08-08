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
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils
from openstackclient.object.v1.lib import container as lib_container


class CreateContainer(show.ShowOne):
    """Create a container"""

    log = logging.getLogger(__name__ + '.CreateContainer')

    def get_parser(self, prog_name):
        parser = super(CreateContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help='New container name',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        data = lib_container.create_container(
            self.app.client_manager.session,
            self.app.client_manager.object_store.endpoint,
            parsed_args.container,
        )

        return zip(*sorted(six.iteritems(data)))


class DeleteContainer(command.Command):
    """Delete a container"""

    log = logging.getLogger(__name__ + '.DeleteContainer')

    def get_parser(self, prog_name):
        parser = super(DeleteContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help='Container name to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        lib_container.delete_container(
            self.app.client_manager.session,
            self.app.client_manager.object_store.endpoint,
            parsed_args.container,
        )


class ListContainer(lister.Lister):
    """List containers"""

    log = logging.getLogger(__name__ + '.ListContainer')

    def get_parser(self, prog_name):
        parser = super(ListContainer, self).get_parser(prog_name)
        parser.add_argument(
            "--prefix",
            metavar="<prefix>",
            help="Filter list using <prefix>",
        )
        parser.add_argument(
            "--marker",
            metavar="<marker>",
            help="Anchor for paging",
        )
        parser.add_argument(
            "--end-marker",
            metavar="<end-marker>",
            help="End anchor for paging",
        )
        parser.add_argument(
            "--limit",
            metavar="<limit>",
            type=int,
            help="Limit the number of containers returned",
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='List all containers (default is 10000)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

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

        data = lib_container.list_containers(
            self.app.client_manager.session,
            self.app.client_manager.object_store.endpoint,
            **kwargs
        )

        return (columns,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ShowContainer(show.ShowOne):
    """Show container information"""

    log = logging.getLogger(__name__ + '.ShowContainer')

    def get_parser(self, prog_name):
        parser = super(ShowContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help='Container name to display',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        data = lib_container.show_container(
            self.app.client_manager.session,
            self.app.client_manager.object_store.endpoint,
            parsed_args.container,
        )

        return zip(*sorted(six.iteritems(data)))
