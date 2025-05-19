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

"""Volume v3 snapshot action implementations"""

import functools
import logging
import typing as ty

from cliff import columns as cliff_columns
from openstack.block_storage.v3 import snapshot as _snapshot
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common

LOG = logging.getLogger(__name__)


class VolumeIdColumn(cliff_columns.FormattableColumn):
    """Formattable column for volume ID column.

    Unlike the parent FormattableColumn class, the initializer of the
    class takes volume_cache as the second argument.
    osc_lib.utils.get_item_properties instantiate cliff FormattableColumn
    object with a single parameter "column value", so you need to pass
    a partially initialized class like
    ``functools.partial(VolumeIdColumn, volume_cache)``.
    """

    def __init__(self, value, volume_cache=None):
        super().__init__(value)
        self._volume_cache = volume_cache or {}

    def human_readable(self):
        """Return a volume name if available

        :rtype: either the volume ID or name
        """
        volume_id = self._value
        volume = volume_id
        if volume_id in self._volume_cache.keys():
            volume = self._volume_cache[volume_id].name
        return volume


def _format_snapshot(snapshot: _snapshot.Snapshot) -> dict[str, ty.Any]:
    # Some columns returned by openstacksdk should not be shown because they're
    # either irrelevant or duplicates
    ignored_columns = {
        # computed columns
        'location',
        # create-only columns
        'consumes_quota',
        'force',
        'group_snapshot_id',
        # ignored columns
        'os-extended-snapshot-attributes:progress',
        'os-extended-snapshot-attributes:project_id',
        'updated_at',
        'user_id',
        # unnecessary columns
        'links',
    }

    info = snapshot.to_dict(original_names=True)
    data = {}
    for key, value in info.items():
        if key in ignored_columns:
            continue

        data[key] = value

    data.update(
        {
            'properties': format_columns.DictColumn(data.pop('metadata')),
        }
    )

    return data


