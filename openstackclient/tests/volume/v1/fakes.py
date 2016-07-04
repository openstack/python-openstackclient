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
from openstackclient.tests import utils


volume_id = 'vvvvvvvv-vvvv-vvvv-vvvvvvvv'
volume_name = 'nigel'
volume_description = 'Nigel Tufnel'
volume_status = 'available'
volume_size = 120
volume_type = 'to-eleven'
volume_zone = 'stonehenge'
volume_metadata = {
    'Alpha': 'a',
    'Beta': 'b',
    'Gamma': 'g',
}
volume_metadata_str = "Alpha='a', Beta='b', Gamma='g'"

VOLUME = {
    'id': volume_id,
    'display_name': volume_name,
    'display_description': volume_description,
    'size': volume_size,
    'status': volume_status,
    'attach_status': 'detached',
    'availability_zone': volume_zone,
    'volume_type': volume_type,
    'metadata': volume_metadata,
}

extension_name = 'SchedulerHints'
extension_namespace = 'http://docs.openstack.org/'\
    'block-service/ext/scheduler-hints/api/v2'
extension_description = 'Pass arbitrary key/value'\
    'pairs to the scheduler.'
extension_updated = '2014-02-07T12:00:0-00:00'
extension_alias = 'OS-SCH-HNT'
extension_links = '[{"href":'\
    '"https://github.com/openstack/block-api", "type":'\
    ' "text/html", "rel": "describedby"}]'

EXTENSION = {
    'name': extension_name,
    'namespace': extension_namespace,
    'description': extension_description,
    'updated': extension_updated,
    'alias': extension_alias,
    'links': extension_links,
}

# NOTE(dtroyer): duplicating here the minimum image info needed to test
#                volume create --image until circular references can be
#                avoided by refactoring the test fakes.

image_id = 'im1'
image_name = 'graven'


IMAGE = {
    'id': image_id,
    'name': image_name,
}

type_id = "5520dc9e-6f9b-4378-a719-729911c0f407"
type_name = "fake-lvmdriver-1"

TYPE = {
    'id': type_id,
    'name': type_name
}

qos_id = '6f2be1de-997b-4230-b76c-a3633b59e8fb'
qos_consumer = 'front-end'
qos_default_consumer = 'both'
qos_name = "fake-qos-specs"
qos_specs = {
    'foo': 'bar',
    'iops': '9001'
}
qos_association = {
    'association_type': 'volume_type',
    'name': type_name,
    'id': type_id
}

QOS = {
    'id': qos_id,
    'consumer': qos_consumer,
    'name': qos_name
}

QOS_DEFAULT_CONSUMER = {
    'id': qos_id,
    'consumer': qos_default_consumer,
    'name': qos_name
}

QOS_WITH_SPECS = {
    'id': qos_id,
    'consumer': qos_consumer,
    'name': qos_name,
    'specs': qos_specs
}

QOS_WITH_ASSOCIATIONS = {
    'id': qos_id,
    'consumer': qos_consumer,
    'name': qos_name,
    'specs': qos_specs,
    'associations': [qos_association]
}


class FakeTransferClient(object):

    def __init__(self, **kwargs):

        self.transfers = mock.Mock()
        self.transfers.resource_class = fakes.FakeResource(None, {})


class TestTransfer(utils.TestCommand):

    def setUp(self):
        super(TestTransfer, self).setUp()

        self.app.client_manager.volume = FakeTransferClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )


class FakeTransfer(object):
    """Fake one or more Transfer."""

    @staticmethod
    def create_one_transfer(attrs=None):
        """Create a fake transfer.

        :param Dictionary attrs:
            A dictionary with all attributes of Transfer Request
        :return:
            A FakeResource object with volume_id, name, id.
        """
        # Set default attribute
        transfer_info = {
            'volume_id': 'ce26708d-a7f8-4b4b-9861-4a80256615a7',
            'name': 'fake_transfer_name',
            'id': '731a7f53-aa92-4fbd-9de3-6f7d729c926b'
        }

        # Overwrite default attributes if there are some attributes set
        attrs = attrs or {}

        transfer_info.update(attrs)

        transfer = fakes.FakeResource(
            None,
            transfer_info,
            loaded=True)

        return transfer


class FakeServiceClient(object):

    def __init__(self, **kwargs):
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})


class TestService(utils.TestCommand):

    def setUp(self):
        super(TestService, self).setUp()

        self.app.client_manager.volume = FakeServiceClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )


class FakeService(object):
    """Fake one or more Services."""

    @staticmethod
    def create_one_service(attrs=None):
        """Create a fake service.

        :param Dictionary attrs:
            A dictionary with all attributes of service
        :return:
            A FakeResource object with host, status, etc.
        """
        # Set default attribute
        service_info = {
            'host': 'host_test',
            'binary': 'cinder_test',
            'status': 'enabled',
            'disabled_reason': 'LongHoliday-GoldenWeek',
            'zone': 'fake_zone',
            'updated_at': 'fake_date',
            'state': 'fake_state',
        }

        # Overwrite default attributes if there are some attributes set
        attrs = attrs or {}

        service_info.update(attrs)

        service = fakes.FakeResource(
            None,
            service_info,
            loaded=True)

        return service

    @staticmethod
    def create_services(attrs=None, count=2):
        """Create multiple fake services.

        :param Dictionary attrs:
            A dictionary with all attributes of service
        :param Integer count:
            The number of services to be faked
        :return:
            A list of FakeResource objects
        """
        services = []
        for n in range(0, count):
            services.append(FakeService.create_one_service(attrs))

        return services

    @staticmethod
    def get_services(services=None, count=2):
        """Get an iterable MagicMock object with a list of faked services.

        If services list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List services:
            A list of FakeResource objects faking services
        :param Integer count:
            The number of services to be faked
        :return
            An iterable Mock object with side_effect set to a list of faked
            services
        """
        if services is None:
            services = FakeService.create_services(count)

        return mock.MagicMock(side_effect=services)


class FakeImagev1Client(object):

    def __init__(self, **kwargs):
        self.images = mock.Mock()


class FakeVolumev1Client(object):

    def __init__(self, **kwargs):
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})
        self.qos_specs = mock.Mock()
        self.qos_specs.resource_class = fakes.FakeResource(None, {})
        self.volume_types = mock.Mock()
        self.volume_types.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestVolumev1(utils.TestCommand):

    def setUp(self):
        super(TestVolumev1, self).setUp()

        self.app.client_manager.volume = FakeVolumev1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.identity = identity_fakes.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.image = FakeImagev1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
