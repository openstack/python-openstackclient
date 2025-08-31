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

from typing import ClassVar
import uuid

from openstackclient.tests.functional.volume.v3 import common


class VolumeGroupTests(common.BaseVolumeTests):
    """Functional tests for volume group."""

    API_VERSION = '3.13'
    GROUP_TYPE_NAME = uuid.uuid4().hex
    GROUP_TYPE_ID: ClassVar[str]
    VOLUME_TYPE_ID: ClassVar[str]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cmd_output = cls.openstack(
            '--os-volume-api-version '
            + cls.API_VERSION
            + ' volume group type create '
            + cls.GROUP_TYPE_NAME,
            parse_output=True,
        )
        cls.GROUP_TYPE_ID = cmd_output['ID']

        volume_type_name = uuid.uuid4().hex
        cmd_output = cls.openstack(
            'volume type create ' + volume_type_name,
            parse_output=True,
        )
        cls.VOLUME_TYPE_ID = cmd_output['id']

    @classmethod
    def tearDownClass(cls):
        try:
            raw_output = cls.openstack(
                'volume type delete ' + cls.VOLUME_TYPE_ID
            )
            cls.assertOutput('', raw_output)
            raw_output = cls.openstack(
                '--os-volume-api-version '
                + cls.API_VERSION
                + ' volume group type delete '
                + cls.GROUP_TYPE_NAME
            )
            cls.assertOutput('', raw_output)
        finally:
            super().tearDownClass()

    def test_volume_group(self):
        # create volume group
        name = uuid.uuid4().hex
        description = 'description-' + uuid.uuid4().hex
        cmd_output = self.openstack(
            '--os-volume-api-version '
            + self.API_VERSION
            + ' volume group create '
            + '--volume-group-type '
            + self.GROUP_TYPE_NAME
            + ' --volume-type '
            + self.VOLUME_TYPE_ID
            + ' --name '
            + name
            + ' --description '
            + description,
            parse_output=True,
        )
        group_id = cmd_output['ID']
        self.addCleanup(
            self.wait_for_delete,
            '--os-volume-api-version ' + self.API_VERSION + ' volume group',
            group_id,
            name_field='ID',
        )
        self.addCleanup(
            self.openstack,
            '--os-volume-api-version '
            + self.API_VERSION
            + ' volume group delete '
            + group_id,
            fail_ok=True,
        )
        self.assertIsNotNone(group_id)
        self.assertEqual(name, cmd_output['Name'])
        self.assertEqual(description, cmd_output['Description'])
        self.assertEqual(self.GROUP_TYPE_ID, cmd_output['Group Type'])
        self.assertIn(self.VOLUME_TYPE_ID, cmd_output['Volume Types'])

        # show volume group
        cmd_output = self.openstack(
            '--os-volume-api-version '
            + self.API_VERSION
            + ' volume group show '
            + group_id,
            parse_output=True,
        )
        self.assertEqual(group_id, cmd_output['ID'])
        self.assertEqual(name, cmd_output['Name'])
        self.assertEqual(description, cmd_output['Description'])

        # list volume group
        cmd_output = self.openstack(
            '--os-volume-api-version '
            + self.API_VERSION
            + ' volume group list',
            parse_output=True,
        )
        self.assertIn(group_id, [group['ID'] for group in cmd_output])
        self.assertIn(name, [group['Name'] for group in cmd_output])

        # set volume group
        new_name = uuid.uuid4().hex
        new_description = 'description-' + uuid.uuid4().hex
        self.openstack(
            '--os-volume-api-version '
            + self.API_VERSION
            + ' volume group set '
            + '--name '
            + new_name
            + ' --description '
            + new_description
            + ' '
            + group_id,
        )

        # show updated volume group
        cmd_output = self.openstack(
            '--os-volume-api-version '
            + self.API_VERSION
            + ' volume group show '
            + group_id,
            parse_output=True,
        )
        self.assertEqual(group_id, cmd_output['ID'])
        self.assertEqual(new_name, cmd_output['Name'])
        self.assertEqual(new_description, cmd_output['Description'])

        # delete volume group
        raw_output = self.openstack(
            '--os-volume-api-version '
            + self.API_VERSION
            + ' volume group delete '
            + group_id,
        )
        self.assertOutput('', raw_output)
        self.wait_for_delete(
            '--os-volume-api-version ' + self.API_VERSION + ' volume group',
            group_id,
            name_field='ID',
        )
