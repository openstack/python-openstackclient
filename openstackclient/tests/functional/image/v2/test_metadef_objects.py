# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openstackclient.tests.functional import base


class MetadefObjectTests(base.TestCase):
    def setUp(self):
        super().setUp()
        self.obj_name = self.getUniqueString('metadef-obj')
        self.ns_name = self.getUniqueString('metadef-ns')
        self.openstack(f"image metadef namespace create {self.ns_name}")
        self.addCleanup(
            lambda: self.openstack(
                f"image metadef namespace delete {self.ns_name}"
            )
        )

    def test_metadef_objects(self):
        # CREATE
        created = self.openstack(
            (
                "image metadef object create "
                f"--namespace {self.ns_name} "
                f"{self.obj_name}"
            ),
            parse_output=True,
        )
        self.addCleanup(
            lambda: self.openstack(
                f"image metadef object delete {self.ns_name} {self.obj_name}"
            )
        )
        self.assertEqual(self.obj_name, created["name"])
        self.assertEqual(self.ns_name, created["namespace_name"])

        # UPDATE
        new_name = f"{self.obj_name}-updated"
        self.openstack(
            "image metadef object update "
            f"{self.ns_name} {self.obj_name} "
            f"--name {new_name}"
        )
        self.obj_name = new_name

        # READ (get)
        shown = self.openstack(
            f"image metadef object show {self.ns_name} {self.obj_name}",
            parse_output=True,
        )
        self.assertEqual(self.obj_name, shown["name"])
        self.assertEqual(self.ns_name, shown["namespace_name"])

        # READ (list)
        rows = self.openstack(
            f"image metadef object list {self.ns_name}",
            parse_output=True,
        )
        names = {row["name"] for row in rows}
        self.assertIn(self.obj_name, names)
