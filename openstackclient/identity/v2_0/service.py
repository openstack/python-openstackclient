# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
Service action implementations
"""

import logging

from cliff import lister
from cliff import show

from openstackclient.common import command
from openstackclient.common import utils


class Create_Service(command.OpenStackCommand):
    """Create service command"""

    # FIXME(dtroyer): Service commands are still WIP
    api = 'identity'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Create_Service, self).get_parser(prog_name)
        parser.add_argument(
            'service_name',
            metavar='<service-name>',
            help='New service name')
        return parser

    def get_data(self, parsed_args):
        self.log.info('v2.Create_Service.get_data(%s)' % parsed_args)


class List_Service(command.OpenStackCommand, lister.Lister):
    """List service command"""

    api = 'identity'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List_Service, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
        return parser

    def get_data(self, parsed_args):
        self.log.debug('v2.List_Service.get_data(%s)' % parsed_args)
        if parsed_args.long:
            columns = ('ID', 'Name', 'Type', 'Description')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.identity.services.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                    ) for s in data),
                )


class Show_Service(command.OpenStackCommand, show.ShowOne):
    """Show service command"""

    api = 'identity'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Show_Service, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help='Name or ID of service to display')
        return parser

    def get_data(self, parsed_args):
        self.log.info('v2.Show_Service.get_data(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        service = utils.find_resource(
            identity_client.services, parsed_args.service)

        info = {}
        info.update(user._info)

        columns = sorted(info.keys())
        values = [info[c] for c in columns]
        return (columns, values)
