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

import json

from openstackclient.tests.functional import base


class QuotaTests(base.TestCase):
    """Functional tests for quota

    Note that for 'set' tests use different quotas for each API in different
    test runs as these may run in parallel and otherwise step on each other.
    """

    PROJECT_NAME = None

    @classmethod
    def setUpClass(cls):
        super(QuotaTests, cls).setUpClass()
        cls.haz_network = cls.is_service_enabled('network')
        cls.PROJECT_NAME =\
            cls.get_openstack_configuration_value('auth.project_name')

    def test_quota_list_details_compute(self):
        expected_headers = ["Resource", "In Use", "Reserved", "Limit"]
        cmd_output = json.loads(self.openstack(
            'quota list -f json --detail --compute'
        ))
        self.assertIsNotNone(cmd_output)
        resources = []
        for row in cmd_output:
            row_headers = [str(r) for r in row.keys()]
            self.assertEqual(sorted(expected_headers), sorted(row_headers))
            resources.append(row['Resource'])
        # Ensure that returned quota is compute quota
        self.assertIn("instances", resources)
        # and that there is no network quota here
        self.assertNotIn("networks", resources)

    def test_quota_list_details_network(self):
        expected_headers = ["Resource", "In Use", "Reserved", "Limit"]
        cmd_output = json.loads(self.openstack(
            'quota list -f json --detail --network'
        ))
        self.assertIsNotNone(cmd_output)
        resources = []
        for row in cmd_output:
            row_headers = [str(r) for r in row.keys()]
            self.assertEqual(sorted(expected_headers), sorted(row_headers))
            resources.append(row['Resource'])
        # Ensure that returned quota is network quota
        self.assertIn("networks", resources)
        # and that there is no compute quota here
        self.assertNotIn("instances", resources)

    def test_quota_list_network_option(self):
        if not self.haz_network:
            self.skipTest("No Network service present")
        self.openstack('quota set --networks 40 ' + self.PROJECT_NAME)
        cmd_output = json.loads(self.openstack(
            'quota list -f json --network'
        ))
        self.assertIsNotNone(cmd_output)
        self.assertEqual(
            40,
            cmd_output[0]["Networks"],
        )

    def test_quota_list_compute_option(self):
        self.openstack('quota set --instances 30 ' + self.PROJECT_NAME)
        cmd_output = json.loads(self.openstack(
            'quota list -f json --compute'
        ))
        self.assertIsNotNone(cmd_output)
        self.assertEqual(
            30,
            cmd_output[0]["Instances"],
        )

    def test_quota_list_volume_option(self):
        self.openstack('quota set --volumes 20 ' + self.PROJECT_NAME)
        cmd_output = json.loads(self.openstack(
            'quota list -f json --volume'
        ))
        self.assertIsNotNone(cmd_output)
        self.assertEqual(
            20,
            cmd_output[0]["Volumes"],
        )

    def test_quota_set_project(self):
        """Test quota set, show"""
        network_option = ""
        if self.haz_network:
            network_option = "--routers 21 "
        self.openstack(
            'quota set --cores 31 --backups 41 ' +
            network_option +
            self.PROJECT_NAME
        )
        cmd_output = json.loads(self.openstack(
            'quota show -f json ' + self.PROJECT_NAME
        ))
        self.assertIsNotNone(cmd_output)
        self.assertEqual(
            31,
            cmd_output["cores"],
        )
        self.assertEqual(
            41,
            cmd_output["backups"],
        )
        if self.haz_network:
            self.assertEqual(
                21,
                cmd_output["routers"],
            )

        # Check default quotas
        cmd_output = json.loads(self.openstack(
            'quota show -f json --default'
        ))
        self.assertIsNotNone(cmd_output)
        # We don't necessarily know the default quotas, we're checking the
        # returned attributes
        self.assertTrue(cmd_output["cores"] >= 0)
        self.assertTrue(cmd_output["backups"] >= 0)
        if self.haz_network:
            self.assertTrue(cmd_output["routers"] >= 0)

    def test_quota_set_class(self):
        self.openstack(
            'quota set --key-pairs 33 --snapshots 43 ' +
            '--class default'
        )
        cmd_output = json.loads(self.openstack(
            'quota show -f json --class default'
        ))
        self.assertIsNotNone(cmd_output)
        self.assertEqual(
            33,
            cmd_output["key-pairs"],
        )
        self.assertEqual(
            43,
            cmd_output["snapshots"],
        )

        # Check default quota class
        cmd_output = json.loads(self.openstack(
            'quota show -f json --class'
        ))
        self.assertIsNotNone(cmd_output)
        # We don't necessarily know the default quotas, we're checking the
        # returned attributes
        self.assertTrue(cmd_output["key-pairs"] >= 0)
        self.assertTrue(cmd_output["snapshots"] >= 0)
