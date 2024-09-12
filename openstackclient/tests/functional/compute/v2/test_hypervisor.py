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


class HypervisorTests(base.TestCase):
    """Functional tests for hypervisor."""

    def test_hypervisor_list(self):
        """Test create defaults, list filters, delete"""
        # Test list
        cmd_output = json.loads(
            self.openstack(
                "hypervisor list -f json --os-compute-api-version 2.1"
            )
        )
        ids1 = [x["ID"] for x in cmd_output]
        self.assertIsNotNone(cmd_output)

        cmd_output = json.loads(self.openstack("hypervisor list -f json"))
        ids2 = [x["ID"] for x in cmd_output]
        self.assertIsNotNone(cmd_output)

        # Show test - old microversion
        for i in ids1:
            cmd_output = json.loads(
                self.openstack(
                    f"hypervisor show {i} -f json "
                    " --os-compute-api-version 2.1"
                )
            )
            self.assertIsNotNone(cmd_output)
        # When we list hypervisors with older MV we get ids as integers. We
        # need to verify that show finds resources independently
        # Show test - latest microversion
        for i in ids2:
            cmd_output = json.loads(
                self.openstack(f"hypervisor show {i} -f json")
            )
            self.assertIsNotNone(cmd_output)
