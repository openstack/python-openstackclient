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

import hashlib

from openstackclient.tests.functional import base


class ComputeAgentTests(base.TestCase):
    """Functional tests for compute agent."""

    ID = None
    MD5HASH = hashlib.md5().hexdigest()
    URL = "http://localhost"
    VER = "v1"
    OS = "TEST_OS"
    ARCH = "x86_64"
    HYPER = "kvm"

    HEADERS = ['agent_id', 'md5hash']
    FIELDS = ['agent_id', 'md5hash']

    @classmethod
    def setUpClass(cls):
        opts = cls.get_opts(cls.HEADERS)
        raw_output = cls.openstack('compute agent create ' +
                                   cls.OS + ' ' + cls.ARCH + ' ' +
                                   cls.VER + ' ' + cls.URL + ' ' +
                                   cls.MD5HASH + ' ' + cls.HYPER + ' ' +
                                   opts)

        # Get agent id because agent can only be deleted by ID
        output_list = raw_output.split('\n', 1)
        cls.ID = output_list[0]

        cls.assertOutput(cls.MD5HASH + '\n', output_list[1])

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('compute agent delete ' + cls.ID)
        cls.assertOutput('', raw_output)

    def test_agent_list(self):
        raw_output = self.openstack('compute agent list')
        self.assertIn(self.ID, raw_output)
        self.assertIn(self.OS, raw_output)
        self.assertIn(self.ARCH, raw_output)
        self.assertIn(self.VER, raw_output)
        self.assertIn(self.URL, raw_output)
        self.assertIn(self.MD5HASH, raw_output)
        self.assertIn(self.HYPER, raw_output)

    def test_agent_set(self):
        ver = 'v2'
        url = "http://openstack"
        md5hash = hashlib.md5().hexdigest()

        self.openstack('compute agent set '
                       + self.ID
                       + ' --agent-version ' + ver
                       + ' --url ' + url
                       + ' --md5hash ' + md5hash)

        raw_output = self.openstack('compute agent list')
        self.assertIn(self.ID, raw_output)
        self.assertIn(ver, raw_output)
        self.assertIn(url, raw_output)
        self.assertIn(md5hash, raw_output)
