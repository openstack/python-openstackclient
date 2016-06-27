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

"""Host action implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class ListHost(command.Lister):
    """List hosts"""

    def get_parser(self, prog_name):
        parser = super(ListHost, self).get_parser(prog_name)
        parser.add_argument(
            "--zone",
            metavar="<zone>",
            help=_("Only return hosts in the availability zone")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        columns = (
            "Host Name",
            "Service",
            "Zone"
        )
        data = compute_client.hosts.list_all(parsed_args.zone)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class SetHost(command.Command):
    """Set host properties"""
    def get_parser(self, prog_name):
        parser = super(SetHost, self).get_parser(prog_name)
        parser.add_argument(
            "host",
            metavar="<host>",
            help=_("Host to modify (name only)")
        )
        status = parser.add_mutually_exclusive_group()
        status.add_argument(
            '--enable',
            action='store_true',
            help=_("Enable the host")
        )
        status.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable the host")
        )
        maintenance = parser.add_mutually_exclusive_group()
        maintenance.add_argument(
            '--enable-maintenance',
            action='store_true',
            help=_("Enable maintenance mode for the host")
        )
        maintenance.add_argument(
            '--disable-maintenance',
            action='store_true',
            help=_("Disable maintenance mode for the host")
        )
        return parser

    def take_action(self, parsed_args):
        kwargs = {}

        if parsed_args.enable:
            kwargs['status'] = 'enable'
        if parsed_args.disable:
            kwargs['status'] = 'disable'
        if parsed_args.enable_maintenance:
            kwargs['maintenance_mode'] = 'enable'
        if parsed_args.disable_maintenance:
            kwargs['maintenance_mode'] = 'disable'

        compute_client = self.app.client_manager.compute

        # More than one hosts will be returned by using find_resource()
        # so that the return value cannot be used in host update() method.
        # find_resource() is just used for checking existence of host and
        # keeping the exception message consistent with other commands.
        utils.find_resource(compute_client.hosts, parsed_args.host)

        compute_client.hosts.update(
            parsed_args.host,
            kwargs
        )


class ShowHost(command.Lister):
    """Display host details"""

    def get_parser(self, prog_name):
        parser = super(ShowHost, self).get_parser(prog_name)
        parser.add_argument(
            "host",
            metavar="<host>",
            help=_("Name of host")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        columns = (
            "Host",
            "Project",
            "CPU",
            "Memory MB",
            "Disk GB"
        )
        data = compute_client.hosts.get(parsed_args.host)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))
