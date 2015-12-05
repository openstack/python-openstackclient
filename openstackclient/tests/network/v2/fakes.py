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

import argparse
import mock

from openstackclient.api import network_v2
from openstackclient.tests import fakes
from openstackclient.tests import utils

extension_name = 'Matrix'
extension_namespace = 'http://docs.openstack.org/network/'
extension_description = 'Simulated reality'
extension_updated = '2013-07-09T12:00:0-00:00'
extension_alias = 'Dystopian'
extension_links = '[{"href":''"https://github.com/os/network", "type"}]'

NETEXT = {
    'name': extension_name,
    'namespace': extension_namespace,
    'description': extension_description,
    'updated': extension_updated,
    'alias': extension_alias,
    'links': extension_links,
}


class FakeNetworkV2Client(object):
    def __init__(self, **kwargs):
        self.list_extensions = mock.Mock(return_value={'extensions': [NETEXT]})


class TestNetworkV2(utils.TestCommand):
    def setUp(self):
        super(TestNetworkV2, self).setUp()

        self.namespace = argparse.Namespace()

        self.app.client_manager.network = FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.network.api = network_v2.APIv2(
            session=mock.Mock(),
            service_type="network",
        )
