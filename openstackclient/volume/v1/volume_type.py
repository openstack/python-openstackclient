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

"""Volume v1 Type action implementations"""

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateVolumeType(command.ShowOne):
    """Create new volume type"""

    def get_parser(self, prog_name):
        parser = super(CreateVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Volume type name'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this volume type '
                   '(repeat option to set multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = volume_client.volume_types.create(parsed_args.name)
        volume_type._info.pop('extra_specs')
        if parsed_args.property:
            result = volume_type.set_keys(parsed_args.property)
            volume_type._info.update({'properties': utils.format_dict(result)})
        volume_type._info.pop("os-volume-type-access:is_public", None)

        return zip(*sorted(six.iteritems(volume_type._info)))


class DeleteVolumeType(command.Command):
    """Delete volume type(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            'volume_types',
            metavar='<volume-type>',
            nargs='+',
            help=_('Volume type(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result = 0

        for volume_type in parsed_args.volume_types:
            try:
                vol_type = utils.find_resource(volume_client.volume_types,
                                               volume_type)

                volume_client.volume_types.delete(vol_type)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete volume type with "
                            "name or ID '%(volume_type)s': %(e)s")
                          % {'volume_type': volume_type, 'e': e})

        if result > 0:
            total = len(parsed_args.volume_types)
            msg = (_("%(result)s of %(total)s volume types failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListVolumeType(command.Lister):
    """List volume types"""

    def get_parser(self, prog_name):
        parser = super(ListVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output')
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.long:
            columns = ('ID', 'Name', 'Extra Specs')
            column_headers = ('ID', 'Name', 'Properties')
        else:
            columns = ('ID', 'Name')
            column_headers = columns
        data = self.app.client_manager.volume.volume_types.list()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Extra Specs': utils.format_dict},
                ) for s in data))


class SetVolumeType(command.Command):
    """Set volume type properties"""

    def get_parser(self, prog_name):
        parser = super(SetVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help=_('Volume type to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this volume type '
                   '(repeat option to set multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type)

        if parsed_args.property:
            volume_type.set_keys(parsed_args.property)


class ShowVolumeType(command.ShowOne):
    """Display volume type details"""

    def get_parser(self, prog_name):
        parser = super(ShowVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            "volume_type",
            metavar="<volume-type>",
            help=_("Volume type to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type)
        properties = utils.format_dict(volume_type._info.pop('extra_specs'))
        volume_type._info.update({'properties': properties})
        volume_type._info.pop("os-volume-type-access:is_public", None)
        return zip(*sorted(six.iteritems(volume_type._info)))


class UnsetVolumeType(command.Command):
    """Unset volume type properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help=_('Volume type to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            help=_('Remove a property from this volume type '
                   '(repeat option to remove multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types,
            parsed_args.volume_type,
        )

        if parsed_args.property:
            volume_type.unset_keys(parsed_args.property)
