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

import os

from openstackclient.common import configuration
from openstackclient.tests.functional import base


BASIC_CONFIG_HEADERS = ['Field', 'Value']


class ConfigurationTests(base.TestCase):

    opts = "-f value -c auth.password"

    def test_configuration_show(self):
        raw_output = self.openstack('configuration show')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_CONFIG_HEADERS)

    def test_configuration_show_unmask(self):
        raw_output = self.openstack('configuration show --unmask ' + self.opts)
        # If we are using os-client-config, this will not be set.  Rather than
        # parse clouds.yaml to get the right value, just make sure
        # we are not getting redacted.
        passwd = os.environ.get('OS_PASSWORD')
        if passwd:
            self.assertEqual(passwd + '\n', raw_output)
        else:
            self.assertNotEqual(configuration.REDACTED + '\n', raw_output)

    def test_configuration_show_mask(self):
        raw_output = self.openstack('configuration show --mask ' + self.opts)
        self.assertEqual(configuration.REDACTED + '\n', raw_output)
