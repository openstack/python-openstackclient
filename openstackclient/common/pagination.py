# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from osc_lib.cli import parseractions

from openstackclient.i18n import _


# TODO(stephenfin): Consider moving these to osc-lib since they're broadly
# useful


def add_marker_pagination_option_to_parser(parser):
    """Add marker-based pagination options to the parser.

    APIs that use marker-based paging use the marker and limit query parameters
    to paginate through items in a collection.

    Marker-based pagination is often used in cases where the length of the
    total set of items is either changing frequently, or where the total length
    might not be known upfront.
    """
    parser.add_argument(
        '--limit',
        metavar='<limit>',
        type=int,
        action=parseractions.NonNegativeAction,
        help=_(
            'The maximum number of entries to return. If the value exceeds '
            'the server-defined maximum, then the maximum value will be used.'
        ),
    )
    parser.add_argument(
        '--marker',
        metavar='<marker>',
        default=None,
        help=_(
            'The first position in the collection to return results from. '
            'This should be a value that was returned in a previous request.'
        ),
    )


def add_offset_pagination_option_to_parser(parser):
    """Add offset-based pagination options to the parser.

    APIs that use offset-based paging use the offset and limit query parameters
    to paginate through items in a collection.

    Offset-based pagination is often used where the list of items is of a fixed
    and predetermined length.
    """
    parser.add_argument(
        '--limit',
        metavar='<limit>',
        type=int,
        action=parseractions.NonNegativeAction,
        help=_(
            'The maximum number of entries to return. If the value exceeds '
            'the server-defined maximum, then the maximum value will be used.'
        ),
    )
    parser.add_argument(
        '--offset',
        metavar='<offset>',
        type=int,
        action=parseractions.NonNegativeAction,
        default=None,
        help=_(
            'The (zero-based) offset of the first item in the collection to '
            'return.'
        ),
    )
