# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import random
from unittest import mock
import uuid

from cinderclient import api_versions

from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_v2_fakes


class FakeVolumeClient(object):

    def __init__(self, **kwargs):
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']
        self.api_version = api_versions.APIVersion('3.0')

        self.attachments = mock.Mock()
        self.attachments.resource_class = fakes.FakeResource(None, {})
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})


class TestVolume(utils.TestCommand):

    def setUp(self):
        super().setUp()

        self.app.client_manager.volume = FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )
        self.app.client_manager.identity = identity_fakes.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )
        self.app.client_manager.compute = compute_fakes.FakeComputev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


# TODO(stephenfin): Check if the responses are actually the same
FakeVolume = volume_v2_fakes.FakeVolume


class FakeVolumeAttachment:
    """Fake one or more volume attachments."""

    @staticmethod
    def create_one_volume_attachment(attrs=None):
        """Create a fake volume attachment.

        :param attrs: A dictionary with all attributes of volume attachment
        :return: A FakeResource object with id, status, etc.
        """
        attrs = attrs or {}

        attachment_id = uuid.uuid4().hex
        volume_id = attrs.pop('volume_id', None) or uuid.uuid4().hex
        server_id = attrs.pop('instance', None) or uuid.uuid4().hex

        # Set default attribute
        attachment_info = {
            'id': attachment_id,
            'volume_id': volume_id,
            'instance': server_id,
            'status': random.choice([
                'attached',
                'attaching',
                'detached',
                'reserved',
                'error_attaching',
                'error_detaching',
                'deleted',
            ]),
            'attach_mode': random.choice(['ro', 'rw']),
            'attached_at': '2015-09-16T09:28:52.000000',
            'detached_at': None,
            'connection_info': {
                'access_mode': 'rw',
                'attachment_id': attachment_id,
                'auth_method': 'CHAP',
                'auth_password': 'AcUZ8PpxLHwzypMC',
                'auth_username': '7j3EZQWT3rbE6pcSGKvK',
                'cacheable': False,
                'driver_volume_type': 'iscsi',
                'encrypted': False,
                'qos_specs': None,
                'target_discovered': False,
                'target_iqn':
                    f'iqn.2010-10.org.openstack:volume-{attachment_id}',
                'target_lun': '1',
                'target_portal': '192.168.122.170:3260',
                'volume_id': volume_id,
            },
        }

        # Overwrite default attributes if there are some attributes set
        attachment_info.update(attrs)

        attachment = fakes.FakeResource(
            None,
            attachment_info,
            loaded=True)
        return attachment

    @staticmethod
    def create_volume_attachments(attrs=None, count=2):
        """Create multiple fake volume attachments.

        :param attrs: A dictionary with all attributes of volume attachment
        :param count: The number of volume attachments to be faked
        :return: A list of FakeResource objects
        """
        attachments = []

        for n in range(0, count):
            attachments.append(
                FakeVolumeAttachment.create_one_volume_attachment(attrs))

        return attachments

    @staticmethod
    def get_volume_attachments(attachments=None, count=2):
        """Get an iterable MagicMock object with a list of faked volumes.

        If attachments list is provided, then initialize the Mock object with
        the list. Otherwise create one.

        :param attachments: A list of FakeResource objects faking volume
            attachments
        :param count: The number of volume attachments to be faked
        :return An iterable Mock object with side_effect set to a list of faked
            volume attachments
        """
        if attachments is None:
            attachments = FakeVolumeAttachment.create_volume_attachments(count)

        return mock.Mock(side_effect=attachments)
