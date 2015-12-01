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

import copy
import mock
import uuid

from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.image.v2 import fakes as image_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils
from openstackclient.tests.volume.v2 import fakes as volume_fakes


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

floating_ip_num = 100
fix_ip_num = 100
injected_file_num = 100
injected_file_size_num = 10240
injected_path_size_num = 255
key_pair_num = 100
core_num = 20
ram_num = 51200
instance_num = 10
property_num = 128
secgroup_rule_num = 20
secgroup_num = 10
project_name = 'project_test'
QUOTA = {
    'project': project_name,
    'floating-ips': floating_ip_num,
    'fix-ips': fix_ip_num,
    'injected-files': injected_file_num,
    'injected-file-size': injected_file_size_num,
    'injected-path-size': injected_path_size_num,
    'key-pairs': key_pair_num,
    'cores': core_num,
    'ram': ram_num,
    'instances': instance_num,
    'properties': property_num,
    'secgroup_rules': secgroup_rule_num,
    'secgroups': secgroup_num,
}

QUOTA_columns = tuple(sorted(QUOTA))
QUOTA_data = tuple(QUOTA[x] for x in sorted(QUOTA))

block_device_mapping = 'vda=' + volume_fakes.volume_name + ':::0'

service_host = 'host_test'
service_binary = 'compute_test'
service_status = 'enabled'
SERVICE = {
    'host': service_host,
    'binary': service_binary,
    'status': service_status,
}


class FakeComputev2Client(object):
    def __init__(self, **kwargs):
        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})
        self.servers = mock.Mock()
        self.servers.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})
        self.flavors = mock.Mock()
        self.flavors.resource_class = fakes.FakeResource(None, {})
        self.quotas = mock.Mock()
        self.quotas.resource_class = fakes.FakeResource(None, {})
        self.quota_classes = mock.Mock()
        self.quota_classes.resource_class = fakes.FakeResource(None, {})
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})
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

        self.app.client_manager.volume = volume_fakes.FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


class FakeServer(object):
    """Fake one or more compute servers."""

    @staticmethod
    def create_one_server(attrs={}, methods={}):
        """Create a fake server.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, metadata
        """
        # Set default attributes.
        server_info = {
            'id': 'server-id-' + uuid.uuid4().hex,
            'name': 'server-name-' + uuid.uuid4().hex,
            'metadata': {},
        }

        # Overwrite default attributes.
        server_info.update(attrs)

        server = fakes.FakeResource(info=copy.deepcopy(server_info),
                                    methods=methods,
                                    loaded=True)
        return server

    @staticmethod
    def create_servers(attrs={}, methods={}, count=2):
        """Create multiple fake servers.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of servers to fake
        :return:
            A list of FakeResource objects faking the servers
        """
        servers = []
        for i in range(0, count):
            servers.append(FakeServer.create_one_server(attrs, methods))

        return servers

    @staticmethod
    def get_servers(servers=None, count=2):
        """Get an iterable MagicMock object with a list of faked servers.

        If servers list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List servers:
            A list of FakeResource objects faking servers
        :param int count:
            The number of servers to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            servers
        """
        if servers is None:
            servers = FakeServer.create_servers(count)
        return mock.MagicMock(side_effect=servers)


class FakeFlavorResource(fakes.FakeResource):
    """Fake flavor object's methods to help test.

    The flavor object has three methods to get, set, unset its properties.
    Need to fake them, otherwise the functions to be tested won't run properly.
    """

    # Fake properties.
    _keys = {'property': 'value'}

    def set_keys(self, args):
        self._keys.update(args)

    def unset_keys(self, keys):
        for key in keys:
            self._keys.pop(key, None)

    def get_keys(self):
        return self._keys


class FakeFlavor(object):
    """Fake one or more flavors."""

    @staticmethod
    def create_one_flavor(attrs={}):
        """Create a fake flavor.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeFlavorResource object, with id, name, ram, vcpus, properties
        """
        # Set default attributes.
        flavor_info = {
            'id': 'flavor-id-' + uuid.uuid4().hex,
            'name': 'flavor-name-' + uuid.uuid4().hex,
            'ram': 8192,
            'vcpus': 4,
        }

        # Overwrite default attributes.
        flavor_info.update(attrs)

        flavor = FakeFlavorResource(info=copy.deepcopy(flavor_info),
                                    loaded=True)
        return flavor

    @staticmethod
    def create_flavors(attrs={}, count=2):
        """Create multiple fake flavors.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of flavors to fake
        :return:
            A list of FakeFlavorResource objects faking the flavors
        """
        flavors = []
        for i in range(0, count):
            flavors.append(FakeFlavor.create_one_flavor(attrs))

        return flavors

    @staticmethod
    def get_flavors(flavors=None, count=2):
        """Get an iterable MagicMock object with a list of faked flavors.

        If flavors list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List flavors:
            A list of FakeFlavorResource objects faking flavors
        :param int count:
            The number of flavors to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            flavors
        """
        if flavors is None:
            flavors = FakeServer.create_flavors(count)
        return mock.MagicMock(side_effect=flavors)
