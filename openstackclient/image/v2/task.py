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

from openstackclient.i18n import _


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
        parser = super(ShowTask, self).get_parser(prog_name)

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
