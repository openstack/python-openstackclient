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
import six

from cliff import lister
from cliff import show

from openstackclient.common import utils
from openstackclient.i18n import _  # noqa


def _format_endpoints(eps=None):
    if not eps:
        return ""
    ret = ''
    for index, ep in enumerate(eps):
        region = eps[index].get('region', '<none>')
        ret += region + '\n'
        for endpoint_type in ['publicURL', 'internalURL', 'adminURL']:
            url = eps[index].get(endpoint_type)
            if url:
                ret += "  %s: %s\n" % (endpoint_type, url)
    return ret


class ListCatalog(lister.Lister):
    """List services in the service catalog"""

    log = logging.getLogger(__name__ + '.ListCatalog')

    @utils.log_method(log)
    def take_action(self, parsed_args):

        # This is ugly because if auth hasn't happened yet we need
        # to trigger it here.
        sc = self.app.client_manager.session.auth.get_auth_ref(
            self.app.client_manager.session,
        ).service_catalog

        data = sc.get_data()
        columns = ('Name', 'Type', 'Endpoints')
        return (columns,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={
                        'Endpoints': _format_endpoints,
                    },
                ) for s in data))


class ShowCatalog(show.ShowOne):
    """Display service catalog details"""

    log = logging.getLogger(__name__ + '.ShowCatalog')

    def get_parser(self, prog_name):
        parser = super(ShowCatalog, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help=_('Service to display (type or name)'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        # This is ugly because if auth hasn't happened yet we need
        # to trigger it here.
        sc = self.app.client_manager.session.auth.get_auth_ref(
            self.app.client_manager.session,
        ).service_catalog

        data = None
        for service in sc.get_data():
            if (service.get('name') == parsed_args.service or
                    service.get('type') == parsed_args.service):
                data = service
                data['endpoints'] = _format_endpoints(data['endpoints'])
                if 'endpoints_links' in data:
                    data.pop('endpoints_links')
                break

        if not data:
            self.app.log.error('service %s not found\n' %
                               parsed_args.service)
            return ([], [])

        return zip(*sorted(six.iteritems(data)))