class CreateVolumeSnapshot(command.ShowOne):
    _description = _("Create new volume snapshot")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "snapshot_name",
            metavar="<snapshot-name>",
            help=_("Name of the new snapshot"),
        )
        parser.add_argument(
            "--volume",
            metavar="<volume>",
            help=_(
                "Volume to snapshot (name or ID) (default is <snapshot-name>)"
            ),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Description of the snapshot"),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help=_(
                "Create a snapshot attached to an instance. Default is False"
            ),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            dest='properties',
            action=parseractions.KeyValueAction,
            help=_(
                "Set a property to this snapshot "
                "(repeat option to set multiple properties)"
            ),
        )
        parser.add_argument(
            "--remote-source",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_(
                "The attribute(s) of the existing remote volume snapshot "
                "(admin required) (repeat option to specify multiple "
                "attributes) e.g.: '--remote-source source-name=test_name "
                "--remote-source source-id=test_id'"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        volume = parsed_args.volume
        if not parsed_args.volume:
            volume = parsed_args.snapshot_name
        volume_id = volume_client.find_volume(volume, ignore_missing=False).id

        if parsed_args.remote_source:
            # Create a new snapshot from an existing remote snapshot source
            if parsed_args.force:
                msg = _(
                    "'--force' option will not work when you create "
                    "new volume snapshot from an existing remote "
                    "volume snapshot"
                )
                LOG.warning(msg)

            snapshot = volume_client.manage_snapshot(
                volume_id=volume_id,
                ref=parsed_args.remote_source,
                name=parsed_args.snapshot_name,
                description=parsed_args.description,
                metadata=parsed_args.properties,
            )
        else:
            # Create a new snapshot from scratch
            snapshot = volume_client.create_snapshot(
                volume_id=volume_id,
                force=parsed_args.force,
                name=parsed_args.snapshot_name,
                description=parsed_args.description,
                metadata=parsed_args.properties,
            )

        data = _format_snapshot(snapshot)
        return zip(*sorted(data.items()))


class DeleteVolumeSnapshot(command.Command):
    _description = _("Delete volume snapshot(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "snapshots",
            metavar="<snapshot>",
            nargs="+",
            help=_("Snapshot(s) to delete (name or ID)"),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=_(
                "Attempt forced removal of snapshot(s), "
                "regardless of state (defaults to False)"
            ),
        )
        parser.add_argument(
            '--remote',
            action='store_true',
            help=_(
                'Unmanage the snapshot, removing it from the Block Storage '
                'service management but not from the backend.'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume
        result = 0

        if parsed_args.remote:
            if parsed_args.force:
                msg = _(
                    "The --force option is not supported with the "
                    "--remote parameter."
                )
                raise exceptions.CommandError(msg)

        for snapshot in parsed_args.snapshots:
            try:
                snapshot_id = volume_client.find_snapshot(
                    snapshot, ignore_missing=False
                ).id
                if parsed_args.remote:
                    volume_client.unmanage_snapshot(snapshot_id)
                else:
                    volume_client.delete_snapshot(
                        snapshot_id, force=parsed_args.force
                    )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete snapshot with "
                        "name or ID '%(snapshot)s': %(e)s"
                    )
                    % {'snapshot': snapshot, 'e': e}
                )

        if result > 0:
            total = len(parsed_args.snapshots)
            msg = _("%(result)s of %(total)s snapshots failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListVolumeSnapshot(command.Lister):
    _description = _("List volume snapshots")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Filter results by project (name or ID) (admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            default=None,
            help=_('Filters results by a name.'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            choices=[
                'available',
                'error',
                'creating',
                'deleting',
                'error_deleting',
            ],
            help=_(
                "Filters results by a status. "
                "('available', 'error', 'creating', 'deleting'"
                " or 'error_deleting')"
            ),
        )
        parser.add_argument(
            '--volume',
            metavar='<volume>',
            default=None,
            help=_('Filters results by a volume (name or ID).'),
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume
        identity_client = self.app.client_manager.identity

        columns: tuple[str, ...] = (
            'id',
            'name',
            'description',
            'status',
            'size',
        )
        column_headers: tuple[str, ...] = (
            'ID',
            'Name',
            'Description',
            'Status',
            'Size',
        )
        if parsed_args.long:
            columns += (
                'created_at',
                'volume_id',
                'metadata',
            )
            column_headers += (
                'Created At',
                'Volume',
                'Properties',
            )

        # Cache the volume list
        volume_cache = {}
        try:
            for s in volume_client.volumes():
                volume_cache[s.id] = s
        except Exception:  # noqa: S110
            # Just forget it if there's any trouble
            pass
        _VolumeIdColumn = functools.partial(
            VolumeIdColumn, volume_cache=volume_cache
        )

        volume_id = None
        if parsed_args.volume:
            volume_id = volume_client.find_volume(
                parsed_args.volume, ignore_missing=False
            ).id

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id

        # set value of 'all_tenants' when using project option
        all_projects = (
            True if parsed_args.project else parsed_args.all_projects
        )

        data = volume_client.snapshots(
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            all_projects=all_projects,
            project_id=project_id,
            name=parsed_args.name,
            status=parsed_args.status,
            volume_id=volume_id,
        )
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={
                        'metadata': format_columns.DictColumn,
                        'volume_id': _VolumeIdColumn,
                    },
                )
                for s in data
            ),
        )


class SetVolumeSnapshot(command.Command):
    _description = _("Set volume snapshot properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help=_('Snapshot to modify (name or ID)'),
        )
        parser.add_argument(
            '--name', metavar='<name>', help=_('New snapshot name')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New snapshot description'),
        )
        parser.add_argument(
            "--no-property",
            dest="no_property",
            action="store_true",
            help=_(
                "Remove all properties from <snapshot> "
                "(specify both --no-property and --property to "
                "remove the current properties before setting "
                "new properties.)"
            ),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            dest='properties',
            help=_(
                'Property to add/change for this snapshot '
                '(repeat option to set multiple properties)'
            ),
        )
        parser.add_argument(
            '--state',
            metavar='<state>',
            choices=[
                'available',
                'error',
                'creating',
                'deleting',
                'error_deleting',
            ],
            help=_(
                'New snapshot state. ("available", "error", "creating", '
                '"deleting", or "error_deleting") (admin only) '
                '(This option simply changes the state of the snapshot '
                'in the database with no regard to actual status, '
                'exercise caution when using)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        snapshot = volume_client.find_snapshot(
            parsed_args.snapshot, ignore_missing=False
        )

        result = 0
        if parsed_args.no_property:
            try:
                volume_client.delete_snapshot_metadata(
                    snapshot.id, keys=list(snapshot.metadata)
                )
            except Exception as e:
                LOG.error(_("Failed to clean snapshot properties: %s"), e)
                result += 1

        if parsed_args.properties:
            try:
                volume_client.set_snapshot_metadata(
                    snapshot.id, **parsed_args.properties
                )
            except Exception as e:
                LOG.error(_("Failed to set snapshot property: %s"), e)
                result += 1

        if parsed_args.state:
            try:
                volume_client.reset_snapshot_status(
                    snapshot.id, parsed_args.state
                )
            except Exception as e:
                LOG.error(_("Failed to set snapshot state: %s"), e)
                result += 1

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if kwargs:
            try:
                volume_client.update_snapshot(snapshot.id, **kwargs)
            except Exception as e:
                LOG.error(
                    _("Failed to update snapshot name or description: %s"),
                    e,
                )
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("One or more of the set operations failed")
            )


class ShowVolumeSnapshot(command.ShowOne):
    _description = _("Display volume snapshot details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help=_("Snapshot to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        snapshot = volume_client.find_snapshot(
            parsed_args.snapshot, ignore_missing=False
        )

        data = _format_snapshot(snapshot)
        return zip(*sorted(data.items()))


class UnsetVolumeSnapshot(command.Command):
    _description = _("Unset volume snapshot properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help=_('Snapshot to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            dest='properties',
            action='append',
            default=[],
            help=_(
                'Property to remove from snapshot '
                '(repeat option to remove multiple properties)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        snapshot = volume_client.find_snapshot(
            parsed_args.snapshot, ignore_missing=False
        )

        if parsed_args.properties:
            volume_client.delete_snapshot_metadata(
                snapshot.id, keys=parsed_args.properties
            )
