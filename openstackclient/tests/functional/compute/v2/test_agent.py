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

import hashlib
import json

from openstackclient.tests.functional import base


class ComputeAgentTests(base.TestCase):
    """Functional tests for compute agent."""

    # Generate two different md5hash
    MD5HASH1 = hashlib.md5()
    MD5HASH1.update('agent_1')
    MD5HASH1 = MD5HASH1.hexdigest()
    MD5HASH2 = hashlib.md5()
    MD5HASH2.update('agent_2')
    MD5HASH2 = MD5HASH2.hexdigest()

    def test_compute_agent_delete(self):
        """Test compute agent create, delete multiple"""
        os1 = "os_1"
        arch1 = "x86_64"
        ver1 = "v1"
        url1 = "http://localhost"
        md5hash1 = self.MD5HASH1
        hyper1 = "kvm"
        cmd1 = ' '.join((os1, arch1, ver1, url1, md5hash1, hyper1))

        cmd_output = json.loads(self.openstack(
            'compute agent create -f json ' +
            cmd1
        ))
        agent_id1 = str(cmd_output["agent_id"])

        os2 = "os_2"
        arch2 = "x86"
        ver2 = "v2"
        url2 = "http://openstack"
        md5hash2 = self.MD5HASH2
        hyper2 = "xen"
        cmd2 = ' '.join((os2, arch2, ver2, url2, md5hash2, hyper2))

        cmd_output = json.loads(self.openstack(
            'compute agent create -f json ' +
            cmd2
        ))
        agent_id2 = str(cmd_output["agent_id"])

        # Test compute agent delete
        del_output = self.openstack(
            'compute agent delete ' +
            agent_id1 + ' ' + agent_id2
        )
        self.assertOutput('', del_output)

    def test_compute_agent_list(self):
        """Test compute agent create and list"""
        os1 = "os_1"
        arch1 = "x86_64"
        ver1 = "v1"
        url1 = "http://localhost"
        md5hash1 = self.MD5HASH1
        hyper1 = "kvm"
        cmd1 = ' '.join((os1, arch1, ver1, url1, md5hash1, hyper1))

        cmd_output = json.loads(self.openstack(
            'compute agent create -f json ' +
            cmd1
        ))
        agent_id1 = str(cmd_output["agent_id"])
        self.addCleanup(self.openstack, 'compute agent delete ' + agent_id1)

        os2 = "os_2"
        arch2 = "x86"
        ver2 = "v2"
        url2 = "http://openstack"
        md5hash2 = self.MD5HASH2
        hyper2 = "xen"
        cmd2 = ' '.join((os2, arch2, ver2, url2, md5hash2, hyper2))

        cmd_output = json.loads(self.openstack(
            'compute agent create -f json ' +
            cmd2
        ))
        agent_id2 = str(cmd_output["agent_id"])
        self.addCleanup(self.openstack, 'compute agent delete ' + agent_id2)

        # Test compute agent list
        cmd_output = json.loads(self.openstack(
            'compute agent list -f json'
        ))

        hypervisors = [x["Hypervisor"] for x in cmd_output]
        self.assertIn(hyper1, hypervisors)
        self.assertIn(hyper2, hypervisors)

        os = [x['OS'] for x in cmd_output]
        self.assertIn(os1, os)
        self.assertIn(os2, os)

        archs = [x['Architecture'] for x in cmd_output]
        self.assertIn(arch1, archs)
        self.assertIn(arch2, archs)

        versions = [x['Version'] for x in cmd_output]
        self.assertIn(ver1, versions)
        self.assertIn(ver2, versions)

        md5hashes = [x['Md5Hash'] for x in cmd_output]
        self.assertIn(md5hash1, md5hashes)
        self.assertIn(md5hash2, md5hashes)

        urls = [x['URL'] for x in cmd_output]
        self.assertIn(url1, urls)
        self.assertIn(url2, urls)

        # Test compute agent list --hypervisor
        cmd_output = json.loads(self.openstack(
            'compute agent list -f json ' +
            '--hypervisor kvm'
        ))

        hypervisors = [x["Hypervisor"] for x in cmd_output]
        self.assertIn(hyper1, hypervisors)
        self.assertNotIn(hyper2, hypervisors)

        os = [x['OS'] for x in cmd_output]
        self.assertIn(os1, os)
        self.assertNotIn(os2, os)

        archs = [x['Architecture'] for x in cmd_output]
        self.assertIn(arch1, archs)
        self.assertNotIn(arch2, archs)

        versions = [x['Version'] for x in cmd_output]
        self.assertIn(ver1, versions)
        self.assertNotIn(ver2, versions)

        md5hashes = [x['Md5Hash'] for x in cmd_output]
        self.assertIn(md5hash1, md5hashes)
        self.assertNotIn(md5hash2, md5hashes)

        urls = [x['URL'] for x in cmd_output]
        self.assertIn(url1, urls)
        self.assertNotIn(url2, urls)

    def test_compute_agent_set(self):
        """Test compute agent set"""
        os1 = "os_1"
        arch1 = "x86_64"
        ver1 = "v1"
        ver2 = "v2"
        url1 = "http://localhost"
        url2 = "http://openstack"
        md5hash1 = self.MD5HASH1
        md5hash2 = self.MD5HASH2
        hyper1 = "kvm"
        cmd = ' '.join((os1, arch1, ver1, url1, md5hash1, hyper1))

        cmd_output = json.loads(self.openstack(
            'compute agent create -f json ' +
            cmd
        ))
        agent_id = str(cmd_output["agent_id"])
        self.assertEqual(ver1, cmd_output["version"])
        self.assertEqual(url1, cmd_output["url"])
        self.assertEqual(md5hash1, cmd_output["md5hash"])

        self.addCleanup(self.openstack, 'compute agent delete ' + agent_id)

        raw_output = self.openstack(
            'compute agent set ' +
            agent_id + ' ' +
            '--agent-version ' + ver2 + ' ' +
            '--url ' + url2 + ' ' +
            '--md5hash ' + md5hash2
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'compute agent list -f json'
        ))
        self.assertEqual(ver2, cmd_output[0]["Version"])
        self.assertEqual(url2, cmd_output[0]["URL"])
        self.assertEqual(md5hash2, cmd_output[0]["Md5Hash"])
