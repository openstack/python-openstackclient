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

"""Volume v2 Type action implementations"""

import functools
import logging

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


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
        super().__init__(value)
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
        msg = _(
            "'--encryption-provider' should be specified while "
            "creating a new encryption type"
        )
        raise exceptions.CommandError(msg)
    # set the default of control location while creating
    control_location = 'front-end'
    if parsed_args.encryption_control_location:
        control_location = parsed_args.encryption_control_location
    body = {
        'provider': parsed_args.encryption_provider,
        'cipher': parsed_args.encryption_cipher,
        'key_size': parsed_args.encryption_key_size,
        'control_location': control_location,
    }
    encryption = volume_client.volume_encryption_types.create(
        volume_type, body
    )
    return encryption


def _set_encryption_type(volume_client, volume_type, parsed_args):
    # update the existing encryption type
    body = {}
    for attr in ['provider', 'cipher', 'key_size', 'control_location']:
        info = getattr(parsed_args, 'encryption_' + attr, None)
        if info is not None:
            body[attr] = info
    try:
        volume_client.volume_encryption_types.update(volume_type, body)
    except Exception as e:
        if type(e).__name__ == 'NotFound':
            # create new encryption type
            LOG.warning(
                _(
                    "No existing encryption type found, creating "
                    "new encryption type for this volume type ..."
                )
            )
            _create_encryption_type(volume_client, volume_type, parsed_args)


