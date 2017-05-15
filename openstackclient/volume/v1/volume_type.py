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

import functools
import logging

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class EncryptionInfoColumn(cliff_columns.FormattableColumn):
    """Formattable column for encryption info column.

    Unlike the parent FormattableColumn class, the initializer of the
    class takes encryption_data as the second argument.
    osc_lib.utils.get_item_properties instantiate cliff FormattableColumn
    object with a single parameter "column value", so you need to pass
    a partially initialized class like
    ``functools.partial(EncryptionInfoColumn encryption_data)``.
    """

    def __init__(self, value, encryption_data=None):
        super(EncryptionInfoColumn, self).__init__(value)
        self._encryption_data = encryption_data or {}

    def _get_encryption_info(self):
        type_id = self._value
        return self._encryption_data.get(type_id)

    def human_readable(self):
        encryption_info = self._get_encryption_info()
        if encryption_info:
            return utils.format_dict(encryption_info)
        else:
            return '-'

    def machine_readable(self):
        return self._get_encryption_info()


def _create_encryption_type(volume_client, volume_type, parsed_args):
    if not parsed_args.encryption_provider:
        msg = _("'--encryption-provider' should be specified while "
                "creating a new encryption type")
        raise exceptions.CommandError(msg)
    # set the default of control location while creating
    control_location = 'front-end'
    if parsed_args.encryption_control_location:
        control_location = parsed_args.encryption_control_location
    body = {
        'provider': parsed_args.encryption_provider,
        'cipher': parsed_args.encryption_cipher,
        'key_size': parsed_args.encryption_key_size,
        'control_location': control_location
    }
    encryption = volume_client.volume_encryption_types.create(
        volume_type, body)
    return encryption


