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

"""Volume v1 Volume action implementations"""

import argparse
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
        super(AttachmentsColumn, self).__init__(value)
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
            msg += 'Attached to %s on %s ' % (server, device)
        return msg


def _check_size_arg(args):
    """Check whether --size option is required or not.

    Require size parameter only in case when snapshot or source
    volume is not specified.
    """

    if ((args.snapshot or args.source)
            is None and args.size is None):
        msg = _("--size is a required option if snapshot "
                "or source volume is not specified.")
        raise exceptions.CommandError(msg)


class CreateVolume(command.ShowOne):
    _description = _("Create new volume")

    def get_parser(self, prog_name):
        parser = super(CreateVolume, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Volume name'),
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            type=int,
            help=_("Volume size in GB (Required unless --snapshot or "
                   "--source is specified)"),
        )
        parser.add_argument(
            '--type',
            metavar='<volume-type>',
            help=_("Set the type of volume"),
        )
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument(
            '--image',
            metavar='<image>',
            help=_('Use <image> as source of volume (name or ID)'),
        )
        source_group.add_argument(
            '--snapshot',
            metavar='<snapshot>',
            help=_('Use <snapshot> as source of volume (name or ID)'),
        )
        source_group.add_argument(
            '--snapshot-id',
            metavar='<snapshot-id>',
            help=argparse.SUPPRESS,
        )
        source_group.add_argument(
            '--source',
            metavar='<volume>',
            help=_('Volume to clone (name or ID)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Volume description'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Specify an alternate user (name or ID)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Specify an alternate project (name or ID)'),
        )
        parser.add_argument(
            '--availability-zone',
            metavar='<availability-zone>',
            help=_('Create volume in <availability-zone>'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this volume '
                   '(repeat option to set multiple properties)'),
        )
        bootable_group = parser.add_mutually_exclusive_group()
        bootable_group.add_argument(
            "--bootable",
            action="store_true",
            help=_("Mark volume as bootable")
        )
        bootable_group.add_argument(
            "--non-bootable",
            action="store_true",
            help=_("Mark volume as non-bootable (default)")
        )
        readonly_group = parser.add_mutually_exclusive_group()
        readonly_group.add_argument(
            "--read-only",
            action="store_true",
            help=_("Set volume to read-only access mode")
        )
        readonly_group.add_argument(
            "--read-write",
            action="store_true",
            help=_("Set volume to read-write access mode (default)")
        )

        return parser

    def take_action(self, parsed_args):
        _check_size_arg(parsed_args)
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image
        volume_client = self.app.client_manager.volume

        source_volume = None
        if parsed_args.source:
            source_volume = utils.find_resource(
                volume_client.volumes,
                parsed_args.source,
            ).id

        project = None
        if parsed_args.project:
            project = utils.find_resource(
                identity_client.tenants,
                parsed_args.project,
            ).id

        user = None
        if parsed_args.user:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            ).id

        image = None
        if parsed_args.image:
            image = utils.find_resource(
                image_client.images,
                parsed_args.image,
            ).id

        snapshot = parsed_args.snapshot or parsed_args.snapshot_id

        volume = volume_client.volumes.create(
            parsed_args.size,
            snapshot,
            source_volume,
            parsed_args.name,
            parsed_args.description,
            parsed_args.type,
            user,
            project,
            parsed_args.availability_zone,
            parsed_args.property,
            image,
        )

        if parsed_args.bootable or parsed_args.non_bootable:
            try:
                volume_client.volumes.set_bootable(
                    volume.id, parsed_args.bootable)
            except Exception as e:
                LOG.error(_("Failed to set volume bootable property: %s"), e)
        if parsed_args.read_only or parsed_args.read_write:
            try:
                volume_client.volumes.update_readonly_flag(
                    volume.id,
                    parsed_args.read_only)
            except Exception as e:
                LOG.error(_("Failed to set volume read-only access "
                            "mode flag: %s"), e)

        # Map 'metadata' column to 'properties'
        volume._info.update(
            {
                'properties':
                format_columns.DictColumn(volume._info.pop('metadata')),
                'type': volume._info.pop('volume_type'),
            },
        )
        # Replace "display_name" by "name", keep consistent in v1 and v2
        if 'display_name' in volume._info:
            volume._info.update({'name': volume._info.pop('display_name')})
        volume_info = utils.backward_compat_col_showone(
            volume._info, parsed_args.columns, {'display_name': 'name'}
        )

        return zip(*sorted(six.iteritems(volume_info)))


