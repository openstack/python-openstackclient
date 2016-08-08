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

import uuid

from openstackclient.tests.functional.volume.v1 import common


class TransferRequestTests(common.BaseVolumeTests):
    """Functional tests for transfer request. """

    NAME = uuid.uuid4().hex
    VOLUME_NAME = uuid.uuid4().hex
    HEADERS = ['Name']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        super(TransferRequestTests, cls).setUpClass()
        opts = cls.get_opts(['display_name'])
        raw_output = cls.openstack(
            'volume create --size 1 ' + cls.VOLUME_NAME + opts)
        cls.assertOutput(cls.VOLUME_NAME + '\n', raw_output)

        opts = cls.get_opts(cls.FIELDS)
        raw_output = cls.openstack(
            'volume transfer request create ' +
            cls.VOLUME_NAME +
            ' --name ' + cls.NAME + opts)
        cls.assertOutput(cls.NAME + '\n', raw_output)

    @classmethod
    def tearDownClass(cls):
        raw_output_transfer = cls.openstack(
            'volume transfer request delete ' + cls.NAME)
        raw_output_volume = cls.openstack(
            'volume delete ' + cls.VOLUME_NAME)
        cls.assertOutput('', raw_output_transfer)
        cls.assertOutput('', raw_output_volume)

    def test_volume_transfer_request_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('volume transfer request list' + opts)
        self.assertIn(self.NAME, raw_output)
