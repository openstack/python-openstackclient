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

"""Identity v3 Endpoint Group action implementations"""

import json
import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class _FiltersReader(object):
    _description = _("Helper class capable of reading filters from files")

    def _read_filters(self, path):
        """Read and parse rules from path

        Expect the file to contain a valid JSON structure.

        :param path: path to the file
        :return: loaded and valid dictionary with filters
        :raises exception.CommandError: In case the file cannot be
            accessed or the content is not a valid JSON.

        Example of the content of the file:
           {
              "interface": "admin",
              "service_id": "1b501a"
           }
        """
        blob = utils.read_blob_file_contents(path)
        try:
            rules = json.loads(blob)
        except ValueError as e:
            msg = _("An error occurred when reading filters from file "
                    "%(path)s: %(error)s") % {"path": path, "error": e}
            raise exceptions.CommandError(msg)
        else:
            return rules


class AddProjectToEndpointGroup(command.Command):
    _description = _("Add a project to an endpoint group")

    def get_parser(self, prog_name):
        parser = super(
            AddProjectToEndpointGroup, self).get_parser(prog_name)
        parser.add_argument(
            'endpointgroup',
            metavar='<endpoint-group>',
            help=_('Endpoint group (name or ID)'),
        )
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Project to associate (name or ID)'),
        )
        common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.identity

        endpointgroup = utils.find_resource(client.endpoint_groups,
                                            parsed_args.endpointgroup)

        project = common.find_project(client,
                                      parsed_args.project,
                                      parsed_args.project_domain)

        client.endpoint_filter.add_endpoint_group_to_project(
            endpoint_group=endpointgroup.id,
            project=project.id)


class CreateEndpointGroup(command.ShowOne, _FiltersReader):
    _description = _("Create new endpoint group")

    def get_parser(self, prog_name):
        parser = super(CreateEndpointGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the endpoint group'),
        )
        parser.add_argument(
            'filters',
            metavar='<filename>',
            help=_('Filename that contains a new set of filters'),
        )
        parser.add_argument(
            '--description',
            help=_('Description of the endpoint group'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        filters = None
        if parsed_args.filters:
            filters = self._read_filters(parsed_args.filters)

        endpoint_group = identity_client.endpoint_groups.create(
            name=parsed_args.name,
            filters=filters,
            description=parsed_args.description
        )

        info = {}
        endpoint_group._info.pop('links')
        info.update(endpoint_group._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteEndpointGroup(command.Command):
    _description = _("Delete endpoint group(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteEndpointGroup, self).get_parser(prog_name)
        parser.add_argument(
            'endpointgroup',
            metavar='<endpoint-group>',
            nargs='+',
            help=_('Endpoint group(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.endpointgroup:
            try:
                endpoint_id = utils.find_resource(
                    identity_client.endpoint_groups, i).id
                identity_client.endpoint_groups.delete(endpoint_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete endpoint group with "
                          "ID '%(endpointgroup)s': %(e)s"),
                          {'endpointgroup': i, 'e': e})

        if result > 0:
            total = len(parsed_args.endpointgroup)
            msg = (_("%(result)s of %(total)s endpointgroups failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListEndpointGroup(command.Lister):
    _description = _("List endpoint groups")

    def get_parser(self, prog_name):
        parser = super(ListEndpointGroup, self).get_parser(prog_name)
        list_group = parser.add_mutually_exclusive_group()
        list_group.add_argument(
            '--endpointgroup',
            metavar='<endpoint-group>',
            help=_('Endpoint Group (name or ID)'),
        )
        list_group.add_argument(
            '--project',
            metavar='<project>',
            help=_('Project (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain owning <project> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.identity

        endpointgroup = None
        if parsed_args.endpointgroup:
            endpointgroup = utils.find_resource(client.endpoint_groups,
                                                parsed_args.endpointgroup)
        project = None
        if parsed_args.project:
            project = common.find_project(client,
                                          parsed_args.project,
                                          parsed_args.domain)

        if endpointgroup:
            # List projects associated to the endpoint group
            columns = ('ID', 'Name', 'Description')
            data = client.endpoint_filter.list_projects_for_endpoint_group(
                endpoint_group=endpointgroup.id)
        elif project:
            columns = ('ID', 'Name', 'Description')
            data = client.endpoint_filter.list_endpoint_groups_for_project(
                project=project.id)
        else:
            columns = ('ID', 'Name', 'Description')
            data = client.endpoint_groups.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RemoveProjectFromEndpointGroup(command.Command):
    _description = _("Remove project from endpoint group")

    def get_parser(self, prog_name):
        parser = super(
            RemoveProjectFromEndpointGroup, self).get_parser(prog_name)
        parser.add_argument(
            'endpointgroup',
            metavar='<endpoint-group>',
            help=_('Endpoint group (name or ID)'),
        )
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Project to remove (name or ID)'),
        )
        common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.identity

        endpointgroup = utils.find_resource(client.endpoint_groups,
                                            parsed_args.endpointgroup)

        project = common.find_project(client,
                                      parsed_args.project,
                                      parsed_args.project_domain)

        client.endpoint_filter.delete_endpoint_group_from_project(
            endpoint_group=endpointgroup.id,
            project=project.id)


class SetEndpointGroup(command.Command, _FiltersReader):
    _description = _("Set endpoint group properties")

    def get_parser(self, prog_name):
        parser = super(SetEndpointGroup, self).get_parser(prog_name)
        parser.add_argument(
            'endpointgroup',
            metavar='<endpoint-group>',
            help=_('Endpoint Group to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New enpoint group name'),
        )
        parser.add_argument(
            '--filters',
            metavar='<filename>',
            help=_('Filename that contains a new set of filters'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            default='',
            help=_('New endpoint group description'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        endpointgroup = utils.find_resource(identity_client.endpoint_groups,
                                            parsed_args.endpointgroup)

        filters = None
        if parsed_args.filters:
            filters = self._read_filters(parsed_args.filters)

        identity_client.endpoint_groups.update(
            endpointgroup.id,
            name=parsed_args.name,
            filters=filters,
            description=parsed_args.description
        )


class ShowEndpointGroup(command.ShowOne):
    _description = _("Display endpoint group details")

    def get_parser(self, prog_name):
        parser = super(ShowEndpointGroup, self).get_parser(prog_name)
        parser.add_argument(
            'endpointgroup',
            metavar='<endpointgroup>',
            help=_('Endpoint group (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        endpoint_group = utils.find_resource(identity_client.endpoint_groups,
                                             parsed_args.endpointgroup)

        info = {}
        endpoint_group._info.pop('links')
        info.update(endpoint_group._info)
        return zip(*sorted(six.iteritems(info)))