class DeleteVolume(command.Command):
    _description = _("Delete volume(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volumes',
            metavar='<volume>',
            nargs="+",
            help=_('Volume(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_('Attempt forced removal of volume(s), regardless of state '
                   '(defaults to False)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result = 0

        for i in parsed_args.volumes:
            try:
                volume_obj = utils.find_resource(
                    volume_client.volumes, i)
                if parsed_args.force:
                    volume_client.volumes.force_delete(volume_obj.id)
                else:
                    volume_client.volumes.delete(volume_obj.id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete volume with "
                            "name or ID '%(volume)s': %(e)s"),
                          {'volume': i, 'e': e})

        if result > 0:
            total = len(parsed_args.volumes)
            msg = (_("%(result)s of %(total)s volumes failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListVolume(command.Lister):
    _description = _("List volumes")

    def get_parser(self, prog_name):
        parser = super(ListVolume, self).get_parser(prog_name)
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
        parser.add_argument(
            '--limit',
            type=int,
            action=parseractions.NonNegativeAction,
            metavar='<num-volumes>',
            help=_('Maximum number of volumes to display'),
        )
        return parser

    def take_action(self, parsed_args):

        volume_client = self.app.client_manager.volume
        compute_client = self.app.client_manager.compute

        if parsed_args.long:
            columns = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Volume Type',
                'Bootable',
                'Attachments',
                'Metadata',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Size',
                'Type',
                'Bootable',
                'Attached to',
                'Properties',
            )
        else:
            columns = (
                'ID',
                'Display Name',
                'Status',
                'Size',
                'Attachments',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Size',
                'Attached to',
            )

        # Cache the server list
        server_cache = {}
        try:
            for s in compute_client.servers.list():
                server_cache[s.id] = s
        except Exception:
            # Just forget it if there's any trouble
            pass
        AttachmentsColumnWithCache = functools.partial(
            AttachmentsColumn, server_cache=server_cache)

        search_opts = {
            'all_tenants': parsed_args.all_projects,
            'display_name': parsed_args.name,
            'status': parsed_args.status,
        }

        data = volume_client.volumes.list(
            search_opts=search_opts,
            limit=parsed_args.limit,
        )
        column_headers = utils.backward_compat_col_lister(
            column_headers, parsed_args.columns, {'Display Name': 'Name'})

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': format_columns.DictColumn,
                                'Attachments': AttachmentsColumnWithCache},
                ) for s in data))


class MigrateVolume(command.Command):
    _description = _("Migrate volume to a new host")

    def get_parser(self, prog_name):
        parser = super(MigrateVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar="<volume>",
            help=_("Volume to migrate (name or ID)")
        )
        parser.add_argument(
            '--host',
            metavar="<host>",
            required=True,
            help=_("Destination host (takes the form: host@backend-name#pool)")
        )
        parser.add_argument(
            '--force-host-copy',
            action="store_true",
            help=_("Enable generic host-based force-migration, "
                   "which bypasses driver optimizations")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)
        volume_client.volumes.migrate_volume(volume.id, parsed_args.host,
                                             parsed_args.force_host_copy,)


