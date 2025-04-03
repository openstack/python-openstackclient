#   Copyright 2013 OpenStack Foundation
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

"""Agent action implementations"""

import logging

from openstack import exceptions as sdk_exceptions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateAgent(command.ShowOne):
    """Create compute agent.

    The compute agent functionality is hypervisor specific and is only
    supported by the XenAPI hypervisor driver. It was removed from nova in the
    23.0.0 (Wallaby) release.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument("os", metavar="<os>", help=_("Type of OS"))
        parser.add_argument(
            "architecture",
            metavar="<architecture>",
            help=_("Type of architecture"),
        )
        parser.add_argument("version", metavar="<version>", help=_("Version"))
        parser.add_argument("url", metavar="<url>", help=_("URL"))
        parser.add_argument("md5hash", metavar="<md5hash>", help=_("MD5 hash"))
        parser.add_argument(
            "hypervisor",
            metavar="<hypervisor>",
            default="xen",
            help=_("Type of hypervisor"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        # doing this since openstacksdk has decided not to support this
        # deprecated command
        data = {
            'agent': {
                'hypervisor': parsed_args.hypervisor,
                'os': parsed_args.os,
                'architecture': parsed_args.architecture,
                'version': parsed_args.version,
                'url': parsed_args.url,
                'md5hash': parsed_args.md5hash,
            },
        }
        response = compute_client.post(
            '/os-agents', json=data, microversion='2.1'
        )
        sdk_exceptions.raise_from_response(response)
        agent = response.json().get('agent')

        return zip(*sorted(agent.items()))


class DeleteAgent(command.Command):
    """Delete compute agent(s).

    The compute agent functionality is hypervisor specific and is only
    supported by the XenAPI hypervisor driver. It was removed from nova in the
    23.0.0 (Wallaby) release.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "id", metavar="<id>", nargs='+', help=_("ID of agent(s) to delete")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for id in parsed_args.id:
            try:
                # doing this since openstacksdk has decided not to support this
                # deprecated command
                response = compute_client.delete(
                    f'/os-agents/{id}', microversion='2.1'
                )
                sdk_exceptions.raise_from_response(response)
            except Exception as e:
                result += 1
                LOG.error(
                    _("Failed to delete agent with ID '%(id)s': %(e)s"),
                    {'id': id, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.id)
            msg = _("%(result)s of %(total)s agents failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListAgent(command.Lister):
    """List compute agents.

    The compute agent functionality is hypervisor specific and is only
    supported by the XenAPI hypervisor driver. It was removed from nova in the
    23.0.0 (Wallaby) release.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--hypervisor",
            metavar="<hypervisor>",
            help=_("Type of hypervisor"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        columns = (
            "Agent ID",
            "Hypervisor",
            "OS",
            "Architecture",
            "Version",
            "Md5Hash",
            "URL",
        )

        # doing this since openstacksdk has decided not to support this
        # deprecated command
        path = '/os-agents'
        if parsed_args.hypervisor:
            path += f'?hypervisor={parsed_args.hypervisor}'

        response = compute_client.get(path, microversion='2.1')
        sdk_exceptions.raise_from_response(response)
        agents = response.json().get('agents')

        return columns, (utils.get_dict_properties(s, columns) for s in agents)


class SetAgent(command.Command):
    """Set compute agent properties.

    The compute agent functionality is hypervisor-specific and is only
    supported by the XenAPI hypervisor driver. It was removed from nova in the
    23.0.0 (Wallaby) release.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "id",
            metavar="<id>",
            type=int,
            help=_("ID of the agent"),
        )
        parser.add_argument(
            "--agent-version",
            dest="version",
            metavar="<version>",
            help=_("Version of the agent"),
        )
        parser.add_argument(
            "--url", metavar="<url>", help=_("URL of the agent")
        )
        parser.add_argument(
            "--md5hash", metavar="<md5hash>", help=_("MD5 hash of the agent")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        response = compute_client.get('/os-agents', microversion='2.1')
        sdk_exceptions.raise_from_response(response)
        agents = response.json().get('agents')
        data = {}
        for agent in agents:
            if agent['agent_id'] == parsed_args.id:
                data['version'] = agent['version']
                data['url'] = agent['url']
                data['md5hash'] = agent['md5hash']
                break
        else:
            msg = _("No agent with a ID of '%(id)s' exists.")
            raise exceptions.CommandError(msg % {'id': parsed_args.id})

        if parsed_args.version:
            data['version'] = parsed_args.version
        if parsed_args.url:
            data['url'] = parsed_args.url
        if parsed_args.md5hash:
            data['md5hash'] = parsed_args.md5hash

        data = {'para': data}

        # doing this since openstacksdk has decided not to support this
        # deprecated command
        response = compute_client.put(
            f'/os-agents/{parsed_args.id}', json=data, microversion='2.1'
        )
        sdk_exceptions.raise_from_response(response)
