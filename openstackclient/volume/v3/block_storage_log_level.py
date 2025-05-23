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

"""Block Storage Service action implementations"""

from openstack import utils as sdk_utils
from osc_lib.command import command
from osc_lib import exceptions

from openstackclient.i18n import _


class BlockStorageLogLevelList(command.Lister):
    """List log levels of block storage service.

    Supported by --os-volume-api-version 3.32 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--host",
            metavar="<host>",
            default=None,
            help=_(
                "List block storage service log level of specified host "
                "(name only)"
            ),
        )
        parser.add_argument(
            "--service",
            metavar="<service>",
            default=None,
            choices=(
                None,
                '*',
                'cinder-api',
                'cinder-volume',
                'cinder-scheduler',
                'cinder-backup',
            ),
            help=_(
                "List block storage service log level of the specified "
                "service (name only)"
            ),
        )
        parser.add_argument(
            "--log-prefix",
            metavar="<log-prefix>",
            default=None,
            help="Prefix for the log, e.g. 'sqlalchemy'",
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume
        columns = [
            "Binary",
            "Host",
            "Prefix",
            "Level",
        ]

        if not sdk_utils.supports_microversion(volume_client, '3.32'):
            msg = _(
                "--os-volume-api-version 3.32 or greater is required to "
                "support the 'block storage log level list' command"
            )
            raise exceptions.CommandError(msg)

        data = []
        for entry in volume_client.get_service_log_levels(
            binary=parsed_args.service,
            server=parsed_args.host,
            prefix=parsed_args.log_prefix,
        ):
            entry_levels = sorted(entry.levels.items(), key=lambda x: x[0])
            for prefix, level in entry_levels:
                data.append((entry.binary, entry.host, prefix, level))

        return (columns, data)


class BlockStorageLogLevelSet(command.Command):
    """Set log level of block storage service

    Supported by --os-volume-api-version 3.32 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "level",
            metavar="<log-level>",
            choices=('INFO', 'WARNING', 'ERROR', 'DEBUG'),
            type=str.upper,
            help=_("Desired log level"),
        )
        parser.add_argument(
            "--host",
            metavar="<host>",
            default=None,
            help=_(
                "Set block storage service log level of specified host "
                "(name only)"
            ),
        )
        parser.add_argument(
            "--service",
            metavar="<service>",
            default=None,
            choices=(
                None,
                '*',
                'cinder-api',
                'cinder-volume',
                'cinder-scheduler',
                'cinder-backup',
            ),
            help=_(
                "Set block storage service log level of specified service "
                "(name only)"
            ),
        )
        parser.add_argument(
            "--log-prefix",
            metavar="<log-prefix>",
            default=None,
            help="Prefix for the log, e.g. 'sqlalchemy'",
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.32'):
            msg = _(
                "--os-volume-api-version 3.32 or greater is required to "
                "support the 'block storage log level set' command"
            )
            raise exceptions.CommandError(msg)

        volume_client.set_service_log_levels(
            level=parsed_args.level,
            binary=parsed_args.service,
            server=parsed_args.host,
            prefix=parsed_args.log_prefix,
        )
