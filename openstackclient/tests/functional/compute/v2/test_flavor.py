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

from openstackclient.tests.functional import base


class FlavorTests(base.TestCase):
    """Functional tests for flavor."""

    PROJECT_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Make a project
        cmd_output = cls.openstack(
            "project create --enable " + cls.PROJECT_NAME,
            parse_output=True,
        )
        cls.project_id = cmd_output["id"]

    @classmethod
    def tearDownClass(cls):
        try:
            raw_output = cls.openstack("project delete " + cls.PROJECT_NAME)
            cls.assertOutput('', raw_output)
        finally:
            super().tearDownClass()

    def test_flavor_delete(self):
        """Test create w/project, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            "flavor create "
            + "--project "
            + self.PROJECT_NAME
            + " "
            + "--private "
            + name1,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            "flavor create "
            + "--id qaz "
            + "--project "
            + self.PROJECT_NAME
            + " "
            + "--private "
            + name2,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            "qaz",
            cmd_output["id"],
        )

        raw_output = self.openstack(
            "flavor delete " + name1 + " " + name2,
        )
        self.assertOutput('', raw_output)

    def test_flavor_list(self):
        """Test create defaults, list filters, delete"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            "flavor create " + "--property a=b " + "--property c=d " + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, "flavor delete " + name1)
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            name1,
            cmd_output["name"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            "flavor create "
            + "--id qaz "
            + "--ram 123 "
            + "--private "
            + "--property a=b2 "
            + "--property b=d2 "
            + name2,
            parse_output=True,
        )
        self.addCleanup(self.openstack, "flavor delete " + name2)
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            "qaz",
            cmd_output["id"],
        )
        self.assertEqual(
            name2,
            cmd_output["name"],
        )
        self.assertEqual(
            123,
            cmd_output["ram"],
        )
        self.assertEqual(
            0,
            cmd_output["disk"],
        )
        self.assertFalse(
            cmd_output["os-flavor-access:is_public"],
        )
        self.assertDictEqual(
            {"a": "b2", "b": "d2"},
            cmd_output["properties"],
        )

        # Test list
        cmd_output = self.openstack(
            "flavor list",
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertNotIn(name2, col_name)

        # Test list --long
        cmd_output = self.openstack(
            "flavor list " + "--long",
            parse_output=True,
        )
        # We have list of complex json objects
        # Iterate through the list setting flags
        found_expected = False
        for rec in cmd_output:
            if rec['Name'] == name1:
                found_expected = True
                self.assertEqual('b', rec['Properties']['a'])
                self.assertEqual('d', rec['Properties']['c'])
            elif rec['Name'] == name2:
                # We should have not seen private flavor
                self.assertFalse(True)
        self.assertTrue(found_expected)

        # Test list --public
        cmd_output = self.openstack(
            "flavor list " + "--public",
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertNotIn(name2, col_name)

        # Test list --private
        cmd_output = self.openstack(
            "flavor list " + "--private",
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, col_name)
        self.assertIn(name2, col_name)

        # Test list --all
        cmd_output = self.openstack(
            "flavor list " + "--all",
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertIn(name2, col_name)

    def test_flavor_properties(self):
        """Test create defaults, list filters, delete"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            "flavor create "
            + "--id qaz "
            + "--ram 123 "
            + "--disk 20 "
            + "--private "
            + "--property a=first "
            + "--property b=second "
            + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, "flavor delete " + name1)
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            "qaz",
            cmd_output["id"],
        )
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        self.assertEqual(
            123,
            cmd_output["ram"],
        )
        self.assertEqual(
            20,
            cmd_output["disk"],
        )
        self.assertFalse(
            cmd_output["os-flavor-access:is_public"],
        )
        self.assertDictEqual(
            {"a": "first", "b": "second"},
            cmd_output["properties"],
        )

        raw_output = self.openstack(
            "flavor set "
            + "--property a='third and 10' "
            + "--property g=fourth "
            + name1
        )
        self.assertEqual('', raw_output)

        cmd_output = self.openstack(
            "flavor show " + name1,
            parse_output=True,
        )
        self.assertEqual(
            "qaz",
            cmd_output["id"],
        )
        self.assertEqual('third and 10', cmd_output['properties']['a'])
        self.assertEqual('second', cmd_output['properties']['b'])
        self.assertEqual('fourth', cmd_output['properties']['g'])

        raw_output = self.openstack("flavor unset " + "--property b " + name1)
        self.assertEqual('', raw_output)

        cmd_output = self.openstack(
            "flavor show " + name1,
            parse_output=True,
        )

        self.assertNotIn('b', cmd_output['properties'])
