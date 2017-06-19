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
import os
import uuid

# from glanceclient import exc as image_exceptions

from openstackclient.tests.functional import base


class ImageTests(base.TestCase):
    """Functional tests for image. """

    NAME = uuid.uuid4().hex
    OTHER_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        os.environ['OS_IMAGE_API_VERSION'] = '2'
        json_output = json.loads(cls.openstack(
            'image create -f json ' +
            cls.NAME
        ))
        cls.image_id = json_output["id"]
        cls.assertOutput(cls.NAME, json_output['name'])

    @classmethod
    def tearDownClass(cls):
        cls.openstack(
            'image delete ' +
            cls.image_id
        )

    def test_image_list(self):
        json_output = json.loads(self.openstack(
            'image list -f json '
        ))
        self.assertIn(
            self.NAME,
            [img['Name'] for img in json_output]
        )

    def test_image_list_with_name_filter(self):
        json_output = json.loads(self.openstack(
            'image list --name ' + self.NAME + ' -f json'
        ))
        self.assertIn(
            self.NAME,
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

    def test_image_attributes(self):
        """Test set, unset, show on attributes, tags and properties"""

        # Test explicit attributes
        self.openstack(
            'image set ' +
            '--min-disk 4 ' +
            '--min-ram 5 ' +
            '--public ' +
            self.NAME
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.NAME
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
            self.NAME
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.NAME
        ))
        self.assertEqual(
            "a='b', c='d'",
            json_output["properties"],
        )

        self.openstack(
            'image unset ' +
            '--property a ' +
            '--property c ' +
            self.NAME
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.NAME
        ))
        self.assertNotIn(
            'properties',
            json_output,
        )

        # Test tags
        self.openstack(
            'image set ' +
            '--tag 01 ' +
            self.NAME
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.NAME
        ))
        self.assertEqual(
            '01',
            json_output["tags"],
        )

        self.openstack(
            'image unset ' +
            '--tag 01 ' +
            self.NAME
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.NAME
        ))
        self.assertEqual(
            '',
            json_output["tags"],
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
            self.NAME
        ))
        # NOTE(dtroyer): Until OSC supports --shared flags in create and set
        #                we can not properly test membership.  Sometimes the
        #                images are shared and sometimes they are not.
        if json_output["visibility"] == 'shared':
            self.openstack(
                'image add project ' +
                self.NAME + ' ' +
                my_project_id
            )
            # self.addCleanup(
            #     self.openstack,
            #     'image remove project ' +
            #     self.NAME + ' ' +
            #     my_project_id
            # )

            self.openstack(
                'image set ' +
                '--accept ' +
                self.NAME
            )
            json_output = json.loads(self.openstack(
                'image list -f json ' +
                '--shared'
            ))
            self.assertIn(
                self.NAME,
                [img['Name'] for img in json_output]
            )

            self.openstack(
                'image set ' +
                '--reject ' +
                self.NAME
            )
            json_output = json.loads(self.openstack(
                'image list -f json ' +
                '--shared'
            ))
            # self.assertNotIn(
            #     self.NAME,
            #     [img['Name'] for img in json_output]
            # )

            self.openstack(
                'image remove project ' +
                self.NAME + ' ' +
                my_project_id
            )

        # else:
        #     # Test not shared
        #     self.assertRaises(
        #         image_exceptions.HTTPForbidden,
        #         self.openstack,
        #         'image add project ' +
        #         self.NAME + ' ' +
        #         my_project_id
        #     )
        #     self.openstack(
        #         'image set ' +
        #         '--share ' +
        #         self.NAME
        #     )
