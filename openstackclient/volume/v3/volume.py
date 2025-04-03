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

"""Volume V3 Volume action implementations"""

import argparse
import copy
import functools
import logging

from cliff import columns as cliff_columns
from openstack import exceptions as sdk_exceptions
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.volume.v2 import volume as volume_v2


LOG = logging.getLogger(__name__)


class KeyValueHintAction(argparse.Action):
    """Uses KeyValueAction or KeyValueAppendAction based on the given key"""

    APPEND_KEYS = ('same_host', 'different_host')

    def __init__(self, *args, **kwargs):
        self._key_value_action = parseractions.KeyValueAction(*args, **kwargs)
        self._key_value_append_action = parseractions.KeyValueAppendAction(
            *args, **kwargs
        )
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values.startswith(self.APPEND_KEYS):
            self._key_value_append_action(
                parser, namespace, values, option_string=option_string
            )
        else:
            self._key_value_action(
                parser, namespace, values, option_string=option_string
            )


class AttachmentsColumn(cliff_columns.FormattableColumn):
    """Formattable column for attachments column.

    Unlike the parent FormattableColumn class, the initializer of the
    class takes server_cache as the second argument.
    osc_lib.utils.get_item_properties instantiate cliff FormattableColumn
    object with a single parameter "column value", so you need to pass
    a partially initialized class like
    ``functools.partial(AttachmentsColumn, server_cache)``.
    """

    def __init__(self, value, server_cache=None):
        super().__init__(value)
        self._server_cache = server_cache or {}

    def human_readable(self):
        """Return a formatted string of a volume's attached instances

        :rtype: a string of formatted instances
        """

        msg = ''
        for attachment in self._value:
            server = attachment['server_id']
            if server in self._server_cache.keys():
                server = self._server_cache[server].name
            device = attachment['device']
            msg += f'Attached to {server} on {device} '
        return msg


