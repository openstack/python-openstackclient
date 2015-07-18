#   Copyright 2013 Nebula Inc.
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

import mock

from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.image.v2 import fakes as image_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils


server_id = 'serv1'
server_name = 'waiter'

SERVER = {
    'id': server_id,
    'name': server_name,
    'metadata': {},
}

extension_name = 'Multinic'
extension_namespace = 'http://docs.openstack.org/compute/ext/'\
    'multinic/api/v1.1'
extension_description = 'Multiple network support'
extension_updated = '2014-01-07T12:00:0-00:00'
extension_alias = 'NMN'
extension_links = '[{"href":'\
    '"https://github.com/openstack/compute-api", "type":'\
    ' "text/html", "rel": "describedby"}]'

EXTENSION = {
    'name': extension_name,
    'namespace': extension_namespace,
    'description': extension_description,
    'updated': extension_updated,
    'alias': extension_alias,
    'links': extension_links,
}

flavor_id = 'm1.large'
flavor_name = 'Large'
flavor_ram = 8192
flavor_vcpus = 4

FLAVOR = {
    'id': flavor_id,
    'name': flavor_name,
    'ram': flavor_ram,
    'vcpus': flavor_vcpus,
}

floating_ip_num = 100
fix_ip_num = 100
injected_file_num = 100
key_pair_num = 100
project_name = 'project_test'
QUOTA = {
    'project': project_name,
    'floating-ips': floating_ip_num,
    'fix-ips': fix_ip_num,
    'injected-files': injected_file_num,
    'key-pairs': key_pair_num,
}

QUOTA_columns = tuple(sorted(QUOTA))
QUOTA_data = tuple(QUOTA[x] for x in sorted(QUOTA))


class FakeComputev2Client(object):
    def __init__(self, **kwargs):
        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})
        self.servers = mock.Mock()
        self.servers.resource_class = fakes.FakeResource(None, {})
        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})
        self.flavors = mock.Mock()
        self.flavors.resource_class = fakes.FakeResource(None, {})
        self.quotas = mock.Mock()
        self.quotas.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestComputev2(utils.TestCommand):
    def setUp(self):
        super(TestComputev2, self).setUp()

        self.app.client_manager.compute = FakeComputev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.identity = identity_fakes.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.image = image_fakes.FakeImagev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.network = network_fakes.FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
