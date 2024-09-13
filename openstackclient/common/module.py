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

"""Module action implementation"""

import sys

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class ListCommand(command.Lister):
    _description = _("List recognized commands by group")

    auth_required = False

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--group',
            metavar='<group-keyword>',
            help=_(
                'Show commands filtered by a command group, for example: '
                'identity, volume, compute, image, network and '
                'other keywords'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        cm = self.app.command_manager
        groups = cm.get_command_groups()
        groups = sorted(groups)
        columns = ('Command Group', 'Commands')

        if parsed_args.group:
            groups = (group for group in groups if parsed_args.group in group)

        commands = []
        for group in groups:
            command_names = cm.get_command_names(group)
            command_names = sorted(command_names)

            if command_names != []:
                # TODO(bapalm): Fix this when cliff properly supports
                # handling the detection rather than using the hard-code below.
                if parsed_args.formatter == 'table':
                    command_names = utils.format_list(command_names, "\n")

                commands.append((group, command_names))

        return (columns, commands)


class ListModule(command.ShowOne):
    _description = _("List module versions")

    auth_required = False

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help=_('Show all modules that have version information'),
        )
        return parser

    def take_action(self, parsed_args):
        data = {}
        # Get module versions
        mods = sys.modules
        for k in mods.keys():
            k = k.split('.')[0]
            # Skip private modules and the modules that had been added,
            # like: keystoneclient, keystoneclient.exceptions and
            # keystoneclient.auth
            if not k.startswith('_') and k not in data:
                # TODO(dtroyer): Need a better way to decide which modules to
                #                show for the default (not --all) invocation.
                #                It should be just the things we actually care
                #                about like client and plugin modules...
                if (
                    parsed_args.all
                    or
                    # Handle xxxclient and openstacksdk
                    (k.endswith('client') or k == 'openstack')
                ):
                    try:
                        # NOTE(RuiChen): openstacksdk bug/1588823 exist,
                        #                no good way to add __version__ for
                        #                openstack module properly, hard code
                        #                looks bad, but openstacksdk module
                        #                information is important.
                        if k == 'openstack':
                            data[k] = mods[k].version.__version__
                        else:
                            data[k] = mods[k].__version__
                    except Exception:  # noqa: S110
                        # Catch all exceptions, just skip it
                        pass

        return zip(*sorted(data.items()))
