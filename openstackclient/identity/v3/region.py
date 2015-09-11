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
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils
from openstackclient.i18n import _  # noqa


class CreateRegion(show.ShowOne):
    """Create new region"""

    log = logging.getLogger(__name__ + '.CreateRegion')

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
        parser.add_argument(
            '--url',
            metavar='<url>',
            help=_('New region url'),
        )

        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        region = identity_client.regions.create(
            id=parsed_args.region,
            url=parsed_args.url,
            parent_region=parsed_args.parent_region,
            description=parsed_args.description,
        )

        region._info['region'] = region._info.pop('id')
        region._info['parent_region'] = region._info.pop('parent_region_id')
        region._info.pop('links', None)
        return zip(*sorted(six.iteritems(region._info)))


class DeleteRegion(command.Command):
    """Delete region"""

    log = logging.getLogger(__name__ + '.DeleteRegion')

    def get_parser(self, prog_name):
        parser = super(DeleteRegion, self).get_parser(prog_name)
        parser.add_argument(
            'region',
            metavar='<region-id>',
            help=_('Region ID to delete'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        identity_client.regions.delete(parsed_args.region)
        return


class ListRegion(lister.Lister):
    """List regions"""

    log = logging.getLogger(__name__ + '.ListRegion')

    def get_parser(self, prog_name):
        parser = super(ListRegion, self).get_parser(prog_name)
        parser.add_argument(
            '--parent-region',
            metavar='<region-id>',
            help=_('Filter by parent region ID'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        kwargs = {}
        if parsed_args.parent_region:
            kwargs['parent_region_id'] = parsed_args.parent_region

        columns_headers = ('Region', 'Parent Region', 'Description', 'URL')
        columns = ('ID', 'Parent Region Id', 'Description', 'URL')

        data = identity_client.regions.list(**kwargs)
        return (columns_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetRegion(command.Command):
    """Set region properties"""

    log = logging.getLogger(__name__ + '.SetRegion')

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
        parser.add_argument(
            '--url',
            metavar='<url>',
            help=_('New region url'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if (not parsed_args.url
                and not parsed_args.parent_region
                and not parsed_args.description):
            return

        kwargs = {}
        if parsed_args.url:
            kwargs['url'] = parsed_args.url
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.parent_region:
            kwargs['parent_region'] = parsed_args.parent_region

        identity_client.regions.update(parsed_args.region, **kwargs)
        return


class ShowRegion(show.ShowOne):
    """Display region details"""

    log = logging.getLogger(__name__ + '.ShowRegion')

    def get_parser(self, prog_name):
        parser = super(ShowRegion, self).get_parser(prog_name)
        parser.add_argument(
            'region',
            metavar='<region-id>',
            help=_('Region to display'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        region = utils.find_resource(identity_client.regions,
                                     parsed_args.region)

        region._info['region'] = region._info.pop('id')
        region._info['parent_region'] = region._info.pop('parent_region_id')
        region._info.pop('links', None)
        return zip(*sorted(six.iteritems(region._info)))
