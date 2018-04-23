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

"""Limits Action Implementation"""

import itertools

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


class ShowLimits(command.Lister):
    _description = _("Show compute and block storage limits")

    def get_parser(self, prog_name):
        parser = super(ShowLimits, self).get_parser(prog_name)
        type_group = parser.add_mutually_exclusive_group(required=True)
        type_group.add_argument(
            "--absolute",
            dest="is_absolute",
            action="store_true",
            default=False,
            help=_("Show absolute limits"),
        )
        type_group.add_argument(
            "--rate",
            dest="is_rate",
            action="store_true",
            default=False,
            help=_("Show rate limits"),
        )
        parser.add_argument(
            "--reserved",
            dest="is_reserved",
            action="store_true",
            default=False,
            help=_("Include reservations count [only valid with --absolute]"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Show limits for a specific project (name or ID)'
                   ' [only valid with --absolute]'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the project belongs to (name or ID)'
                   ' [only valid with --absolute]'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume

        project_id = None
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            if parsed_args.domain is not None:
                domain = identity_common.find_domain(identity_client,
                                                     parsed_args.domain)
                project_id = utils.find_resource(identity_client.projects,
                                                 parsed_args.project,
                                                 domain_id=domain.id).id
            else:
                project_id = utils.find_resource(identity_client.projects,
                                                 parsed_args.project).id

        compute_limits = None
        volume_limits = None

        if self.app.client_manager.is_compute_endpoint_enabled():
            compute_limits = compute_client.limits.get(parsed_args.is_reserved,
                                                       tenant_id=project_id)

        if self.app.client_manager.is_volume_endpoint_enabled(volume_client):
            volume_limits = volume_client.limits.get()

        data = []
        if parsed_args.is_absolute:
            if compute_limits:
                data.append(compute_limits.absolute)
            if volume_limits:
                data.append(volume_limits.absolute)
            columns = ["Name", "Value"]
            return (columns, (utils.get_item_properties(s, columns)
                              for s in itertools.chain(*data)))

        elif parsed_args.is_rate:
            if compute_limits:
                data.append(compute_limits.rate)
            if volume_limits:
                data.append(volume_limits.rate)
            columns = ["Verb", "URI", "Value", "Remain", "Unit",
                       "Next Available"]
            return (columns, (utils.get_item_properties(s, columns)
                              for s in itertools.chain(*data)))
        else:
            return {}, {}
