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

import fixtures

from openstackclient.tests.functional.volume import base as volume_base


class BaseVolumeTests(volume_base.BaseVolumeTests):
    """Base class for Volume functional tests"""

    @classmethod
    def setUpClass(cls):
        super(BaseVolumeTests, cls).setUpClass()
        # TODO(dtroyer): This needs to be updated to specifically check for
        #                Volume v1 rather than just 'volume', but for now
        #                that is enough until we get proper version negotiation
        cls.haz_volume_v1 = cls.is_service_enabled('volume')

    def setUp(self):
        super(BaseVolumeTests, self).setUp()

        # This class requires Volume v1
        # if not self.haz_volume_v1:
        #     self.skipTest("No Volume v1 service present")

        # TODO(dtroyer): We really want the above to work but right now
        #                (12Sep2017) DevStack still creates a 'volume'
        #                service type even though there is no service behind
        #                it.  Until that is fixed we need to just skip the
        #                volume v1 functional tests in master.
        self.skipTest("No Volume v1 service present")

        ver_fixture = fixtures.EnvironmentVariable(
            'OS_VOLUME_API_VERSION', '1'
        )
        self.useFixture(ver_fixture)