class CreateVolume(volume_v2.CreateVolume):
    _description = _("Create new volume")

    @staticmethod
    def _check_size_arg(args):
        """Check whether --size option is required or not.

        Require size parameter in case if any of the following is not
        specified:

        * snapshot
        * source volume
        * backup
        * remote source (volume to be managed)
        """

        if (
            args.snapshot or args.source or args.backup or args.remote_source
        ) is None and args.size is None:
            msg = _(
                "--size is a required option if none of --snapshot, "
                "--backup, --source, or --remote-source are provided."
            )
            raise exceptions.CommandError(msg)

    def get_parser(self, prog_name):
        parser, source_group = self._get_parser(prog_name)

        source_group.add_argument(
            "--backup",
            metavar="<backup>",
            help=_(
                "Restore backup to a volume (name or ID) "
                "(supported by --os-volume-api-version 3.47 or later)"
            ),
        )
        source_group.add_argument(
            "--remote-source",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_(
                "The attribute(s) of the existing remote volume "
                "(admin required) (repeat option to specify multiple "
                "attributes, e.g.: '--remote-source source-name=test_name "
                "--remote-source source-id=test_id')"
            ),
        )
        parser.add_argument(
            "--host",
            metavar="<host>",
            help=_(
                "Cinder host on which the existing volume resides; "
                "takes the form: host@backend-name#pool. This is only "
                "used along with the --remote-source option."
            ),
        )
        parser.add_argument(
            "--cluster",
            metavar="<cluster>",
            help=_(
                "Cinder cluster on which the existing volume resides; "
                "takes the form: cluster@backend-name#pool. This is only "
                "used along with the --remote-source option. "
                "(supported by --os-volume-api-version 3.16 or above)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        CreateVolume._check_size_arg(parsed_args)
        # size is validated in the above call to
        # _check_size_arg where we check that size
        # should be passed if we are not creating a
        # volume from snapshot, backup or source volume
        size = parsed_args.size

        volume_client_sdk = self.app.client_manager.sdk_connection.volume
        volume_client = self.app.client_manager.volume
        image_client = self.app.client_manager.image

        if (
            parsed_args.host or parsed_args.cluster
        ) and not parsed_args.remote_source:
            msg = _(
                "The --host and --cluster options are only supported "
                "with --remote-source parameter."
            )
            raise exceptions.CommandError(msg)

        if parsed_args.backup and not (
            volume_client.api_version.matches('3.47')
        ):
            msg = _(
                "--os-volume-api-version 3.47 or greater is required "
                "to create a volume from backup."
            )
            raise exceptions.CommandError(msg)

        if parsed_args.remote_source:
            if (
                parsed_args.size
                or parsed_args.consistency_group
                or parsed_args.hint
                or parsed_args.read_only
                or parsed_args.read_write
            ):
                msg = _(
                    "The --size, --consistency-group, --hint, --read-only "
                    "and --read-write options are not supported with the "
                    "--remote-source parameter."
                )
                raise exceptions.CommandError(msg)
            if parsed_args.cluster:
                if not sdk_utils.supports_microversion(
                    volume_client_sdk, '3.16'
                ):
                    msg = _(
                        "--os-volume-api-version 3.16 or greater is required "
                        "to support the cluster parameter."
                    )
                    raise exceptions.CommandError(msg)
            if parsed_args.cluster and parsed_args.host:
                msg = _(
                    "Only one of --host or --cluster needs to be specified "
                    "to manage a volume."
                )
                raise exceptions.CommandError(msg)
            if not parsed_args.cluster and not parsed_args.host:
                msg = _(
                    "One of --host or --cluster needs to be specified to "
                    "manage a volume."
                )
                raise exceptions.CommandError(msg)
            volume = volume_client_sdk.manage_volume(
                host=parsed_args.host,
                cluster=parsed_args.cluster,
                ref=parsed_args.remote_source,
                name=parsed_args.name,
                description=parsed_args.description,
                volume_type=parsed_args.type,
                availability_zone=parsed_args.availability_zone,
                metadata=parsed_args.property,
                bootable=parsed_args.bootable,
            )
            return zip(*sorted(volume.items()))

        source_volume = None
        if parsed_args.source:
            source_volume_obj = utils.find_resource(
                volume_client.volumes, parsed_args.source
            )
            source_volume = source_volume_obj.id
            size = max(size or 0, source_volume_obj.size)

        consistency_group = None
        if parsed_args.consistency_group:
            consistency_group = utils.find_resource(
                volume_client.consistencygroups, parsed_args.consistency_group
            ).id

        image = None
        if parsed_args.image:
            image = image_client.find_image(
                parsed_args.image, ignore_missing=False
            ).id

        snapshot = None
        if parsed_args.snapshot:
            snapshot_obj = utils.find_resource(
                volume_client.volume_snapshots, parsed_args.snapshot
            )
            snapshot = snapshot_obj.id
            # Cinder requires a value for size when creating a volume
            # even if creating from a snapshot. Cinder will create the
            # volume with at least the same size as the snapshot anyway,
            # so since we have the object here, just override the size
            # value if it's either not given or is smaller than the
            # snapshot size.
            size = max(size or 0, snapshot_obj.size)

        backup = None
        if parsed_args.backup:
            backup_obj = utils.find_resource(
                volume_client.backups, parsed_args.backup
            )
            backup = backup_obj.id
            # As above
            size = max(size or 0, backup_obj.size)

        volume = volume_client.volumes.create(
            size=size,
            snapshot_id=snapshot,
            name=parsed_args.name,
            description=parsed_args.description,
            volume_type=parsed_args.type,
            availability_zone=parsed_args.availability_zone,
            metadata=parsed_args.property,
            imageRef=image,
            source_volid=source_volume,
            consistencygroup_id=consistency_group,
            scheduler_hints=parsed_args.hint,
            backup_id=backup,
        )

        if parsed_args.bootable or parsed_args.non_bootable:
            try:
                if utils.wait_for_status(
                    volume_client.volumes.get,
                    volume.id,
                    success_status=['available'],
                    error_status=['error'],
                    sleep_time=1,
                ):
                    volume_client.volumes.set_bootable(
                        volume.id, parsed_args.bootable
                    )
                else:
                    msg = _(
                        "Volume status is not available for setting boot state"
                    )
                    raise exceptions.CommandError(msg)
            except Exception as e:
                LOG.error(_("Failed to set volume bootable property: %s"), e)
        if parsed_args.read_only or parsed_args.read_write:
            try:
                if utils.wait_for_status(
                    volume_client.volumes.get,
                    volume.id,
                    success_status=['available'],
                    error_status=['error'],
                    sleep_time=1,
                ):
                    volume_client.volumes.update_readonly_flag(
                        volume.id, parsed_args.read_only
                    )
                else:
                    msg = _(
                        "Volume status is not available for setting it"
                        "read only."
                    )
                    raise exceptions.CommandError(msg)
            except Exception as e:
                LOG.error(
                    _("Failed to set volume read-only access mode flag: %s"),
                    e,
                )

        # Remove key links from being displayed
        volume._info.update(
            {
                'properties': format_columns.DictColumn(
                    volume._info.pop('metadata')
                ),
                'type': volume._info.pop('volume_type'),
            }
        )
        volume._info.pop("links", None)
        return zip(*sorted(volume._info.items()))


class DeleteVolume(volume_v2.DeleteVolume):
    _description = _("Delete volume(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--remote',
            action='store_true',
            help=_("Specify this parameter to unmanage a volume."),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_client_sdk = self.app.client_manager.sdk_connection.volume
        result = 0

        if parsed_args.remote and (parsed_args.force or parsed_args.purge):
            msg = _(
                "The --force and --purge options are not "
                "supported with the --remote parameter."
            )
            raise exceptions.CommandError(msg)

        for i in parsed_args.volumes:
            try:
                volume_obj = utils.find_resource(volume_client.volumes, i)
                if parsed_args.remote:
                    volume_client_sdk.unmanage_volume(volume_obj.id)
                elif parsed_args.force:
                    volume_client.volumes.force_delete(volume_obj.id)
                else:
                    volume_client.volumes.delete(
                        volume_obj.id, cascade=parsed_args.purge
                    )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete volume with "
                        "name or ID '%(volume)s': %(e)s"
                    ),
                    {'volume': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.volumes)
            msg = _("%(result)s of %(total)s volumes failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListVolume(command.Lister):
    _description = _("List volumes")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Filter results by project (name or ID) (admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Filter results by user (name or ID) (admin only)'),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Filter results by volume name'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help=_('Filter results by status'),
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        identity_client = self.app.client_manager.identity

        if parsed_args.long:
            columns = [
                'ID',
                'Name',
                'Status',
                'Size',
                'Volume Type',
                'Bootable',
                'Attachments',
                'Metadata',
            ]
            column_headers = copy.deepcopy(columns)
            column_headers[4] = 'Type'
            column_headers[6] = 'Attached to'
            column_headers[7] = 'Properties'
        else:
            columns = [
                'ID',
                'Name',
                'Status',
                'Size',
                'Attachments',
            ]
            column_headers = copy.deepcopy(columns)
            column_headers[4] = 'Attached to'

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id

        user_id = None
        if parsed_args.user:
            user_id = identity_common.find_user(
                identity_client, parsed_args.user, parsed_args.user_domain
            ).id

        # set value of 'all_tenants' when using project option
        all_projects = bool(parsed_args.project) or parsed_args.all_projects

        search_opts = {
            'all_tenants': all_projects,
            'project_id': project_id,
            'user_id': user_id,
            'name': parsed_args.name,
            'status': parsed_args.status,
        }

        data = volume_client.volumes.list(
            search_opts=search_opts,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
        )

        do_server_list = False

        for vol in data:
            if vol.status == 'in-use':
                do_server_list = True
                break

        # Cache the server list
        server_cache = {}
        if do_server_list:
            try:
                compute_client = self.app.client_manager.compute
                for s in compute_client.servers():
                    server_cache[s.id] = s
            except sdk_exceptions.SDKException:  # noqa: S110
                # Just forget it if there's any trouble
                pass
        AttachmentsColumnWithCache = functools.partial(
            AttachmentsColumn, server_cache=server_cache
        )

        column_headers = utils.backward_compat_col_lister(
            column_headers, parsed_args.columns, {'Display Name': 'Name'}
        )

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={
                        'Metadata': format_columns.DictColumn,
                        'Attachments': AttachmentsColumnWithCache,
                    },
                )
                for s in data
            ),
        )


class MigrateVolume(command.Command):
    _description = _("Migrate volume to a new host")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar="<volume>",
            help=_("Volume to migrate (name or ID)"),
        )
        parser.add_argument(
            '--host',
            metavar="<host>",
            required=True,
            help=_(
                "Destination host (takes the form: host@backend-name#pool)"
            ),
        )
        parser.add_argument(
            '--force-host-copy',
            action="store_true",
            help=_(
                "Enable generic host-based force-migration, "
                "which bypasses driver optimizations"
            ),
        )
        parser.add_argument(
            '--lock-volume',
            action="store_true",
            help=_(
                "If specified, the volume state will be locked "
                "and will not allow a migration to be aborted "
                "(possibly by another operation)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)
        volume_client.volumes.migrate_volume(
            volume.id,
            parsed_args.host,
            parsed_args.force_host_copy,
            parsed_args.lock_volume,
        )


class SetVolume(command.Command):
    _description = _("Set volume properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Volume to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New volume name'),
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            type=int,
            help=_('Extend volume size in GB'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New volume description'),
        )
        parser.add_argument(
            "--no-property",
            dest="no_property",
            action="store_true",
            help=_(
                "Remove all properties from <volume> "
                "(specify both --no-property and --property to "
                "remove the current properties before setting "
                "new properties.)"
            ),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_(
                'Set a property on this volume '
                '(repeat option to set multiple properties)'
            ),
        )
        parser.add_argument(
            '--image-property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_(
                'Set an image property on this volume '
                '(repeat option to set multiple image properties)'
            ),
        )
        parser.add_argument(
            "--state",
            metavar="<state>",
            choices=[
                'available',
                'error',
                'creating',
                'deleting',
                'in-use',
                'attaching',
                'detaching',
                'error_deleting',
                'maintenance',
            ],
            help=_(
                'New volume state ("available", "error", "creating", '
                '"deleting", "in-use", "attaching", "detaching", '
                '"error_deleting" or "maintenance") (admin only) '
                '(This option simply changes the state of the volume '
                'in the database with no regard to actual status, '
                'exercise caution when using)'
            ),
        )
        attached_group = parser.add_mutually_exclusive_group()
        attached_group.add_argument(
            "--attached",
            action="store_true",
            help=_(
                'Set volume attachment status to "attached" '
                '(admin only) '
                '(This option simply changes the state of the volume '
                'in the database with no regard to actual status, '
                'exercise caution when using)'
            ),
        )
        attached_group.add_argument(
            "--detached",
            action="store_true",
            help=_(
                'Set volume attachment status to "detached" '
                '(admin only) '
                '(This option simply changes the state of the volume '
                'in the database with no regard to actual status, '
                'exercise caution when using)'
            ),
        )
        parser.add_argument(
            '--type',
            metavar='<volume-type>',
            help=_('New volume type (name or ID)'),
        )
        parser.add_argument(
            '--retype-policy',
            metavar='<retype-policy>',
            choices=['never', 'on-demand'],
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--migration-policy',
            metavar='<migration-policy>',
            choices=['never', 'on-demand'],
            help=_(
                'Migration policy while re-typing volume '
                '("never" or "on-demand", default is "never" ) '
                '(available only when --type option is specified)'
            ),
        )
        bootable_group = parser.add_mutually_exclusive_group()
        bootable_group.add_argument(
            "--bootable",
            action="store_true",
            help=_("Mark volume as bootable"),
        )
        bootable_group.add_argument(
            "--non-bootable",
            action="store_true",
            help=_("Mark volume as non-bootable"),
        )
        readonly_group = parser.add_mutually_exclusive_group()
        readonly_group.add_argument(
            "--read-only",
            action="store_true",
            help=_("Set volume to read-only access mode"),
        )
        readonly_group.add_argument(
            "--read-write",
            action="store_true",
            help=_("Set volume to read-write access mode"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        result = 0
        if parsed_args.retype_policy:
            msg = _(
                "The '--retype-policy' option has been deprecated in favor "
                "of '--migration-policy' option. The '--retype-policy' option "
                "will be removed in a future release. Please use "
                "'--migration-policy' instead."
            )
            self.log.warning(msg)

        if parsed_args.size:
            try:
                if parsed_args.size <= volume.size:
                    msg = (
                        _("New size must be greater than %s GB") % volume.size
                    )
                    raise exceptions.CommandError(msg)
                if volume.status not in ('available', 'in-use'):
                    msg = (
                        _(
                            "Volume is in %s state, it must be available "
                            "or in-use before size can be extended."
                        )
                        % volume.status
                    )
                    raise exceptions.CommandError(msg)
                if (
                    volume.status == 'in-use'
                    and not volume_client.api_version.matches('3.42')
                ):
                    msg = _(
                        "--os-volume-api-version 3.42 or greater is "
                        "required to extend in-use volumes."
                    )
                    raise exceptions.CommandError(msg)
                volume_client.volumes.extend(volume.id, parsed_args.size)
            except Exception as e:
                LOG.error(_("Failed to set volume size: %s"), e)
                result += 1

        if parsed_args.no_property:
            try:
                volume_client.volumes.delete_metadata(
                    volume.id, volume.metadata.keys()
                )
            except Exception as e:
                LOG.error(_("Failed to clean volume properties: %s"), e)
                result += 1

        if parsed_args.property:
            try:
                volume_client.volumes.set_metadata(
                    volume.id, parsed_args.property
                )
            except Exception as e:
                LOG.error(_("Failed to set volume property: %s"), e)
                result += 1
        if parsed_args.image_property:
            try:
                volume_client.volumes.set_image_metadata(
                    volume.id, parsed_args.image_property
                )
            except Exception as e:
                LOG.error(_("Failed to set image property: %s"), e)
                result += 1
        if parsed_args.state:
            try:
                volume_client.volumes.reset_state(volume.id, parsed_args.state)
            except Exception as e:
                LOG.error(_("Failed to set volume state: %s"), e)
                result += 1
        if parsed_args.attached:
            try:
                volume_client.volumes.reset_state(
                    volume.id, state=None, attach_status="attached"
                )
            except Exception as e:
                LOG.error(_("Failed to set volume attach-status: %s"), e)
                result += 1
        if parsed_args.detached:
            try:
                volume_client.volumes.reset_state(
                    volume.id, state=None, attach_status="detached"
                )
            except Exception as e:
                LOG.error(_("Failed to set volume attach-status: %s"), e)
                result += 1
        if parsed_args.bootable or parsed_args.non_bootable:
            try:
                volume_client.volumes.set_bootable(
                    volume.id, parsed_args.bootable
                )
            except Exception as e:
                LOG.error(_("Failed to set volume bootable property: %s"), e)
                result += 1
        if parsed_args.read_only or parsed_args.read_write:
            try:
                volume_client.volumes.update_readonly_flag(
                    volume.id, parsed_args.read_only
                )
            except Exception as e:
                LOG.error(
                    _("Failed to set volume read-only access mode flag: %s"),
                    e,
                )
                result += 1
        policy = parsed_args.migration_policy or parsed_args.retype_policy
        if parsed_args.type:
            # get the migration policy
            migration_policy = 'never'
            if policy:
                migration_policy = policy
            try:
                # find the volume type
                volume_type = utils.find_resource(
                    volume_client.volume_types, parsed_args.type
                )
                # reset to the new volume type
                volume_client.volumes.retype(
                    volume.id, volume_type.id, migration_policy
                )
            except Exception as e:
                LOG.error(_("Failed to set volume type: %s"), e)
                result += 1
        elif policy:
            # If the "--migration-policy" is specified without "--type"
            LOG.warning(
                _("'%s' option will not work without '--type' option")
                % (
                    '--migration-policy'
                    if parsed_args.migration_policy
                    else '--retype-policy'
                )
            )

        kwargs = {}
        if parsed_args.name:
            kwargs['display_name'] = parsed_args.name
        if parsed_args.description:
            kwargs['display_description'] = parsed_args.description
        if kwargs:
            try:
                volume_client.volumes.update(volume.id, **kwargs)
            except Exception as e:
                LOG.error(
                    _(
                        "Failed to update volume display name "
                        "or display description: %s"
                    ),
                    e,
                )
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("One or more of the set operations failed")
            )


class ShowVolume(command.ShowOne):
    _description = _("Display volume details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar="<volume>",
            help=_("Volume to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        # 'volume_type' --> 'type'
        volume._info.update(
            {
                'properties': format_columns.DictColumn(
                    volume._info.pop('metadata')
                ),
                'type': volume._info.pop('volume_type'),
            },
        )

        # Remove key links from being displayed
        volume._info.pop("links", None)
        return zip(*sorted(volume._info.items()))


class UnsetVolume(command.Command):
    _description = _("Unset volume properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Volume to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            help=_(
                'Remove a property from volume '
                '(repeat option to remove multiple properties)'
            ),
        )
        parser.add_argument(
            '--image-property',
            metavar='<key>',
            action='append',
            help=_(
                'Remove an image property from volume '
                '(repeat option to remove multiple image properties)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        result = 0
        if parsed_args.property:
            try:
                volume_client.volumes.delete_metadata(
                    volume.id, parsed_args.property
                )
            except Exception as e:
                LOG.error(_("Failed to unset volume property: %s"), e)
                result += 1

        if parsed_args.image_property:
            try:
                volume_client.volumes.delete_image_metadata(
                    volume.id, parsed_args.image_property
                )
            except Exception as e:
                LOG.error(_("Failed to unset image property: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("One or more of the unset operations failed")
            )


class VolumeSummary(command.ShowOne):
    _description = _("Show a summary of all volumes in this deployment.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.12'):
            msg = _(
                "--os-volume-api-version 3.12 or greater is required to "
                "support the 'volume summary' command"
            )
            raise exceptions.CommandError(msg)

        columns = [
            'total_count',
            'total_size',
        ]
        column_headers = [
            'Total Count',
            'Total Size',
        ]
        if sdk_utils.supports_microversion(volume_client, '3.36'):
            columns.append('metadata')
            column_headers.append('Metadata')

        # set value of 'all_tenants' when using project option
        all_projects = parsed_args.all_projects

        vol_summary = volume_client.summary(all_projects)

        return (
            column_headers,
            utils.get_item_properties(
                vol_summary,
                columns,
                formatters={'metadata': format_columns.DictColumn},
            ),
        )


class VolumeRevertToSnapshot(command.Command):
    _description = _("Revert a volume to a snapshot.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar="<snapshot>",
            help=_(
                'Name or ID of the snapshot to restore. The snapshot must '
                'be the most recent one known to cinder.'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.40'):
            msg = _(
                "--os-volume-api-version 3.40 or greater is required to "
                "support the 'volume revert snapshot' command"
            )
            raise exceptions.CommandError(msg)

        snapshot = volume_client.find_snapshot(
            parsed_args.snapshot,
            ignore_missing=False,
        )
        volume = volume_client.find_volume(
            snapshot.volume_id,
            ignore_missing=False,
        )

        volume_client.revert_volume_to_snapshot(volume, snapshot)
