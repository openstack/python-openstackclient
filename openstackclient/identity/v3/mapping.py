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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


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
            msg = _("An error occurred when reading rules from file "
                    "%(path)s: %(error)s") % {"path": path, "error": e}
            raise exceptions.CommandError(msg)
        else:
            return rules


class CreateMapping(command.ShowOne, _RulesReader):
    """Create new mapping"""

    def get_parser(self, prog_name):
        parser = super(CreateMapping, self).get_parser(prog_name)
        parser.add_argument(
            'mapping',
            metavar='<name>',
            help=_('New mapping name (must be unique)'),
        )
        parser.add_argument(
            '--rules',
            metavar='<filename>', required=True,
            help=_('Filename that contains a set of mapping rules (required)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        rules = self._read_rules(parsed_args.rules)
        mapping = identity_client.federation.mappings.create(
            mapping_id=parsed_args.mapping,
            rules=rules)

        mapping._info.pop('links', None)
        return zip(*sorted(six.iteritems(mapping._info)))


class DeleteMapping(command.Command):
    """Delete mapping(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteMapping, self).get_parser(prog_name)
        parser.add_argument(
            'mapping',
            metavar='<mapping>',
            nargs='+',
            help=_('Mapping(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.mapping:
            try:
                identity_client.federation.mappings.delete(i)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete mapping with name or "
                          "ID '%(mapping)s': %(e)s")
                          % {'mapping': i, 'e': e})

        if result > 0:
            total = len(parsed_args.mapping)
            msg = (_("%(result)s of %(total)s mappings failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListMapping(command.Lister):
    """List mappings"""

    def take_action(self, parsed_args):
        # NOTE(marek-denis): Since rules can be long and tedious I have decided
        # to only list ids of the mappings. If somebody wants to check the
        # rules, (s)he should show specific ones.
        identity_client = self.app.client_manager.identity
        data = identity_client.federation.mappings.list()
        columns = ('ID',)
        items = [utils.get_item_properties(s, columns) for s in data]
        return (columns, items)


class SetMapping(command.Command, _RulesReader):
    """Set mapping properties"""

    def get_parser(self, prog_name):
        parser = super(SetMapping, self).get_parser(prog_name)
        parser.add_argument(
            'mapping',
            metavar='<name>',
            help=_('Mapping to modify'),
        )
        parser.add_argument(
            '--rules',
            metavar='<filename>',
            help=_('Filename that contains a new set of mapping rules'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        rules = self._read_rules(parsed_args.rules)

        mapping = identity_client.federation.mappings.update(
            mapping=parsed_args.mapping,
            rules=rules)

        mapping._info.pop('links', None)
        return zip(*sorted(six.iteritems(mapping._info)))


class ShowMapping(command.ShowOne):
    """Display mapping details"""

    def get_parser(self, prog_name):
        parser = super(ShowMapping, self).get_parser(prog_name)
        parser.add_argument(
            'mapping',
            metavar='<mapping>',
            help=_('Mapping to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        mapping = identity_client.federation.mappings.get(parsed_args.mapping)

        mapping._info.pop('links', None)
        return zip(*sorted(six.iteritems(mapping._info)))
