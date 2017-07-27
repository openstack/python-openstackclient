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

# from openstackclient.tests.functional import base
from openstackclient.tests.functional.object.v1 import common


class ContainerTests(common.ObjectStoreTests):
    """Functional tests for Object Store container commands"""
    NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super(ContainerTests, cls).setUpClass()
        if cls.haz_object_store:
            opts = cls.get_opts(['container'])
            raw_output = cls.openstack('container create ' + cls.NAME + opts)
            cls.assertOutput(cls.NAME + '\n', raw_output)

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.haz_object_store:
                raw_output = cls.openstack('container delete ' + cls.NAME)
                cls.assertOutput('', raw_output)
        finally:
            super(ContainerTests, cls).tearDownClass()

    def setUp(self):
        super(ContainerTests, self).setUp()
        # Skip tests if no object-store is present
        if not self.haz_object_store:
            self.skipTest("No object-store service present")

    def test_container_list(self):
        opts = self.get_opts(['Name'])
        raw_output = self.openstack('container list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_container_show(self):
        opts = self.get_opts(['container'])
        raw_output = self.openstack('container show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)
