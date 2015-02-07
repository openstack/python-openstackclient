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

"""Network v2 API Library"""

from openstackclient.api import api


class APIv2(api.BaseAPI):
    """Network v2 API"""

    def __init__(self, **kwargs):
        super(APIv2, self).__init__(**kwargs)

    def dhcp_agent_list(
        self,
        dhcp_id=None,
        **filter
    ):
        """List DHCP agents

        :param string dhcp_id:
            DHCP Agent ID
        :param filter:
            used to create the query string filters
            http://docs.openstack.org/api/openstack-network/2.0/content/filtering.html
        """

        return self.list('dhcp-networks', **filter)['dhcp-networks']

    def network_list(
        self,
        external=False,
        **filter
    ):
        """List external networks

        :param string dhcp_id:
            DHCP agent ID
        :param bool external:
            Return external networks if True
        :param filter:
            used to create the query string filters
            http://docs.openstack.org/api/openstack-network/2.0/content/filtering.html
        """

        if external:
            filter = {'router:external': True}
        return self.list('networks', **filter)['networks']
