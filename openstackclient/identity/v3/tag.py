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

import argparse

from openstackclient.i18n import _


class _CommaListAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.split(','))


def add_tag_filtering_option_to_parser(parser, collection_name):
    parser.add_argument(
        '--tags',
        metavar='<tag>[,<tag>,...]',
        action=_CommaListAction,
        help=_('List %s which have all given tag(s) '
               '(Comma-separated list of tags)') % collection_name
    )
    parser.add_argument(
        '--tags-any',
        metavar='<tag>[,<tag>,...]',
        action=_CommaListAction,
        help=_('List %s which have any given tag(s) '
               '(Comma-separated list of tags)') % collection_name
    )
    parser.add_argument(
        '--not-tags',
        metavar='<tag>[,<tag>,...]',
        action=_CommaListAction,
        help=_('Exclude %s which have all given tag(s) '
               '(Comma-separated list of tags)') % collection_name
    )
    parser.add_argument(
        '--not-tags-any',
        metavar='<tag>[,<tag>,...]',
        action=_CommaListAction,
        help=_('Exclude %s which have any given tag(s) '
               '(Comma-separated list of tags)') % collection_name
    )


def get_tag_filtering_args(parsed_args, args):
    if parsed_args.tags:
        args['tags'] = ','.join(parsed_args.tags)
    if parsed_args.tags_any:
        args['tags-any'] = ','.join(parsed_args.tags_any)
    if parsed_args.not_tags:
        args['not-tags'] = ','.join(parsed_args.not_tags)
    if parsed_args.not_tags_any:
        args['not-tags-any'] = ','.join(parsed_args.not_tags_any)


def add_tag_option_to_parser_for_create(parser, resource_name):
    tag_group = parser.add_mutually_exclusive_group()
    tag_group.add_argument(
        '--tag',
        action='append',
        dest='tags',
        metavar='<tag>',
        default=[],
        help=_('Tag to be added to the %s '
               '(repeat option to set multiple tags)') % resource_name
    )


def add_tag_option_to_parser_for_set(parser, resource_name):
    parser.add_argument(
        '--tag',
        action='append',
        dest='tags',
        metavar='<tag>',
        default=[],
        help=_('Tag to be added to the %s '
               '(repeat option to set multiple tags)') % resource_name
    )
    parser.add_argument(
        '--clear-tags',
        action='store_true',
        help=_('Clear tags associated with the %s. Specify '
               'both --tag and --clear-tags to overwrite '
               'current tags') % resource_name
    )
    parser.add_argument(
        '--remove-tag',
        metavar='<tag>',
        default=[],
        help=_('Tag to be deleted from the %s '
               '(repeat option to delete multiple tags)') % resource_name
    )


def update_tags_in_args(parsed_args, obj, args):
    if parsed_args.clear_tags:
        args['tags'] = []
        obj.tags = []
    if parsed_args.remove_tag:
        if parsed_args.remove_tag in obj.tags:
            obj.tags.remove(parsed_args.remove_tag)
        args['tags'] = list(set(obj.tags))
        return
    if parsed_args.tags:
        args['tags'] = list(set(obj.tags).union(
            set(parsed_args.tags)))
