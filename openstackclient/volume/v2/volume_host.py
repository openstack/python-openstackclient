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

"""Volume v2 host action implementations"""

from osc_lib.command import command

from openstackclient.i18n import _


class FailoverVolumeHost(command.Command):
    _description = _("Failover volume host to different backend")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "host", metavar="<host-name>", help=_("Name of volume host")
        )
        parser.add_argument(
            "--volume-backend",
            metavar="<backend-id>",
            required=True,
            help=_(
                "The ID of the volume backend replication "
                "target where the host will failover to (required)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        service_client = self.app.client_manager.volume
        service_client.services.failover_host(
            parsed_args.host, parsed_args.volume_backend
        )


class SetVolumeHost(command.Command):
    _description = _("Set volume host properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "host", metavar="<host-name>", help=_("Name of volume host")
        )
        enabled_group = parser.add_mutually_exclusive_group()
        enabled_group.add_argument(
            "--disable",
            action="store_true",
            help=_("Freeze and disable the specified volume host"),
        )
        enabled_group.add_argument(
            "--enable",
            action="store_true",
            help=_("Thaw and enable the specified volume host"),
        )
        return parser

    def take_action(self, parsed_args):
        service_client = self.app.client_manager.volume
        if parsed_args.enable:
            service_client.services.thaw_host(parsed_args.host)
        if parsed_args.disable:
            service_client.services.freeze_host(parsed_args.host)
