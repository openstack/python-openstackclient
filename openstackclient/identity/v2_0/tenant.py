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
Tenant action implementations
"""

import logging

from cliff import lister
from cliff import show

from openstackclient.common import command
from openstackclient.common import utils


def get_tenant_properties(tenant, fields, formatters={}):
    """Return a tuple containing the server properties.

    :param server: a single Server resource
    :param fields: tuple of strings with the desired field names
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []
    mixed_case_fields = []

    for field in fields:
        if field in formatters:
            row.append(formatters[field](tenant))
        else:
            if field in mixed_case_fields:
                field_name = field.replace(' ', '_')
            else:
                field_name = field.lower().replace(' ', '_')
            data = getattr(tenant, field_name, '')
            row.append(data)
    return tuple(row)


class List_Tenant(command.OpenStackCommand, lister.Lister):
    "List tenant command."

    api = 'identity'
    log = logging.getLogger(__name__)

    def get_data(self, parsed_args):
        self.log.debug('v2.List_Service.run(%s)' % parsed_args)
        columns = ('ID', 'Name', 'Enabled')
        data = self.app.client_manager.identity.tenants.list()
        return (columns,
                (get_tenant_properties(
                    s, columns,
                    formatters={},
                    ) for s in data),
                )


class Show_Tenant(command.OpenStackCommand, show.ShowOne):
    "Show server command."

    api = 'identity'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Show_Tenant, self).get_parser(prog_name)
        parser.add_argument(
            'tenant',
            metavar='<tenant>',
            help='Name or ID of tenant to display')
        return parser

    def get_data(self, parsed_args):
        self.log.debug('v2.Show_Tenant.run(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        tenant = utils.find_resource(
            identity_client.tenants, parsed_args.tenant)

        info = {}
        info.update(tenant._info)

        # Remove a couple of values that are long and not too useful
        #info.pop('links', None)

        columns = sorted(info.keys())
        values = [info[c] for c in columns]
        return (columns, values)
