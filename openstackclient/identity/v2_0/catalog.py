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

"""Identity v2 Service Catalog action implementations"""

import logging

from cliff import columns as cliff_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class EndpointsColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        if not self._value:
            return ""
        ret = ''
        for ep in self._value:
            region = ep.get('region')
            if region is None:
                region = '<none>'
            ret += region + '\n'
            for endpoint_type in ['publicURL', 'internalURL', 'adminURL']:
                url = ep.get(endpoint_type)
                if url:
                    ret += "  %s: %s\n" % (endpoint_type, url)
        return ret


class ListCatalog(command.Lister):
    _description = _("List services in the service catalog")

    def take_action(self, parsed_args):

        # Trigger auth if it has not happened yet
        auth_ref = self.app.client_manager.auth_ref
        if not auth_ref:
            raise exceptions.AuthorizationFailure(
                "Only an authorized user may issue a new token."
            )

        data = auth_ref.service_catalog.catalog
        columns = ('Name', 'Type', 'Endpoints')
        return (columns,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={
                        'Endpoints': EndpointsColumn,
                    },
                ) for s in data))


class ShowCatalog(command.ShowOne):
    _description = _("Display service catalog details")

    def get_parser(self, prog_name):
        parser = super(ShowCatalog, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help=_('Service to display (type or name)'),
        )
        return parser

    def take_action(self, parsed_args):

        # Trigger auth if it has not happened yet
        auth_ref = self.app.client_manager.auth_ref
        if not auth_ref:
            raise exceptions.AuthorizationFailure(
                "Only an authorized user may issue a new token."
            )

        data = None
        for service in auth_ref.service_catalog.catalog:
            if (service.get('name') == parsed_args.service or
                    service.get('type') == parsed_args.service):
                data = service
                data['endpoints'] = EndpointsColumn(data['endpoints'])
                if 'endpoints_links' in data:
                    data.pop('endpoints_links')
                break

        if not data:
            LOG.error(_('service %s not found\n'), parsed_args.service)
            return ((), ())

        return zip(*sorted(six.iteritems(data)))