class SetVolume(command.Command):
    _description = _("Set volume properties")

    def get_parser(self, prog_name):
        parser = super(SetVolume, self).get_parser(prog_name)
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
            '--description',
            metavar='<description>',
            help=_('New volume description'),
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            type=int,
            help=_('Extend volume size in GB'),
        )
        parser.add_argument(
            "--no-property",
            dest="no_property",
            action="store_true",
            help=_("Remove all properties from <volume> "
                   "(specify both --no-property and --property to "
                   "remove the current properties before setting "
                   "new properties.)"),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this volume '
                   '(repeat option to set multiple properties)'),
        )
        bootable_group = parser.add_mutually_exclusive_group()
        bootable_group.add_argument(
            "--bootable",
            action="store_true",
            help=_("Mark volume as bootable")
        )
        bootable_group.add_argument(
            "--non-bootable",
            action="store_true",
            help=_("Mark volume as non-bootable")
        )
        readonly_group = parser.add_mutually_exclusive_group()
        readonly_group.add_argument(
            "--read-only",
            action="store_true",
            help=_("Set volume to read-only access mode")
        )
        readonly_group.add_argument(
            "--read-write",
            action="store_true",
            help=_("Set volume to read-write access mode")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        result = 0
        if parsed_args.size:
            try:
                if volume.status != 'available':
                    msg = (_("Volume is in %s state, it must be available "
                           "before size can be extended") % volume.status)
                    raise exceptions.CommandError(msg)
                if parsed_args.size <= volume.size:
                    msg = (_("New size must be greater than %s GB")
                           % volume.size)
                    raise exceptions.CommandError(msg)
                volume_client.volumes.extend(volume.id, parsed_args.size)
            except Exception as e:
                LOG.error(_("Failed to set volume size: %s"), e)
                result += 1

        if parsed_args.no_property:
            try:
                volume_client.volumes.delete_metadata(
                    volume.id, volume.metadata.keys())
            except Exception as e:
                LOG.error(_("Failed to clean volume properties: %s"), e)
                result += 1

        if parsed_args.property:
            try:
                volume_client.volumes.set_metadata(
                    volume.id,
                    parsed_args.property)
            except Exception as e:
                LOG.error(_("Failed to set volume property: %s"), e)
                result += 1
        if parsed_args.bootable or parsed_args.non_bootable:
            try:
                volume_client.volumes.set_bootable(
                    volume.id, parsed_args.bootable)
            except Exception as e:
                LOG.error(_("Failed to set volume bootable property: %s"), e)
                result += 1
        if parsed_args.read_only or parsed_args.read_write:
            try:
                volume_client.volumes.update_readonly_flag(
                    volume.id,
                    parsed_args.read_only)
            except Exception as e:
                LOG.error(_("Failed to set volume read-only access "
                            "mode flag: %s"), e)
                result += 1
        kwargs = {}
        if parsed_args.name:
            kwargs['display_name'] = parsed_args.name
        if parsed_args.description:
            kwargs['display_description'] = parsed_args.description
        if kwargs:
            try:
                volume_client.volumes.update(volume.id, **kwargs)
            except Exception as e:
                LOG.error(_("Failed to update volume display name "
                          "or display description: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("One or more of the "
                                          "set operations failed"))


class ShowVolume(command.ShowOne):
    _description = _("Show volume details")

    def get_parser(self, prog_name):
        parser = super(ShowVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Volume to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)
        # Map 'metadata' column to 'properties'
        volume._info.update(
            {
                'properties':
                format_columns.DictColumn(volume._info.pop('metadata')),
                'type': volume._info.pop('volume_type'),
            },
        )
        if 'os-vol-tenant-attr:tenant_id' in volume._info:
            volume._info.update(
                {'project_id': volume._info.pop(
                    'os-vol-tenant-attr:tenant_id')}
            )
        # Replace "display_name" by "name", keep consistent in v1 and v2
        if 'display_name' in volume._info:
            volume._info.update({'name': volume._info.pop('display_name')})

        volume_info = utils.backward_compat_col_showone(
            volume._info, parsed_args.columns, {'display_name': 'name'}
        )

        return zip(*sorted(six.iteritems(volume_info)))


class UnsetVolume(command.Command):
    _description = _("Unset volume properties")

    def get_parser(self, prog_name):
        parser = super(UnsetVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Volume to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            help=_('Remove a property from volume '
                   '(repeat option to remove multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(
            volume_client.volumes, parsed_args.volume)

        if parsed_args.property:
            volume_client.volumes.delete_metadata(
                volume.id,
                parsed_args.property,
            )
