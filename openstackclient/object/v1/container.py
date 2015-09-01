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


class CreateContainer(lister.Lister):
    """Create new container"""

    log = logging.getLogger(__name__ + '.CreateContainer')

    def get_parser(self, prog_name):
        parser = super(CreateContainer, self).get_parser(prog_name)
        parser.add_argument(
            'containers',
            metavar='<container-name>',
            nargs="+",
            help='New container name(s)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        results = []
        for container in parsed_args.containers:
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
    """Delete container"""

    log = logging.getLogger(__name__ + '.DeleteContainer')

    def get_parser(self, prog_name):
        parser = super(DeleteContainer, self).get_parser(prog_name)
        parser.add_argument(
            'containers',
            metavar='<container>',
            nargs="+",
            help='Container(s) to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        for container in parsed_args.containers:
            self.app.client_manager.object_store.container_delete(
                container=container,
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

    @utils.log_method(log)
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
    """Save container contents locally"""

    log = logging.getLogger(__name__ + ".SaveContainer")

    def get_parser(self, prog_name):
        parser = super(SaveContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help='Container to save',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        self.app.client_manager.object_store.container_save(
            container=parsed_args.container,
        )


class ShowContainer(show.ShowOne):
    """Display container details"""

    log = logging.getLogger(__name__ + '.ShowContainer')

    def get_parser(self, prog_name):
        parser = super(ShowContainer, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help='Container to display',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        data = self.app.client_manager.object_store.container_show(
            container=parsed_args.container,
        )

        return zip(*sorted(six.iteritems(data)))
