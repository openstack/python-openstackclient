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

from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions

from openstackclient.tests.functional import base


class QuotaTests(base.TestCase):
    """Functional tests for quota

    Note that for 'set' tests use different quotas for each API in different
    test runs as these may run in parallel and otherwise step on each other.
    """

    PROJECT_NAME: str

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.haz_network = cls.is_service_enabled('network')
        cls.PROJECT_NAME = data_utils.rand_name('TestProject')
        cls.openstack(f'project create {cls.PROJECT_NAME}')

    @classmethod
    def tearDownClass(cls):
        cls.openstack(f'project delete {cls.PROJECT_NAME}')
        super().tearDownClass()

    def test_quota_list_network_option(self):
        if not self.haz_network:
            self.skipTest("No Network service present")
        self.openstack('quota set --networks 40 ' + self.PROJECT_NAME)
        cmd_output = self.openstack(
            'quota list --network',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        self.assertEqual(
            40,
            cmd_output[0]["Networks"],
        )

    def test_quota_list_compute_option(self):
        self.openstack('quota set --instances 30 ' + self.PROJECT_NAME)
        cmd_output = self.openstack(
            'quota list --compute',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        self.assertEqual(
            30,
            cmd_output[0]["Instances"],
        )

    def test_quota_list_volume_option(self):
        self.openstack('quota set --volumes 20 ' + self.PROJECT_NAME)
        cmd_output = self.openstack(
            'quota list --volume',
            parse_output=True,
        )
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
            'quota set --cores 31 --backups 41 '
            + network_option
            + self.PROJECT_NAME
        )
        cmd_output = self.openstack(
            'quota show ' + self.PROJECT_NAME,
            parse_output=True,
        )
        cmd_output = {x['Resource']: x['Limit'] for x in cmd_output}
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
        cmd_output = self.openstack(
            'quota show --default',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        # We don't necessarily know the default quotas, we're checking the
        # returned attributes
        cmd_output = {x['Resource']: x['Limit'] for x in cmd_output}
        self.assertTrue(cmd_output["cores"] >= 0)
        self.assertTrue(cmd_output["backups"] >= 0)
        if self.haz_network:
            self.assertTrue(cmd_output["routers"] >= 0)

    def test_quota_set_default(self):
        self.openstack(
            'quota set --key-pairs 33 --snapshots 43 --class default'
        )
        cmd_output = self.openstack(
            'quota show --default',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        cmd_output = {x['Resource']: x['Limit'] for x in cmd_output}
        self.assertEqual(33, cmd_output["key-pairs"])
        self.assertEqual(43, cmd_output["snapshots"])

    def _restore_quota_limit(self, resource, limit, project):
        self.openstack(f'quota set --{resource} {limit} {project}')

    def test_quota_set_network(self):
        if not self.haz_network:
            self.skipTest('No Network service present')
        if not self.is_extension_enabled('quota-check-limit'):
            self.skipTest('No "quota-check-limit" extension present')

        cmd_output = self.openstack(
            'quota list --network',
            parse_output=True,
        )
        self.addCleanup(
            self._restore_quota_limit,
            'network',
            cmd_output[0]['Networks'],
            self.PROJECT_NAME,
        )

        self.openstack('quota set --networks 40 ' + self.PROJECT_NAME)
        cmd_output = self.openstack(
            'quota list --network',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        self.assertEqual(40, cmd_output[0]['Networks'])

        # That will ensure we have at least two networks in the system.
        for _ in range(2):
            self.openstack(
                f'network create --project {self.PROJECT_NAME} {uuid.uuid4().hex}'
            )

        self.assertRaises(
            exceptions.CommandFailed,
            self.openstack,
            'quota set --networks 1 ' + self.PROJECT_NAME,
        )

    def test_quota_set_network_with_force(self):
        self.skipTest('story 2010110')
        if not self.haz_network:
            self.skipTest('No Network service present')
        # NOTE(ralonsoh): the Neutron support for the flag "check-limit" was
        # added with the extension "quota-check-limit". The flag "force" was
        # added too in order to change the behaviour of Neutron quota engine
        # and mimic the Nova one: by default the engine will check the resource
        # usage before setting the new limit; with "force", this check will be
        # skipped (in Yoga, this behaviour is still NOT the default in
        # Neutron).
        if not self.is_extension_enabled('quota-check-limit'):
            self.skipTest('No "quota-check-limit" extension present')

        cmd_output = self.openstack(
            'quota list --network',
            parse_output=True,
        )
        self.addCleanup(
            self._restore_quota_limit,
            'network',
            cmd_output[0]['Networks'],
            self.PROJECT_NAME,
        )

        self.openstack('quota set --networks 40 ' + self.PROJECT_NAME)
        cmd_output = self.openstack(
            'quota list --network',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        self.assertEqual(40, cmd_output[0]['Networks'])

        # That will ensure we have at least two networks in the system.
        for _ in range(2):
            self.openstack(
                f'network create --project {self.PROJECT_NAME} {uuid.uuid4().hex}'
            )

        self.openstack('quota set --networks 1 --force ' + self.PROJECT_NAME)
        cmd_output = self.openstack(
            'quota list --network',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        self.assertEqual(1, cmd_output[0]['Networks'])

    def test_quota_show(self):
        expected_headers = ["Resource", "Limit"]
        cmd_output = self.openstack(
            'quota show',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        resources = []
        for row in cmd_output:
            row_headers = [str(r) for r in row.keys()]
            self.assertEqual(sorted(expected_headers), sorted(row_headers))
            resources.append(row['Resource'])
        # Ensure that returned quota has network quota...
        self.assertIn("networks", resources)
        # ...and compute quota
        self.assertIn("instances", resources)

    def test_quota_show_usage_option(self):
        expected_headers = ["Resource", "Limit", "In Use", "Reserved"]
        cmd_output = self.openstack(
            'quota show --usage',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        resources = []
        for row in cmd_output:
            row_headers = [str(r) for r in row.keys()]
            self.assertEqual(sorted(expected_headers), sorted(row_headers))
            resources.append(row['Resource'])
            for header in expected_headers[1:]:
                self.assertIsInstance(row[header], int)
        # Ensure that returned quota has network quota...
        self.assertIn("networks", resources)
        # ...and compute quota
        self.assertIn("instances", resources)
