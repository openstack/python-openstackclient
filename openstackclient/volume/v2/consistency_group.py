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

"""Volume v2 consistency group action implementations"""

import logging

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _find_volumes(parsed_args_volumes, volume_client):
    result = 0
    uuid = ''
    for volume in parsed_args_volumes:
        try:
            volume_id = utils.find_resource(
                volume_client.volumes, volume).id
            uuid += volume_id + ','
        except Exception as e:
            result += 1
            LOG.error(_("Failed to find volume with "
                        "name or ID '%(volume)s':%(e)s")
                      % {'volume': volume, 'e': e})

    return result, uuid


class AddVolumeToConsistencyGroup(command.Command):
    _description = _("Add volume(s) to consistency group")

    def get_parser(self, prog_name):
        parser = super(AddVolumeToConsistencyGroup, self).get_parser(prog_name)
        parser.add_argument(
            'consistency_group',
            metavar="<consistency-group>",
            help=_('Consistency group to contain <volume> (name or ID)'),
        )
        parser.add_argument(
            'volumes',
            metavar='<volume>',
            nargs='+',
            help=_('Volume(s) to add to <consistency-group> (name or ID) '
                   '(repeat option to add multiple volumes)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result, add_uuid = _find_volumes(parsed_args.volumes, volume_client)

        if result > 0:
            total = len(parsed_args.volumes)
            LOG.error(_("%(result)s of %(total)s volumes failed "
                      "to add.") % {'result': result, 'total': total})

        if add_uuid:
            add_uuid = add_uuid.rstrip(',')
            consistency_group_id = utils.find_resource(
                volume_client.consistencygroups,
                parsed_args.consistency_group).id
            volume_client.consistencygroups.update(
                consistency_group_id, add_volumes=add_uuid)


class CreateConsistencyGroup(command.ShowOne):
    _description = _("Create new consistency group.")

    def get_parser(self, prog_name):
        parser = super(CreateConsistencyGroup, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            nargs="?",
            help=_("Name of new consistency group (default to None)")
        )
        exclusive_group = parser.add_mutually_exclusive_group(required=True)
        exclusive_group.add_argument(
            "--volume-type",
            metavar="<volume-type>",
            help=_("Volume type of this consistency group (name or ID)")
        )
        exclusive_group.add_argument(
            "--consistency-group-source",
            metavar="<consistency-group>",
            help=_("Existing consistency group (name or ID)")
        )
        exclusive_group.add_argument(
            "--consistency-group-snapshot",
            metavar="<consistency-group-snapshot>",
            help=_("Existing consistency group snapshot (name or ID)")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Description of this consistency group")
        )
        parser.add_argument(
            "--availability-zone",
            metavar="<availability-zone>",
            help=_("Availability zone for this consistency group "
                   "(not available if creating consistency group "
                   "from source)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        if parsed_args.volume_type:
            volume_type_id = utils.find_resource(
                volume_client.volume_types,
                parsed_args.volume_type).id
            consistency_group = volume_client.consistencygroups.create(
                volume_type_id,
                name=parsed_args.name,
                description=parsed_args.description,
                availability_zone=parsed_args.availability_zone
            )
        else:
            if parsed_args.availability_zone:
                msg = _("'--availability-zone' option will not work "
                        "if creating consistency group from source")
                LOG.warning(msg)

            consistency_group_id = None
            consistency_group_snapshot = None
            if parsed_args.consistency_group_source:
                consistency_group_id = utils.find_resource(
                    volume_client.consistencygroups,
                    parsed_args.consistency_group_source).id
            elif parsed_args.consistency_group_snapshot:
                consistency_group_snapshot = utils.find_resource(
                    volume_client.cgsnapshots,
                    parsed_args.consistency_group_snapshot).id

            consistency_group = (
                volume_client.consistencygroups.create_from_src(
                    consistency_group_snapshot,
                    consistency_group_id,
                    name=parsed_args.name,
                    description=parsed_args.description
                )
            )

        return zip(*sorted(six.iteritems(consistency_group._info)))


class DeleteConsistencyGroup(command.Command):
    _description = _("Delete consistency group(s).")

    def get_parser(self, prog_name):
        parser = super(DeleteConsistencyGroup, self).get_parser(prog_name)
        parser.add_argument(
            'consistency_groups',
            metavar='<consistency-group>',
            nargs="+",
            help=_('Consistency group(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_("Allow delete in state other than error or available"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result = 0

        for i in parsed_args.consistency_groups:
            try:
                consistency_group_id = utils.find_resource(
                    volume_client.consistencygroups, i).id
                volume_client.consistencygroups.delete(
                    consistency_group_id, parsed_args.force)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete consistency group with "
                            "name or ID '%(consistency_group)s':%(e)s")
                          % {'consistency_group': i, 'e': e})

        if result > 0:
            total = len(parsed_args.consistency_groups)
            msg = (_("%(result)s of %(total)s consistency groups failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListConsistencyGroup(command.Lister):
    _description = _("List consistency groups.")

    def get_parser(self, prog_name):
        parser = super(ListConsistencyGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action="store_true",
            help=_('Show details for all projects. Admin only. '
                   '(defaults to False)')
        )
        parser.add_argument(
            '--long',
            action="store_true",
            help=_('List additional fields in output')
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.long:
            columns = ['ID', 'Status', 'Availability Zone',
                       'Name', 'Description', 'Volume Types']
        else:
            columns = ['ID', 'Status', 'Name']
        volume_client = self.app.client_manager.volume
        consistency_groups = volume_client.consistencygroups.list(
            detailed=True,
            search_opts={'all_tenants': parsed_args.all_projects}
        )

        return (columns, (
            utils.get_item_properties(
                s, columns,
                formatters={'Volume Types': format_columns.ListColumn})
            for s in consistency_groups))


class RemoveVolumeFromConsistencyGroup(command.Command):
    _description = _("Remove volume(s) from consistency group")

    def get_parser(self, prog_name):
        parser = \
            super(RemoveVolumeFromConsistencyGroup, self).get_parser(prog_name)
        parser.add_argument(
            'consistency_group',
            metavar="<consistency-group>",
            help=_('Consistency group containing <volume> (name or ID)'),
        )
        parser.add_argument(
            'volumes',
            metavar='<volume>',
            nargs='+',
            help=_('Volume(s) to remove from <consistency-group> (name or ID) '
                   '(repeat option to remove multiple volumes)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result, remove_uuid = _find_volumes(parsed_args.volumes, volume_client)

        if result > 0:
            total = len(parsed_args.volumes)
            LOG.error(_("%(result)s of %(total)s volumes failed "
                      "to remove.") % {'result': result, 'total': total})

        if remove_uuid:
            remove_uuid = remove_uuid.rstrip(',')
            consistency_group_id = utils.find_resource(
                volume_client.consistencygroups,
                parsed_args.consistency_group).id
            volume_client.consistencygroups.update(
                consistency_group_id, remove_volumes=remove_uuid)


class SetConsistencyGroup(command.Command):
    _description = _("Set consistency group properties")

    def get_parser(self, prog_name):
        parser = super(SetConsistencyGroup, self).get_parser(prog_name)
        parser.add_argument(
            'consistency_group',
            metavar='<consistency-group>',
            help=_('Consistency group to modify (name or ID)')
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New consistency group name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New consistency group description'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if kwargs:
            consistency_group_id = utils.find_resource(
                volume_client.consistencygroups,
                parsed_args.consistency_group).id
            volume_client.consistencygroups.update(
                consistency_group_id, **kwargs)


class ShowConsistencyGroup(command.ShowOne):
    _description = _("Display consistency group details.")

    def get_parser(self, prog_name):
        parser = super(ShowConsistencyGroup, self).get_parser(prog_name)
        parser.add_argument(
            "consistency_group",
            metavar="<consistency-group>",
            help=_("Consistency group to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        consistency_group = utils.find_resource(
            volume_client.consistencygroups,
            parsed_args.consistency_group)
        return zip(*sorted(six.iteritems(consistency_group._info)))
