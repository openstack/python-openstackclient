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

from openstackclient.tests.functional import base


class ObjectStoreTests(base.TestCase):
    """Functional tests for Object Store commands"""

    @classmethod
    def setUpClass(cls):
        super(ObjectStoreTests, cls).setUpClass()
        cls.haz_object_store = cls.is_service_enabled('object-store')
