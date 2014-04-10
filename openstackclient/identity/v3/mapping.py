#   Copyright 2014 CERN
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

"""Identity v3 federation mapping action implementations"""

import json
import logging

from cliff import command
from cliff import lister
from cliff import show
import six

from openstackclient.common import exceptions
from openstackclient.common import utils


class _RulesReader(object):
    """Helper class capable of reading rules from files"""

    def _read_rules(self, path):
        """Read and parse rules from path

        Expect the file to contain a valid JSON structure.

        :param path: path to the file
        :return: loaded and valid dictionary with rules
        :raises exception.CommandError: In case the file cannot be
            accessed or the content is not a valid JSON.

        Example of the content of the file:
            [
                {
                    "local": [
                        {
                            "group": {
                                "id": "85a868"
                            }
                        }
                    ],
                    "remote": [
                        {
                            "type": "orgPersonType",
                            "any_one_of": [
                                "Employee"
                            ]
                        },
                        {
                            "type": "sn",
                            "any_one_of": [
                                "Young"
                            ]
                        }
                    ]
                }
            ]

        """
        blob = utils.read_blob_file_contents(path)
        try:
            rules = json.loads(blob)
        except ValueError as e:
            raise exceptions.CommandError(
                'An error occurred when reading '
                'rules from file %s: %s' % (path, e))
        else:
            return rules


class CreateMapping(show.ShowOne, _RulesReader):
    """Create new federation mapping"""

    log = logging.getLogger(__name__ + '.CreateMapping')

    def get_parser(self, prog_name):
        parser = super(CreateMapping, self).get_parser(prog_name)
        parser.add_argument(
            'mapping',
            metavar='<name>',
            help='New mapping (must be unique)',
        )
        parser.add_argument(
            '--rules',
            metavar='<rules>', required=True,
            help='Filename with rules',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        rules = self._read_rules(parsed_args.rules)
        mapping = identity_client.federation.mappings.create(
            mapping_id=parsed_args.mapping,
            rules=rules)

        info = {}
        info.update(mapping._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteMapping(command.Command):
    """Delete federation mapping"""

    log = logging.getLogger(__name__ + '.DeleteMapping')

    def get_parser(self, prog_name):
        parser = super(DeleteMapping, self).get_parser(prog_name)
        parser.add_argument(
            'mapping',
            metavar='<name>',
            help='Mapping to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        identity_client.federation.mappings.delete(parsed_args.mapping)
        return


class ListMapping(lister.Lister):
    """List federation mappings"""
    log = logging.getLogger(__name__ + '.ListMapping')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        # NOTE(marek-denis): Since rules can be long and tedious I have decided
        # to only list ids of the mappings. If somebody wants to check the
        # rules, (s)he should show specific ones.
        identity_client = self.app.client_manager.identity
        data = identity_client.federation.mappings.list()
        columns = ('ID',)
        items = [utils.get_item_properties(s, columns) for s in data]
        return (columns, items)


class SetMapping(show.ShowOne, _RulesReader):
    """Update federation mapping"""

    log = logging.getLogger(__name__ + '.SetMapping')

    def get_parser(self, prog_name):
        parser = super(SetMapping, self).get_parser(prog_name)
        parser.add_argument(
            'mapping',
            metavar='<name>',
            help='Mapping to update.',
        )
        parser.add_argument(
            '--rules',
            metavar='<rules>', required=True,
            help='Filename with rules',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        rules = self._read_rules(parsed_args.rules)

        mapping = identity_client.federation.mappings.update(
            mapping=parsed_args.mapping,
            rules=rules)

        info = {}
        info.update(mapping._info)
        return zip(*sorted(six.iteritems(info)))


class ShowMapping(show.ShowOne):
    """Show federation mapping details"""

    log = logging.getLogger(__name__ + '.ShowMapping')

    def get_parser(self, prog_name):
        parser = super(ShowMapping, self).get_parser(prog_name)
        parser.add_argument(
            'mapping',
            metavar='<name>',
            help='Mapping to show',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        mapping = identity_client.federation.mappings.get(parsed_args.mapping)

        info = {}
        info.update(mapping._info)
        return zip(*sorted(six.iteritems(info)))
