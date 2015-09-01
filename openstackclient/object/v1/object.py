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

"""Object v1 action implementations"""


import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateObject(lister.Lister):
    """Upload object to container"""

    log = logging.getLogger(__name__ + '.CreateObject')

    def get_parser(self, prog_name):
        parser = super(CreateObject, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help='Container for new object',
        )
        parser.add_argument(
            'objects',
            metavar='<filename>',
            nargs="+",
            help='Local filename(s) to upload',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        results = []
        for obj in parsed_args.objects:
            data = self.app.client_manager.object_store.object_create(
                container=parsed_args.container,
                object=obj,
            )
            results.append(data)

        columns = ("object", "container", "etag")
        return (columns,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={},
                ) for s in results))


class DeleteObject(command.Command):
    """Delete object from container"""

    log = logging.getLogger(__name__ + '.DeleteObject')

    def get_parser(self, prog_name):
        parser = super(DeleteObject, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help='Delete object(s) from <container>',
        )
        parser.add_argument(
            'objects',
            metavar='<object>',
            nargs="+",
            help='Object(s) to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        for obj in parsed_args.objects:
            self.app.client_manager.object_store.object_delete(
                container=parsed_args.container,
                object=obj,
            )


class ListObject(lister.Lister):
    """List objects"""

    log = logging.getLogger(__name__ + '.ListObject')

    def get_parser(self, prog_name):
        parser = super(ListObject, self).get_parser(prog_name)
        parser.add_argument(
            "container",
            metavar="<container>",
            help="Container to list",
        )
        parser.add_argument(
            "--prefix",
            metavar="<prefix>",
            help="Filter list using <prefix>",
        )
        parser.add_argument(
            "--delimiter",
            metavar="<delimiter>",
            help="Roll up items with <delimiter>",
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
            help="Limit the number of objects returned",
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
            help='List all objects in container (default is 10000)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        if parsed_args.long:
            columns = (
                'Name',
                'Bytes',
                'Hash',
                'Content Type',
                'Last Modified',
            )
        else:
            columns = ('Name',)

        kwargs = {}
        if parsed_args.prefix:
            kwargs['prefix'] = parsed_args.prefix
        if parsed_args.delimiter:
            kwargs['delimiter'] = parsed_args.delimiter
        if parsed_args.marker:
            kwargs['marker'] = parsed_args.marker
        if parsed_args.end_marker:
            kwargs['end_marker'] = parsed_args.end_marker
        if parsed_args.limit:
            kwargs['limit'] = parsed_args.limit
        if parsed_args.all:
            kwargs['full_listing'] = True

        data = self.app.client_manager.object_store.object_list(
            container=parsed_args.container,
            **kwargs
        )

        return (columns,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SaveObject(command.Command):
    """Save object locally"""

    log = logging.getLogger(__name__ + ".SaveObject")

    def get_parser(self, prog_name):
        parser = super(SaveObject, self).get_parser(prog_name)
        parser.add_argument(
            "--file",
            metavar="<filename>",
            help="Destination filename (defaults to object name)",
        )
        parser.add_argument(
            'container',
            metavar='<container>',
            help='Download <object> from <container>',
        )
        parser.add_argument(
            "object",
            metavar="<object>",
            help="Object to save",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        self.app.client_manager.object_store.object_save(
            container=parsed_args.container,
            object=parsed_args.object,
            file=parsed_args.file,
        )


class ShowObject(show.ShowOne):
    """Display object details"""

    log = logging.getLogger(__name__ + '.ShowObject')

    def get_parser(self, prog_name):
        parser = super(ShowObject, self).get_parser(prog_name)
        parser.add_argument(
            'container',
            metavar='<container>',
            help='Display <object> from <container>',
        )
        parser.add_argument(
            'object',
            metavar='<object>',
            help='Object to display',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        data = self.app.client_manager.object_store.object_show(
            container=parsed_args.container,
            object=parsed_args.object,
        )

        return zip(*sorted(six.iteritems(data)))