class CreateVolumeType(command.ShowOne):
    _description = _("Create new volume type")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("Volume type name"),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Volume type description"),
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            action="store_true",
            dest="is_public",
            default=None,
            help=_("Volume type is accessible to the public"),
        )
        public_group.add_argument(
            "--private",
            action="store_false",
            dest="is_public",
            default=None,
            help=_("Volume type is not accessible to the public"),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            dest='properties',
            help=_(
                'Set a property on this volume type '
                '(repeat option to set multiple properties)'
            ),
        )
        parser.add_argument(
            '--multiattach',
            action='store_true',
            default=False,
            help=_(
                "Enable multi-attach for this volume type "
                "(this is an alias for '--property multiattach=<is> True') "
                "(requires driver support)"
            ),
        )
        parser.add_argument(
            '--cacheable',
            action='store_true',
            default=False,
            help=_(
                "Enable caching for this volume type "
                "(this is an alias for '--property cacheable=<is> True') "
                "(requires driver support)"
            ),
        )
        parser.add_argument(
            '--replicated',
            action='store_true',
            default=False,
            help=_(
                "Enabled replication for this volume type "
                "(this is an alias for '--property replication_enabled=<is> True') "
                "(requires driver support)"
            ),
        )
        parser.add_argument(
            '--availability-zone',
            action='append',
            dest='availability_zones',
            help=_(
                "Set an availability zone for this volume type "
                "(this is an alias for '--property RESKEY:availability_zones:<az>') "
                "(repeat option to set multiple availability zones)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                "Allow <project> to access private type (name or ID) "
                "(must be used with --private option)"
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        # TODO(Huanxuan Ao): Add choices for each "--encryption-*" option.
        parser.add_argument(
            '--encryption-provider',
            metavar='<provider>',
            help=_(
                'Set the encryption provider format for '
                'this volume type (e.g "luks" or "plain") (admin only) '
                '(this option is required when setting encryption type '
                'of a volume; consider using other encryption options '
                'such as: "--encryption-cipher", "--encryption-key-size" '
                'and "--encryption-control-location")'
            ),
        )
        parser.add_argument(
            '--encryption-cipher',
            metavar='<cipher>',
            help=_(
                'Set the encryption algorithm or mode for this '
                'volume type (e.g "aes-xts-plain64") (admin only)'
            ),
        )
        parser.add_argument(
            '--encryption-key-size',
            metavar='<key-size>',
            type=int,
            help=_(
                'Set the size of the encryption key of this '
                'volume type (e.g "128" or "256") (admin only)'
            ),
        )
        parser.add_argument(
            '--encryption-control-location',
            metavar='<control-location>',
            choices=['front-end', 'back-end'],
            help=_(
                'Set the notional service where the encryption is '
                'performed ("front-end" or "back-end") (admin only) '
                '(The default value for this option is "front-end" '
                'when setting encryption type of a volume. Consider '
                'using other encryption options such as: '
                '"--encryption-cipher", "--encryption-key-size" and '
                '"--encryption-provider")'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        volume_client = self.app.client_manager.volume

        if parsed_args.project and parsed_args.is_public is not False:
            msg = _("--project is only allowed with --private")
            raise exceptions.CommandError(msg)

        kwargs = {}

        if parsed_args.is_public is not None:
            kwargs['is_public'] = parsed_args.is_public

        volume_type = volume_client.volume_types.create(
            parsed_args.name,
            description=parsed_args.description,
            **kwargs,
        )
        volume_type._info.pop('extra_specs')

        if parsed_args.project:
            try:
                project_id = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain,
                ).id
                volume_client.volume_type_access.add_project_access(
                    volume_type.id, project_id
                )
            except Exception as e:
                msg = _(
                    "Failed to add project %(project)s access to type: %(e)s"
                )
                LOG.error(msg % {'project': parsed_args.project, 'e': e})

        properties = {}
        if parsed_args.properties:
            properties.update(parsed_args.properties)
        if parsed_args.multiattach:
            properties['multiattach'] = '<is> True'
        if parsed_args.cacheable:
            properties['cacheable'] = '<is> True'
        if parsed_args.replicated:
            properties['replication_enabled'] = '<is> True'
        if parsed_args.availability_zones:
            properties['RESKEY:availability_zones'] = ','.join(
                parsed_args.availability_zones
            )
        if properties:
            result = volume_type.set_keys(properties)
            volume_type._info.update(
                {'properties': format_columns.DictColumn(result)}
            )

        if (
            parsed_args.encryption_provider
            or parsed_args.encryption_cipher
            or parsed_args.encryption_key_size
            or parsed_args.encryption_control_location
        ):
            try:
                # create new encryption
                encryption = _create_encryption_type(
                    volume_client, volume_type, parsed_args
                )
            except Exception as e:
                LOG.error(
                    _(
                        "Failed to set encryption information for this "
                        "volume type: %s"
                    ),
                    e,
                )
            # add encryption info in result
            encryption._info.pop("volume_type_id", None)
            volume_type._info.update(
                {'encryption': format_columns.DictColumn(encryption._info)}
            )

        volume_type._info.pop("os-volume-type-access:is_public", None)

        return zip(*sorted(volume_type._info.items()))


class DeleteVolumeType(command.Command):
    _description = _("Delete volume type(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "volume_types",
            metavar="<volume-type>",
            nargs="+",
            help=_("Volume type(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result = 0

        for volume_type in parsed_args.volume_types:
            try:
                vol_type = utils.find_resource(
                    volume_client.volume_types, volume_type
                )

                volume_client.volume_types.delete(vol_type)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete volume type with "
                        "name or ID '%(volume_type)s': %(e)s"
                    )
                    % {'volume_type': volume_type, 'e': e}
                )

        if result > 0:
            total = len(parsed_args.volume_types)
            msg = _(
                "%(result)s of %(total)s volume types failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListVolumeType(command.Lister):
    _description = _("List volume types")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--default",
            action='store_true',
            default=False,
            help=_('List the default volume type'),
        )
        public_group.add_argument(
            "--public",
            action="store_true",
            dest="is_public",
            default=None,
            help=_("List only public types"),
        )
        public_group.add_argument(
            "--private",
            action="store_false",
            dest="is_public",
            default=None,
            help=_("List only private types (admin only)"),
        )
        parser.add_argument(
            "--encryption-type",
            action="store_true",
            help=_(
                "Display encryption information for each volume type "
                "(admin only)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if parsed_args.long:
            columns = [
                'ID',
                'Name',
                'Is Public',
                'Description',
            ]
            column_headers = [
                'ID',
                'Name',
                'Is Public',
                'Description',
            ]
        else:
            columns = ['ID', 'Name', 'Is Public']
            column_headers = ['ID', 'Name', 'Is Public']

        if parsed_args.default:
            data = [volume_client.volume_types.default()]
        else:
            data = volume_client.volume_types.list(
                is_public=parsed_args.is_public,
            )

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
                    'volume_type_id',
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
                EncryptionInfoColumn, encryption_data=encryption
            )
            formatters['id'] = _EncryptionInfoColumn

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters=formatters,
                )
                for s in data
            ),
        )


class SetVolumeType(command.Command):
    _description = _("Set volume type properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help=_('Volume type to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set volume type name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set volume type description'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            dest='properties',
            help=_(
                'Set a property on this volume type '
                '(repeat option to set multiple properties)'
            ),
        )
        parser.add_argument(
            '--multiattach',
            action='store_true',
            default=False,
            help=_(
                "Enable multi-attach for this volume type "
                "(this is an alias for '--property multiattach=<is> True') "
                "(requires driver support)"
            ),
        )
        parser.add_argument(
            '--cacheable',
            action='store_true',
            default=False,
            help=_(
                "Enable caching for this volume type "
                "(this is an alias for '--property cacheable=<is> True') "
                "(requires driver support)"
            ),
        )
        parser.add_argument(
            '--replicated',
            action='store_true',
            default=False,
            help=_(
                "Enabled replication for this volume type "
                "(this is an alias for '--property replication_enabled=<is> True') "
                "(requires driver support)"
            ),
        )
        parser.add_argument(
            '--availability-zone',
            action='append',
            dest='availability_zones',
            help=_(
                "Set an availability zone for this volume type "
                "(this is an alias for '--property RESKEY:availability_zones:<az>') "
                "(repeat option to set multiple availability zones)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                'Set volume type access to project (name or ID) (admin only)'
            ),
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            '--public',
            action='store_true',
            dest='is_public',
            default=None,
            help=_('Volume type is accessible to the public'),
        )
        public_group.add_argument(
            '--private',
            action='store_false',
            dest='is_public',
            default=None,
            help=_("Volume type is not accessible to the public"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        # TODO(Huanxuan Ao): Add choices for each "--encryption-*" option.
        parser.add_argument(
            '--encryption-provider',
            metavar='<provider>',
            help=_(
                'Set the encryption provider format for '
                'this volume type (e.g "luks" or "plain") (admin only) '
                '(This option is required when setting encryption type '
                'of a volume for the first time. Consider using other '
                'encryption options such as: "--encryption-cipher", '
                '"--encryption-key-size" and '
                '"--encryption-control-location")'
            ),
        )
        parser.add_argument(
            '--encryption-cipher',
            metavar='<cipher>',
            help=_(
                'Set the encryption algorithm or mode for this '
                'volume type (e.g "aes-xts-plain64") (admin only)'
            ),
        )
        parser.add_argument(
            '--encryption-key-size',
            metavar='<key-size>',
            type=int,
            help=_(
                'Set the size of the encryption key of this '
                'volume type (e.g "128" or "256") (admin only)'
            ),
        )
        parser.add_argument(
            '--encryption-control-location',
            metavar='<control-location>',
            choices=['front-end', 'back-end'],
            help=_(
                'Set the notional service where the encryption is '
                'performed ("front-end" or "back-end") (admin only) '
                '(The default value for this option is "front-end" '
                'when setting encryption type of a volume for the '
                'first time. Consider using other encryption options '
                'such as: "--encryption-cipher", "--encryption-key-size" '
                'and "--encryption-provider")'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        identity_client = self.app.client_manager.identity

        volume_type = utils.find_resource(
            volume_client.volume_types,
            parsed_args.volume_type,
        )

        result = 0
        kwargs = {}

        if parsed_args.name:
            kwargs['name'] = parsed_args.name

        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.is_public is not None:
            kwargs['is_public'] = parsed_args.is_public

        if kwargs:
            try:
                volume_client.volume_types.update(volume_type.id, **kwargs)
            except Exception as e:
                LOG.error(
                    _("Failed to update volume type name or description: %s"),
                    e,
                )
                result += 1

        properties: dict[str, str] = {}
        if parsed_args.properties:
            properties.update(parsed_args.properties)
        if parsed_args.multiattach:
            properties['multiattach'] = '<is> True'
        if parsed_args.cacheable:
            properties['cacheable'] = '<is> True'
        if parsed_args.replicated:
            properties['replication_enabled'] = '<is> True'
        if parsed_args.availability_zones:
            properties['RESKEY:availability_zones'] = ','.join(
                parsed_args.availability_zones
            )
        if properties:
            try:
                volume_type.set_keys(properties)
            except Exception as e:
                LOG.error(_("Failed to set volume type properties: %s"), e)
                result += 1

        if parsed_args.project:
            project_info = None
            try:
                project_info = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain,
                )

                volume_client.volume_type_access.add_project_access(
                    volume_type.id, project_info.id
                )
            except Exception as e:
                LOG.error(
                    _("Failed to set volume type access to project: %s"), e
                )
                result += 1

        if (
            parsed_args.encryption_provider
            or parsed_args.encryption_cipher
            or parsed_args.encryption_key_size
            or parsed_args.encryption_control_location
        ):
            try:
                _set_encryption_type(volume_client, volume_type, parsed_args)
            except Exception as e:
                LOG.error(
                    _(
                        "Failed to set encryption information for this "
                        "volume type: %s"
                    ),
                    e,
                )
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("Command Failed: One or more of the operations failed")
            )


class ShowVolumeType(command.ShowOne):
    _description = _("Display volume type details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "volume_type",
            metavar="<volume-type>",
            help=_("Volume type to display (name or ID)"),
        )
        parser.add_argument(
            "--encryption-type",
            action="store_true",
            help=_(
                "Display encryption information of this volume type "
                "(admin only)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type
        )
        properties = format_columns.DictColumn(
            volume_type._info.pop('extra_specs', {})
        )
        volume_type._info.update({'properties': properties})
        access_project_ids = None
        if not volume_type.is_public:
            try:
                volume_type_access = volume_client.volume_type_access.list(
                    volume_type.id
                )
                project_ids = [
                    utils.get_field(item, 'project_id')
                    for item in volume_type_access
                ]
                # TODO(Rui Chen): This format list case can be removed after
                # patch https://review.opendev.org/#/c/330223/ merged.
                access_project_ids = format_columns.ListColumn(project_ids)
            except Exception as e:
                msg = _(
                    'Failed to get access project list for volume type '
                    '%(type)s: %(e)s'
                )
                LOG.error(msg % {'type': volume_type.id, 'e': e})
        volume_type._info.update({'access_project_ids': access_project_ids})
        if parsed_args.encryption_type:
            # show encryption type information for this volume type
            try:
                encryption = volume_client.volume_encryption_types.get(
                    volume_type.id
                )
                encryption._info.pop("volume_type_id", None)
                volume_type._info.update(
                    {'encryption': format_columns.DictColumn(encryption._info)}
                )
            except Exception as e:
                LOG.error(
                    _(
                        "Failed to display the encryption information "
                        "of this volume type: %s"
                    ),
                    e,
                )
        volume_type._info.pop("os-volume-type-access:is_public", None)
        return zip(*sorted(volume_type._info.items()))


class UnsetVolumeType(command.Command):
    _description = _("Unset volume type properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help=_('Volume type to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            dest='properties',
            help=_(
                'Remove a property from this volume type '
                '(repeat option to remove multiple properties)'
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                'Removes volume type access to project (name or ID) '
                '(admin only)'
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            "--encryption-type",
            action="store_true",
            help=_(
                "Remove the encryption type for this volume type (admin only)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        identity_client = self.app.client_manager.identity

        volume_type = utils.find_resource(
            volume_client.volume_types,
            parsed_args.volume_type,
        )

        result = 0
        if parsed_args.properties:
            try:
                volume_type.unset_keys(parsed_args.properties)
            except Exception as e:
                LOG.error(_("Failed to unset volume type properties: %s"), e)
                result += 1

        if parsed_args.project:
            project_info = None
            try:
                project_info = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain,
                )

                volume_client.volume_type_access.remove_project_access(
                    volume_type.id, project_info.id
                )
            except Exception as e:
                LOG.error(
                    _("Failed to remove volume type access from project: %s"),
                    e,
                )
                result += 1
        if parsed_args.encryption_type:
            try:
                volume_client.volume_encryption_types.delete(volume_type)
            except Exception as e:
                LOG.error(
                    _(
                        "Failed to remove the encryption type for this "
                        "volume type: %s"
                    ),
                    e,
                )
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("Command Failed: One or more of the operations failed")
            )
