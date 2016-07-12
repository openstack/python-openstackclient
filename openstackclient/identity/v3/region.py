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
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateRegion(command.ShowOne):
    """Create new region"""

    def get_parser(self, prog_name):
        parser = super(CreateRegion, self).get_parser(prog_name)
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
        identity_client = self.app.client_manager.identity

        region = identity_client.regions.create(
            id=parsed_args.region,
            parent_region=parsed_args.parent_region,
            description=parsed_args.description,
        )

        region._info['region'] = region._info.pop('id')
        region._info['parent_region'] = region._info.pop('parent_region_id')
        region._info.pop('links', None)
        return zip(*sorted(six.iteritems(region._info)))


class DeleteRegion(command.Command):
    """Delete region(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteRegion, self).get_parser(prog_name)
        parser.add_argument(
            'region',
            metavar='<region-id>',
            nargs='+',
            help=_('Region ID(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.region:
            try:
                identity_client.regions.delete(i)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete region with "
                          "ID '%(region)s': %(e)s")
                          % {'region': i, 'e': e})

        if result > 0:
            total = len(parsed_args.region)
            msg = (_("%(result)s of %(total)s regions failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListRegion(command.Lister):
    """List regions"""

    def get_parser(self, prog_name):
        parser = super(ListRegion, self).get_parser(prog_name)
        parser.add_argument(
            '--parent-region',
            metavar='<region-id>',
            help=_('Filter by parent region ID'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        kwargs = {}
        if parsed_args.parent_region:
            kwargs['parent_region_id'] = parsed_args.parent_region

        columns_headers = ('Region', 'Parent Region', 'Description')
        columns = ('ID', 'Parent Region Id', 'Description')

        data = identity_client.regions.list(**kwargs)
        return (columns_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetRegion(command.Command):
    """Set region properties"""

    def get_parser(self, prog_name):
        parser = super(SetRegion, self).get_parser(prog_name)
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
        identity_client = self.app.client_manager.identity

        kwargs = {}
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.parent_region:
            kwargs['parent_region'] = parsed_args.parent_region

        identity_client.regions.update(parsed_args.region, **kwargs)


class ShowRegion(command.ShowOne):
    """Display region details"""

    def get_parser(self, prog_name):
        parser = super(ShowRegion, self).get_parser(prog_name)
        parser.add_argument(
            'region',
            metavar='<region-id>',
            help=_('Region to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        region = utils.find_resource(identity_client.regions,
                                     parsed_args.region)

        region._info['region'] = region._info.pop('id')
        region._info['parent_region'] = region._info.pop('parent_region_id')
        region._info.pop('links', None)
        return zip(*sorted(six.iteritems(region._info)))
