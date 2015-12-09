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
import copy
import mock
import uuid

from openstackclient.api import network_v2
from openstackclient.tests import fakes
from openstackclient.tests import utils

extension_name = 'Matrix'
extension_namespace = 'http://docs.openstack.org/network/'
extension_description = 'Simulated reality'
extension_updated = '2013-07-09T12:00:0-00:00'
extension_alias = 'Dystopian'
extension_links = '[{"href":''"https://github.com/os/network", "type"}]'


def create_extension():
    extension = mock.Mock()
    extension.name = extension_name
    extension.namespace = extension_namespace
    extension.description = extension_description
    extension.updated = extension_updated
    extension.alias = extension_alias
    extension.links = extension_links
    return extension


class FakeNetworkV2Client(object):
    def __init__(self, **kwargs):
        self.extensions = mock.Mock(return_value=[create_extension()])


class TestNetworkV2(utils.TestCommand):
    def setUp(self):
        super(TestNetworkV2, self).setUp()

        self.namespace = argparse.Namespace()

        self.app.client_manager.session = mock.Mock()

        self.app.client_manager.network = FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.network.api = network_v2.APIv2(
            session=mock.Mock(),
            service_type="network",
        )


class FakeNetwork(object):
    """Fake one or more networks."""

    @staticmethod
    def create_one_network(attrs={}, methods={}):
        """Create a fake network.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, admin_state_up,
            router_external, status, subnets, tenant_id
        """
        # Set default attributes.
        network_attrs = {
            'id': 'network-id-' + uuid.uuid4().hex,
            'name': 'network-name-' + uuid.uuid4().hex,
            'status': 'ACTIVE',
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'admin_state_up': True,
            'shared': False,
            'subnets': ['a', 'b'],
            'provider_network_type': 'vlan',
            'router_external': True,
            'is_dirty': True,
        }

        # Overwrite default attributes.
        network_attrs.update(attrs)

        # Set default methods.
        network_methods = {
            'keys': ['id', 'name', 'admin_state_up', 'router_external',
                     'status', 'subnets', 'tenant_id'],
        }

        # Overwrite default methods.
        network_methods.update(methods)

        network = fakes.FakeResource(info=copy.deepcopy(network_attrs),
                                     methods=copy.deepcopy(network_methods),
                                     loaded=True)
        return network

    @staticmethod
    def create_networks(attrs={}, methods={}, count=2):
        """Create multiple fake networks.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of networks to fake
        :return:
            A list of FakeResource objects faking the networks
        """
        networks = []
        for i in range(0, count):
            networks.append(FakeNetwork.create_one_network(attrs, methods))

        return networks

    @staticmethod
    def get_networks(networks=None, count=2):
        """Get an iterable MagicMock object with a list of faked networks.

        If networks list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List networks:
            A list of FakeResource objects faking networks
        :param int count:
            The number of networks to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            networks
        """
        if networks is None:
            networks = FakeNetwork.create_networks(count)
        return mock.MagicMock(side_effect=networks)
