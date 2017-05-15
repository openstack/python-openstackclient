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
import uuid

import fixtures

from openstackclient.tests.functional.image import base


class ImageTests(base.BaseImageTests):
    """Functional tests for Image commands"""

    def setUp(self):
        super(ImageTests, self).setUp()

        self.name = uuid.uuid4().hex
        self.image_tag = 'my_tag'
        json_output = json.loads(self.openstack(
            '--os-image-api-version 2 '
            'image create -f json --tag {tag} {name}'.format(
                tag=self.image_tag, name=self.name)
        ))
        self.image_id = json_output["id"]
        self.assertOutput(self.name, json_output['name'])

        ver_fixture = fixtures.EnvironmentVariable(
            'OS_IMAGE_API_VERSION', '2'
        )
        self.useFixture(ver_fixture)

    def tearDown(self):
        try:
            self.openstack(
                '--os-image-api-version 2 '
                'image delete ' +
                self.image_id
            )
        finally:
            super(ImageTests, self).tearDown()

    def test_image_list(self):
        json_output = json.loads(self.openstack(
            'image list -f json '
        ))
        self.assertIn(
            self.name,
            [img['Name'] for img in json_output]
        )

    def test_image_list_with_name_filter(self):
        json_output = json.loads(self.openstack(
            'image list --name ' + self.name + ' -f json'
        ))
        self.assertIn(
            self.name,
            [img['Name'] for img in json_output]
        )

    def test_image_list_with_status_filter(self):
        json_output = json.loads(self.openstack(
            'image list ' + ' --status active -f json'
        ))
        self.assertIn(
            'active',
            [img['Status'] for img in json_output]
        )

    def test_image_list_with_tag_filter(self):
        json_output = json.loads(self.openstack(
            'image list --tag ' + self.image_tag + ' --long -f json'
        ))
        for taglist in [img['Tags'] for img in json_output]:
            self.assertIn(
                self.image_tag,
                taglist
            )

    def test_image_attributes(self):
        """Test set, unset, show on attributes, tags and properties"""

        # Test explicit attributes
        self.openstack(
            'image set ' +
            '--min-disk 4 ' +
            '--min-ram 5 ' +
            '--public ' +
            self.name
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.name
        ))
        self.assertEqual(
            4,
            json_output["min_disk"],
        )
        self.assertEqual(
            5,
            json_output["min_ram"],
        )
        self.assertEqual(
            'public',
            json_output["visibility"],
        )

        # Test properties
        self.openstack(
            'image set ' +
            '--property a=b ' +
            '--property c=d ' +
            '--public ' +
            self.name
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.name
        ))
        self.assertIn("a", json_output["properties"])
        self.assertIn("c", json_output["properties"])

        self.openstack(
            'image unset ' +
            '--property a ' +
            '--property c ' +
            self.name
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.name
        ))
        self.assertNotIn("a", json_output["properties"])
        self.assertNotIn("c", json_output["properties"])

        # Test tags
        self.assertNotIn(
            '01',
            json_output["tags"]
        )
        self.openstack(
            'image set ' +
            '--tag 01 ' +
            self.name
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.name
        ))
        self.assertIn(
            '01',
            json_output["tags"]
        )

        self.openstack(
            'image unset ' +
            '--tag 01 ' +
            self.name
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.name
        ))
        self.assertNotIn(
            '01',
            json_output["tags"]
        )

    def test_image_set_rename(self):
        name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'image create -f json ' +
            name
        ))
        image_id = json_output["id"]
        self.assertEqual(
            name,
            json_output["name"],
        )
        self.openstack(
            'image set ' +
            '--name ' + name + 'xx ' +
            image_id
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            name + 'xx'
        ))
        self.assertEqual(
            name + 'xx',
            json_output["name"],
        )

    # TODO(dtroyer): This test is incomplete and doesn't properly test
    #                sharing images.  Fix after the --shared option is
    #                properly added.
    def test_image_members(self):
        """Test member add, remove, accept"""
        json_output = json.loads(self.openstack(
            'token issue -f json'
        ))
        my_project_id = json_output['project_id']

        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.name
        ))
        # NOTE(dtroyer): Until OSC supports --shared flags in create and set
        #                we can not properly test membership.  Sometimes the
        #                images are shared and sometimes they are not.
        if json_output["visibility"] == 'shared':
            self.openstack(
                'image add project ' +
                self.name + ' ' +
                my_project_id
            )
            # self.addCleanup(
            #     self.openstack,
            #     'image remove project ' +
            #     self.name + ' ' +
            #     my_project_id
            # )

            self.openstack(
                'image set ' +
                '--accept ' +
                self.name
            )
            json_output = json.loads(self.openstack(
                'image list -f json ' +
                '--shared'
            ))
            self.assertIn(
                self.name,
                [img['Name'] for img in json_output]
            )

            self.openstack(
                'image set ' +
                '--reject ' +
                self.name
            )
            json_output = json.loads(self.openstack(
                'image list -f json ' +
                '--shared'
            ))
            # self.assertNotIn(
            #     self.name,
            #     [img['Name'] for img in json_output]
            # )

            self.openstack(
                'image remove project ' +
                self.name + ' ' +
                my_project_id
            )

        # else:
        #     # Test not shared
        #     self.assertRaises(
        #         image_exceptions.HTTPForbidden,
        #         self.openstack,
        #         'image add project ' +
        #         self.name + ' ' +
        #         my_project_id
        #     )
        #     self.openstack(
        #         'image set ' +
        #         '--share ' +
        #         self.name
        #     )
