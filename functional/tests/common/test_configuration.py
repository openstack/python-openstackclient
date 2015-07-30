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

from functional.common import test
from openstackclient.common import configuration


BASIC_CONFIG_HEADERS = ['Field', 'Value']


class ConfigurationTests(test.TestCase):

    opts = "-f value -c auth.password"

    def test_configuration_show(self):
        raw_output = self.openstack('configuration show')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_CONFIG_HEADERS)

    def test_configuration_show_unmask(self):
        raw_output = self.openstack('configuration show --unmask ' + self.opts)
        passwd = os.environ['OS_PASSWORD']
        self.assertOutput(passwd + '\n', raw_output)

    def test_configuration_show_mask(self):
        raw_output = self.openstack('configuration show --mask ' + self.opts)
        self.assertOutput(configuration.REDACTED + '\n', raw_output)
