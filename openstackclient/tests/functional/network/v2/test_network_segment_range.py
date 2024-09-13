# Copyright (c) 2019, Intel Corporation.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import uuid

from openstackclient.tests.functional.network.v2 import common


class NetworkSegmentRangeTests(common.NetworkTests):
    """Functional tests for network segment range"""

    def setUp(self):
        super().setUp()

        if not self.is_extension_enabled('network-segment-range'):
            self.skipTest("No network-segment-range extension present")

        self.PROJECT_NAME = uuid.uuid4().hex

    def test_network_segment_range_create_delete(self):
        # Make a project
        project_id = self.openstack(
            'project create ' + self.PROJECT_NAME,
            parse_output=True,
        )['id']
        name = uuid.uuid4().hex
        json_output = self.openstack(
            ' network segment range create '
            + '--private '
            + "--project "
            + self.PROJECT_NAME
            + " "
            + '--network-type vxlan '
            + '--minimum 2005 '
            + '--maximum 2009 '
            + name,
            parse_output=True,
        )
        self.assertEqual(
            name,
            json_output["name"],
        )
        self.assertEqual(
            project_id,
            json_output["project_id"],
        )

        raw_output = self.openstack(
            'network segment range delete ' + name,
        )
        self.assertOutput('', raw_output)
        raw_output_project = self.openstack(
            'project delete ' + self.PROJECT_NAME
        )
        self.assertEqual('', raw_output_project)

    def test_network_segment_range_list(self):
        name = uuid.uuid4().hex
        json_output = self.openstack(
            ' network segment range create '
            + '--shared '
            + '--network-type geneve '
            + '--minimum 2013 '
            + '--maximum 2017 '
            + name,
            parse_output=True,
        )
        network_segment_range_id = json_output.get('id')
        network_segment_range_name = json_output.get('name')
        self.addCleanup(
            self.openstack,
            'network segment range delete ' + network_segment_range_id,
        )
        self.assertEqual(
            name,
            json_output["name"],
        )

        json_output = self.openstack(
            'network segment range list',
            parse_output=True,
        )
        item_map = {item.get('ID'): item.get('Name') for item in json_output}
        self.assertIn(network_segment_range_id, item_map.keys())
        self.assertIn(network_segment_range_name, item_map.values())

    def test_network_segment_range_set_show(self):
        project_id = self.openstack(
            'project create ' + self.PROJECT_NAME,
            parse_output=True,
        )['id']
        name = uuid.uuid4().hex
        json_output = self.openstack(
            ' network segment range create '
            + '--private '
            + "--project "
            + self.PROJECT_NAME
            + " "
            + '--network-type geneve '
            + '--minimum 2021 '
            + '--maximum 2025 '
            + name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'network segment range delete ' + name)
        self.assertEqual(
            name,
            json_output["name"],
        )
        self.assertEqual(
            project_id,
            json_output["project_id"],
        )

        new_minimum = 2020
        new_maximum = 2029
        cmd_output = self.openstack(
            f'network segment range set --minimum {new_minimum} --maximum {new_maximum} '
            f'{name}'
        )
        self.assertOutput('', cmd_output)

        json_output = self.openstack(
            'network segment range show ' + name,
            parse_output=True,
        )
        self.assertEqual(
            new_minimum,
            json_output["minimum"],
        )
        self.assertEqual(
            new_maximum,
            json_output["maximum"],
        )

        raw_output_project = self.openstack(
            'project delete ' + self.PROJECT_NAME
        )
        self.assertEqual('', raw_output_project)
