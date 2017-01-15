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


class QuotaTests(base.TestCase):
    """Functional tests for quota. """
    # Test quota information for compute, network and volume.
    EXPECTED_FIELDS = ['instances', 'networks', 'volumes']
    EXPECTED_CLASS_FIELDS = ['instances', 'volumes']
    PROJECT_NAME = None

    @classmethod
    def setUpClass(cls):
        cls.PROJECT_NAME =\
            cls.get_openstack_configuration_value('auth.project_name')

    def test_quota_set(self):
        self.openstack('quota set --instances 11 --volumes 11 --networks 11 ' +
                       self.PROJECT_NAME)
        opts = self.get_opts(self.EXPECTED_FIELDS)
        raw_output = self.openstack('quota show ' + self.PROJECT_NAME + opts)
        self.assertEqual("11\n11\n11\n", raw_output)

    def test_quota_show(self):
        raw_output = self.openstack('quota show ' + self.PROJECT_NAME)
        for expected_field in self.EXPECTED_FIELDS:
            self.assertIn(expected_field, raw_output)

    def test_quota_show_default_project(self):
        raw_output = self.openstack('quota show')
        for expected_field in self.EXPECTED_FIELDS:
            self.assertIn(expected_field, raw_output)

    def test_quota_show_with_default_option(self):
        raw_output = self.openstack('quota show --default')
        for expected_field in self.EXPECTED_FIELDS:
            self.assertIn(expected_field, raw_output)

    def test_quota_show_with_class_option(self):
        raw_output = self.openstack('quota show --class')
        for expected_field in self.EXPECTED_CLASS_FIELDS:
            self.assertIn(expected_field, raw_output)

    def test_quota_class_set(self):
        class_name = 'default'
        class_expected_fields = ['instances', 'volumes']
        self.openstack('quota set --instances 11 --volumes 11 --class ' +
                       class_name)
        opts = self.get_opts(class_expected_fields)
        raw_output = self.openstack('quota show --class ' + class_name + opts)
        self.assertEqual("11\n11\n", raw_output)
