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

"""Identity v3 Region action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _format_region(region):
    columns = ('id', 'description', 'parent_region_id')
    column_headers = ('region', 'description', 'parent_region')
    return (
        column_headers,
        utils.get_item_properties(region, columns),
    )


class CreateRegion(command.ShowOne):
    _description = _("Create new region")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        # NOTE(stevemar): The API supports an optional region ID, but that
        # seems like poor UX, we will only support user-defined IDs.
        parser.add_argument(
            'region',
            metavar='<region-id>',
            help=_('New region ID'),
        )
        parser.add_argument(
            '--parent-region',
            metavar='<region-id>',
            help=_('Parent region ID'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New region description'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        region = identity_client.create_region(
            id=parsed_args.region,
            parent_region_id=parsed_args.parent_region,
            description=parsed_args.description,
        )

        return _format_region(region)


class DeleteRegion(command.Command):
    _description = _("Delete region(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'region',
            metavar='<region-id>',
            nargs='+',
            help=_('Region ID(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        result = 0
        for i in parsed_args.region:
            try:
                identity_client.delete_region(i)
            except Exception as e:
                result += 1
                LOG.error(
                    _("Failed to delete region with ID '%(region)s': %(e)s"),
                    {'region': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.region)
            msg = _("%(result)s of %(total)s regions failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListRegion(command.Lister):
    _description = _("List regions")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--parent-region',
            metavar='<region-id>',
            help=_('Filter by parent region ID'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.parent_region:
            kwargs['parent_region_id'] = parsed_args.parent_region

        columns_headers = ('Region', 'Parent Region', 'Description')
        columns = ('ID', 'Parent Region Id', 'Description')

        data = identity_client.regions(**kwargs)
        return (
            columns_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class SetRegion(command.Command):
    _description = _("Set region properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'region',
            metavar='<region-id>',
            help=_('Region to modify'),
        )
        parser.add_argument(
            '--parent-region',
            metavar='<region-id>',
            help=_('New parent region ID'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New region description'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.parent_region:
            kwargs['parent_region_id'] = parsed_args.parent_region

        identity_client.update_region(parsed_args.region, **kwargs)


class ShowRegion(command.ShowOne):
    _description = _("Display region details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'region',
            metavar='<region-id>',
            help=_('Region to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        region = identity_client.get_region(parsed_args.region)

        return _format_region(region)
