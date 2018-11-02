# Copyright 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Versions Action Implementation"""

from osc_lib.command import command

from openstackclient.i18n import _


class ShowVersions(command.Lister):
    _description = _("Show available versions of services")

    def get_parser(self, prog_name):
        parser = super(ShowVersions, self).get_parser(prog_name)
        interface_group = parser.add_mutually_exclusive_group()
        interface_group.add_argument(
            "--all-interfaces",
            dest="is_all_interfaces",
            action="store_true",
            default=False,
            help=_("Show values for all interfaces"),
        )
        interface_group.add_argument(
            '--interface',
            default='public',
            metavar='<interface>',
            help=_('Show versions for a specific interface.'),
        )
        parser.add_argument(
            '--region-name',
            metavar='<region_name>',
            help=_('Show versions for a specific region.'),
        )
        parser.add_argument(
            '--service',
            metavar='<region_name>',
            help=_('Show versions for a specific service.'),
        )
        parser.add_argument(
            '--status',
            metavar='<region_name>',
            help=_('Show versions for a specific status.'
                   ' [Valid values are SUPPORTED, CURRENT,'
                   ' DEPRECATED, EXPERIMENTAL]'),
        )
        return parser

    def take_action(self, parsed_args):

        interface = parsed_args.interface
        if parsed_args.is_all_interfaces:
            interface = None

        session = self.app.client_manager.session
        version_data = session.get_all_version_data(
            interface=interface,
            region_name=parsed_args.region_name,
            service_type=parsed_args.service)

        columns = [
            "Region Name",
            "Service Type",
            "Version",
            "Status",
            "Endpoint",
            "Min Microversion",
            "Max Microversion",
        ]

        status = parsed_args.status
        if status:
            status = status.upper()

        versions = []
        for region_name, interfaces in version_data.items():
            for interface, services in interfaces.items():
                for service_type, service_versions in services.items():
                    for data in service_versions:
                        if status and status != data['status']:
                            continue
                        versions.append((
                            region_name,
                            service_type,
                            data['version'],
                            data['status'],
                            data['url'],
                            data['min_microversion'],
                            data['max_microversion'],
                        ))
        return (columns, versions)
