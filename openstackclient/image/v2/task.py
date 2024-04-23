# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _

_formatters = {
    'tags': format_columns.ListColumn,
}


def _format_task(task):
    """Format an task to make it more consistent with OSC operations."""

    info = {}
    properties = {}

    # the only fields we're not including is "links", "tags" and the properties
    fields_to_show = [
        'created_at',
        'expires_at',
        'id',
        'input',
        'message',
        'owner_id',
        'result',
        'status',
        'type',
        'updated_at',
    ]

    # split out the usual key and the properties which are top-level
    for field in fields_to_show:
        info[field] = task.get(field)

    for key in task:
        if key in fields_to_show:
            continue

        if key in {'location', 'name', 'schema'}:
            continue

        properties[key] = task.get(key)

    # add properties back into the dictionary as a top-level key
    info['properties'] = format_columns.DictColumn(properties)

    return info


class ShowTask(command.ShowOne):
    _description = _('Display task details')

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            'task',
            metavar='<Task ID>',
            help=_('Task to display (ID)'),
        )

        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        task = image_client.get_task(parsed_args.task)
        info = _format_task(task)

        return zip(*sorted(info.items()))


class ListTask(command.Lister):
    _description = _('List tasks')

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--sort-key',
            metavar='<key>[:<field>]',
            help=_(
                'Sorts the response by one of the following attributes: '
                'created_at, expires_at, id, status, type, updated_at. '
                '(default is created_at) '
                '(multiple keys and directions can be specified separated '
                'by comma)'
            ),
        )
        parser.add_argument(
            '--sort-dir',
            metavar='<key>[:<direction>]',
            help=_(
                'Sort output by selected keys and directions (asc or desc) '
                '(default: name:desc) '
                '(multiple keys and directions can be specified separated '
                'by comma)'
            ),
        )
        parser.add_argument(
            '--limit',
            metavar='<num-tasks>',
            type=int,
            help=_('Maximum number of tasks to display.'),
        )
        parser.add_argument(
            '--marker',
            metavar='<task>',
            help=_(
                'The last task of the previous page. '
                'Display list of tasks after marker. '
                'Display all tasks if not specified. '
                '(name or ID)'
            ),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            choices=['import'],
            help=_('Filters the response by a task type.'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            choices=[
                'pending',
                'processing',
                'success',
                'failure',
            ],
            help=_('Filter tasks based on status.'),
        )

        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        columns = ('id', 'type', 'status', 'owner_id')
        column_headers = ('ID', 'Type', 'Status', 'Owner')

        kwargs = {}
        copy_attrs = {
            'sort_key',
            'sort_dir',
            'limit',
            'marker',
            'type',
            'status',
        }
        for attr in copy_attrs:
            val = getattr(parsed_args, attr, None)
            if val is not None:
                # Only include a value in kwargs for attributes that are
                # actually present on the command line
                kwargs[attr] = val

        data = image_client.tasks(**kwargs)

        return (
            column_headers,
            (
                utils.get_item_properties(s, columns, formatters=_formatters)
                for s in data
            ),
        )
