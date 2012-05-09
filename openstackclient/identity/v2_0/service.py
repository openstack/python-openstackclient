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


def get_service_properties(service, fields, formatters={}):
    """Return a tuple containing the service properties.

    :param server: a single Service resource
    :param fields: tuple of strings with the desired field names
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []
    mixed_case_fields = []

    for field in fields:
        if field in formatters:
            row.append(formatters[field](service))
        else:
            if field in mixed_case_fields:
                field_name = field.replace(' ', '_')
            else:
                field_name = field.lower().replace(' ', '_')
            data = getattr(service, field_name, '')
            row.append(data)
    return tuple(row)


class Create_Service(command.OpenStackCommand):
    "Create service command."

    api = 'identity'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Create_Service, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
        return parser

    def run(self, parsed_args):
        self.log.info('v2.Create_Service.run(%s)' % parsed_args)


class List_Service(command.OpenStackCommand, lister.Lister):
    "List service command."

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
        self.log.debug('v2.List_Service.run(%s)' % parsed_args)
        if parsed_args.long:
            columns = ('ID', 'Name', 'Type', 'Description')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.identity.services.list()
        print "data: %s" % data
        return (columns,
                (get_service_properties(
                    s, columns,
                    formatters={},
                    ) for s in data),
                )

    #def run(self, parsed_args):
    #    self.log.info('v2.List_Service.run(%s)' % parsed_args)


class Show_Service(command.OpenStackCommand):
    "Show service command."

    api = 'identity'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Show_Service, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
        return parser

    def run(self, parsed_args):
        self.log.info('v2.Show_Service.run(%s)' % parsed_args)
