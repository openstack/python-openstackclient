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

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)


class CreateVolumeType(command.ShowOne):
    """Create new volume type"""

    def get_parser(self, prog_name):
        parser = super(CreateVolumeType, self).get_parser(prog_name)
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
            default=False,
            help=_("Volume type is accessible to the public"),
        )
        public_group.add_argument(
            "--private",
            action="store_true",
            default=False,
            help=_("Volume type is not accessible to the public"),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this volume type '
                   '(repeat option to set multiple properties)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Allow <project> to access private type (name or ID) "
                   "(Must be used with --private option)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        volume_client = self.app.client_manager.volume

        if parsed_args.project and not parsed_args.private:
            msg = _("--project is only allowed with --private")
            raise exceptions.CommandError(msg)

        kwargs = {}
        if parsed_args.public:
            kwargs['is_public'] = True
        if parsed_args.private:
            kwargs['is_public'] = False

        volume_type = volume_client.volume_types.create(
            parsed_args.name,
            description=parsed_args.description,
            **kwargs
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
                    volume_type.id, project_id)
            except Exception as e:
                msg = _("Failed to add project %(project)s access to "
                        "type: %(e)s")
                LOG.error(msg % {'project': parsed_args.project, 'e': e})
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
            "volume_types",
            metavar="<volume-type>",
            nargs="+",
            help=_("Volume type(s) to delete (name or ID)")
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
            help=_('List additional fields in output'))
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            action="store_true",
            help=_("List only public types")
        )
        public_group.add_argument(
            "--private",
            action="store_true",
            help=_("List only private types (admin only)")
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.long:
            columns = ['ID', 'Name', 'Description', 'Extra Specs']
            column_headers = ['ID', 'Name', 'Description', 'Properties']
        else:
            columns = ['ID', 'Name']
            column_headers = columns

        is_public = None
        if parsed_args.public:
            is_public = True
        if parsed_args.private:
            is_public = False
        data = self.app.client_manager.volume.volume_types.list(
            is_public=is_public)
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
            '--name',
            metavar='<name>',
            help=_('Set volume type name'),
        )
        parser.add_argument(
            '--description',
            metavar='<name>',
            help=_('Set volume type description'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this volume type '
                   '(repeat option to set multiple properties)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Set volume type access to project (name or ID) '
                   '(admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        identity_client = self.app.client_manager.identity

        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type)

        result = 0
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if kwargs:
            try:
                volume_client.volume_types.update(
                    volume_type.id,
                    **kwargs
                )
            except Exception as e:
                LOG.error(_("Failed to update volume type name or"
                            " description: %s"), e)
                result += 1

        if parsed_args.property:
            try:
                volume_type.set_keys(parsed_args.property)
            except Exception as e:
                LOG.error(_("Failed to set volume type property: %s"), e)
                result += 1

        if parsed_args.project:
            project_info = None
            try:
                project_info = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain)

                volume_client.volume_type_access.add_project_access(
                    volume_type.id, project_info.id)
            except Exception as e:
                LOG.error(_("Failed to set volume type access to "
                            "project: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("Command Failed: One or more of"
                                            " the operations failed"))


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
        properties = utils.format_dict(
            volume_type._info.pop('extra_specs', {}))
        volume_type._info.update({'properties': properties})
        access_project_ids = None
        if not volume_type.is_public:
            try:
                volume_type_access = volume_client.volume_type_access.list(
                    volume_type.id)
                project_ids = [utils.get_field(item, 'project_id')
                               for item in volume_type_access]
                # TODO(Rui Chen): This format list case can be removed after
                # patch https://review.openstack.org/#/c/330223/ merged.
                access_project_ids = utils.format_list(project_ids)
            except Exception as e:
                msg = _('Failed to get access project list for volume type '
                        '%(type)s: %(e)s')
                LOG.error(msg % {'type': volume_type.id, 'e': e})
        volume_type._info.update({'access_project_ids': access_project_ids})
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
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Removes volume type access to project (name or ID) '
                   ' (admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        identity_client = self.app.client_manager.identity

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

        if parsed_args.project:
            project_info = None
            try:
                project_info = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain)

                volume_client.volume_type_access.remove_project_access(
                    volume_type.id, project_info.id)
            except Exception as e:
                LOG.error(_("Failed to remove volume type access from "
                            "project: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("Command Failed: One or more of"
                                          " the operations failed"))