class CreateVolumeType(command.ShowOne):
    _description = _("Create new volume type")

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
        # TODO(Huanxuan Ao): Add choices for each "--encryption-*" option.
        parser.add_argument(
            '--encryption-provider',
            metavar='<provider>',
            help=_('Set the encryption provider format for '
                   'this volume type (e.g "luks" or "plain") (admin only) '
                   '(This option is required when setting encryption type '
                   'of a volume. Consider using other encryption options '
                   'such as: "--encryption-cipher", "--encryption-key-size" '
                   'and "--encryption-control-location")'),
        )
        parser.add_argument(
            '--encryption-cipher',
            metavar='<cipher>',
            help=_('Set the encryption algorithm or mode for this '
                   'volume type (e.g "aes-xts-plain64") (admin only)'),
        )
        parser.add_argument(
            '--encryption-key-size',
            metavar='<key-size>',
            type=int,
            help=_('Set the size of the encryption key of this '
                   'volume type (e.g "128" or "256") (admin only)'),
        )
        parser.add_argument(
            '--encryption-control-location',
            metavar='<control-location>',
            choices=['front-end', 'back-end'],
            help=_('Set the notional service where the encryption is '
                   'performed ("front-end" or "back-end") (admin only) '
                   '(The default value for this option is "front-end" '
                   'when setting encryption type of a volume. Consider '
                   'using other encryption options such as: '
                   '"--encryption-cipher", "--encryption-key-size" and '
                   '"--encryption-provider")'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = volume_client.volume_types.create(parsed_args.name)
        volume_type._info.pop('extra_specs')
        if parsed_args.property:
            result = volume_type.set_keys(parsed_args.property)
            volume_type._info.update(
                {'properties': format_columns.DictColumn(result)})
        if (parsed_args.encryption_provider or
                parsed_args.encryption_cipher or
                parsed_args.encryption_key_size or
                parsed_args.encryption_control_location):
            try:
                # create new encryption
                encryption = _create_encryption_type(
                    volume_client, volume_type, parsed_args)
            except Exception as e:
                LOG.error(_("Failed to set encryption information for this "
                            "volume type: %s"), e)
            # add encryption info in result
            encryption._info.pop("volume_type_id", None)
            volume_type._info.update(
                {'encryption': format_columns.DictColumn(encryption._info)})
        volume_type._info.pop("os-volume-type-access:is_public", None)

        return zip(*sorted(six.iteritems(volume_type._info)))


class DeleteVolumeType(command.Command):
    _description = _("Delete volume type(s)")

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
    _description = _("List volume types")

    def get_parser(self, prog_name):
        parser = super(ListVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output')
        )
        parser.add_argument(
            "--encryption-type",
            action="store_true",
            help=_("Display encryption information for each volume type "
                   "(admin only)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        if parsed_args.long:
            columns = ['ID', 'Name', 'Is Public', 'Extra Specs']
            column_headers = ['ID', 'Name', 'Is Public', 'Properties']
        else:
            columns = ['ID', 'Name', 'Is Public']
            column_headers = ['ID', 'Name', 'Is Public']
        data = volume_client.volume_types.list()

        formatters = {'Extra Specs': format_columns.DictColumn}

        if parsed_args.encryption_type:
            encryption = {}
            for d in volume_client.volume_encryption_types.list():
                volume_type_id = d._info['volume_type_id']
                # remove some redundant information
                del_key = [
                    'deleted',
                    'created_at',
                    'updated_at',
                    'deleted_at',
                    'volume_type_id'
                ]
                for key in del_key:
                    d._info.pop(key, None)
                # save the encryption information with their volume type ID
                encryption[volume_type_id] = d._info
            # We need to get volume type ID, then show encryption
            # information according to the ID, so use "id" to keep
            # difference to the real "ID" column.
            columns += ['id']
            column_headers += ['Encryption']

            _EncryptionInfoColumn = functools.partial(
                EncryptionInfoColumn, encryption_data=encryption)
            formatters['id'] = _EncryptionInfoColumn

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=formatters,
                ) for s in data))


class SetVolumeType(command.Command):
    _description = _("Set volume type properties")

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
        # TODO(Huanxuan Ao): Add choices for each "--encryption-*" option.
        parser.add_argument(
            '--encryption-provider',
            metavar='<provider>',
            help=_('Set the encryption provider format for '
                   'this volume type (e.g "luks" or "plain") (admin only) '
                   '(This option is required when setting encryption type '
                   'of a volume. Consider using other encryption options '
                   'such as: "--encryption-cipher", "--encryption-key-size" '
                   'and "--encryption-control-location")'),
        )
        parser.add_argument(
            '--encryption-cipher',
            metavar='<cipher>',
            help=_('Set the encryption algorithm or mode for this '
                   'volume type (e.g "aes-xts-plain64") (admin only)'),
        )
        parser.add_argument(
            '--encryption-key-size',
            metavar='<key-size>',
            type=int,
            help=_('Set the size of the encryption key of this '
                   'volume type (e.g "128" or "256") (admin only)'),
        )
        parser.add_argument(
            '--encryption-control-location',
            metavar='<control-location>',
            choices=['front-end', 'back-end'],
            help=_('Set the notional service where the encryption is '
                   'performed ("front-end" or "back-end") (admin only) '
                   '(The default value for this option is "front-end" '
                   'when setting encryption type of a volume. Consider '
                   'using other encryption options such as: '
                   '"--encryption-cipher", "--encryption-key-size" and '
                   '"--encryption-provider")'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type)

        result = 0
        if parsed_args.property:
            try:
                volume_type.set_keys(parsed_args.property)
            except Exception as e:
                LOG.error(_("Failed to set volume type property: %s"), e)
                result += 1

        if (parsed_args.encryption_provider or
                parsed_args.encryption_cipher or
                parsed_args.encryption_key_size or
                parsed_args.encryption_control_location):
            try:
                _create_encryption_type(
                    volume_client, volume_type, parsed_args)
            except Exception as e:
                LOG.error(_("Failed to set encryption information for this "
                            "volume type: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("Command Failed: One or more of"
                                            " the operations failed"))


class ShowVolumeType(command.ShowOne):
    _description = _("Display volume type details")

    def get_parser(self, prog_name):
        parser = super(ShowVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            "volume_type",
            metavar="<volume-type>",
            help=_("Volume type to display (name or ID)")
        )
        parser.add_argument(
            "--encryption-type",
            action="store_true",
            help=_("Display encryption information of this volume type "
                   "(admin only)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type)
        properties = format_columns.DictColumn(
            volume_type._info.pop('extra_specs'))
        volume_type._info.update({'properties': properties})
        if parsed_args.encryption_type:
            # show encryption type information for this volume type
            try:
                encryption = volume_client.volume_encryption_types.get(
                    volume_type.id)
                encryption._info.pop("volume_type_id", None)
                volume_type._info.update(
                    {'encryption':
                     format_columns.DictColumn(encryption._info)})
            except Exception as e:
                LOG.error(_("Failed to display the encryption information "
                          "of this volume type: %s"), e)
        volume_type._info.pop("os-volume-type-access:is_public", None)
        return zip(*sorted(six.iteritems(volume_type._info)))


class UnsetVolumeType(command.Command):
    _description = _("Unset volume type properties")

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
        parser.add_argument(
            "--encryption-type",
            action="store_true",
            help=_("Remove the encryption type for this volume type "
                   "(admin oly)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types,
            parsed_args.volume_type,
        )

        result = 0
        if parsed_args.property:
            try:
                volume_type.unset_keys(parsed_args.property)
            except Exception as e:
                LOG.error(_("Failed to unset volume type property: %s"), e)
                result += 1
        if parsed_args.encryption_type:
            try:
                volume_client.volume_encryption_types.delete(volume_type)
            except Exception as e:
                LOG.error(_("Failed to remove the encryption type for this "
                          "volume type: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("Command Failed: One or more of"
                                          " the operations failed"))
