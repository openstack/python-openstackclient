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

"""Account v1 action implementations"""

from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
import six

from openstackclient.i18n import _


class SetAccount(command.Command):
    _description = _("Set account properties")

    def get_parser(self, prog_name):
        parser = super(SetAccount, self).get_parser(prog_name)
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            required=True,
            action=parseractions.KeyValueAction,
            help=_("Set a property on this account "
                   "(repeat option to set multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        self.app.client_manager.object_store.account_set(
            properties=parsed_args.property,
        )


class ShowAccount(command.ShowOne):
    _description = _("Display account details")

    def take_action(self, parsed_args):
        data = self.app.client_manager.object_store.account_show()
        if 'properties' in data:
            data['properties'] = format_columns.DictColumn(
                data.pop('properties'))
        return zip(*sorted(six.iteritems(data)))


class UnsetAccount(command.Command):
    _description = _("Unset account properties")

    def get_parser(self, prog_name):
        parser = super(UnsetAccount, self).get_parser(prog_name)
        parser.add_argument(
            '--property',
            metavar='<key>',
            required=True,
            action='append',
            default=[],
            help=_('Property to remove from account '
                   '(repeat option to remove multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        self.app.client_manager.object_store.account_unset(
            properties=parsed_args.property,
        )
