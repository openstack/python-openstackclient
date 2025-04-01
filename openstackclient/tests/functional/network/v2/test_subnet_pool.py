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

import random
import uuid

from openstackclient.tests.functional.network.v2 import common


class SubnetPoolTests(common.NetworkTagTests):
    """Functional tests for subnet pool"""

    base_command = 'subnet pool'

    def test_subnet_pool_create_delete(self):
        """Test create, delete"""
        name1 = uuid.uuid4().hex
        cmd_output, pool_prefix = self._subnet_pool_create("", name1)

        self.assertEqual(name1, cmd_output["name"])
        self.assertEqual([pool_prefix], cmd_output["prefixes"])

        name2 = uuid.uuid4().hex
        cmd_output, pool_prefix = self._subnet_pool_create("", name2)

        self.assertEqual(name2, cmd_output["name"])
        self.assertEqual([pool_prefix], cmd_output["prefixes"])

        del_output = self.openstack(
            'subnet pool delete ' + name1 + ' ' + name2,
        )
        self.assertOutput('', del_output)

    def test_subnet_pool_list(self):
        """Test create, list filter"""
        cmd_output = self.openstack('token issue', parse_output=True)
        auth_project_id = cmd_output['project_id']

        cmd_output = self.openstack('project list', parse_output=True)
        admin_project_id = None
        demo_project_id = None
        for p in cmd_output:
            if p['Name'] == 'admin':
                admin_project_id = p['ID']
            if p['Name'] == 'demo':
                demo_project_id = p['ID']

        # Verify assumptions:
        # * admin and demo projects are present
        # * demo and admin are distinct projects
        # * tests run as admin
        self.assertIsNotNone(admin_project_id)
        self.assertIsNotNone(demo_project_id)
        self.assertNotEqual(admin_project_id, demo_project_id)
        self.assertEqual(admin_project_id, auth_project_id)

        # type narrow
        assert admin_project_id is not None
        assert demo_project_id is not None

        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex

        cmd_output, pool_prefix = self._subnet_pool_create(
            '--project ' + demo_project_id + ' --no-share ',
            name1,
        )
        self.addCleanup(self.openstack, 'subnet pool delete ' + name1)
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        self.assertEqual(
            False,
            cmd_output["shared"],
        )
        self.assertEqual(
            demo_project_id,
            cmd_output["project_id"],
        )
        self.assertEqual(
            [pool_prefix],
            cmd_output["prefixes"],
        )

        cmd_output, pool_prefix = self._subnet_pool_create(
            ' --share ',
            name2,
        )
        self.addCleanup(self.openstack, 'subnet pool delete ' + name2)
        self.assertEqual(
            name2,
            cmd_output["name"],
        )
        self.assertEqual(
            True,
            cmd_output["shared"],
        )
        self.assertEqual(
            admin_project_id,
            cmd_output["project_id"],
        )
        self.assertEqual(
            [pool_prefix],
            cmd_output["prefixes"],
        )

        # Test list --project
        cmd_output = self.openstack(
            'subnet pool list ' + '--project ' + demo_project_id,
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

        # Test list --share
        cmd_output = self.openstack(
            'subnet pool list ' + '--share',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertIn(name2, names)

        # Test list --name
        cmd_output = self.openstack(
            'subnet pool list ' + '--name ' + name1,
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

        # Test list --long
        cmd_output = self.openstack(
            'subnet pool list ' + '--long ',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

    def test_subnet_pool_set_show(self):
        """Test create, delete, set, show, unset"""

        name = uuid.uuid4().hex
        new_name = name + "_"
        cmd_output, pool_prefix = self._subnet_pool_create(
            '--default-prefix-length 16 '
            + '--min-prefix-length 16 '
            + '--max-prefix-length 32 '
            + '--description aaaa '
            + '--default-quota 10 ',
            name,
        )

        self.addCleanup(
            self.openstack,
            'subnet pool delete ' + cmd_output['id'],
        )
        self.assertEqual(
            name,
            cmd_output["name"],
        )
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )
        self.assertEqual(
            [pool_prefix],
            cmd_output["prefixes"],
        )
        self.assertEqual(
            16,
            cmd_output["default_prefixlen"],
        )
        self.assertEqual(
            16,
            cmd_output["min_prefixlen"],
        )
        self.assertEqual(
            32,
            cmd_output["max_prefixlen"],
        )
        self.assertEqual(
            10,
            cmd_output["default_quota"],
        )

        # Test set
        cmd_output = self.openstack(
            'subnet pool set '
            + '--name '
            + new_name
            + ' --description bbbb '
            + ' --pool-prefix 10.110.0.0/16 '
            + '--default-prefix-length 8 '
            + '--min-prefix-length 8 '
            + '--max-prefix-length 16 '
            + '--default-quota 20 '
            + name,
        )
        self.assertOutput('', cmd_output)

        cmd_output = self.openstack(
            'subnet pool show ' + new_name,
            parse_output=True,
        )
        self.assertEqual(
            new_name,
            cmd_output["name"],
        )
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )
        self.assertEqual(
            sorted(["10.110.0.0/16", pool_prefix]),
            sorted(cmd_output["prefixes"]),
        )
        self.assertEqual(
            8,
            cmd_output["default_prefixlen"],
        )
        self.assertEqual(
            8,
            cmd_output["min_prefixlen"],
        )
        self.assertEqual(
            16,
            cmd_output["max_prefixlen"],
        )
        self.assertEqual(
            20,
            cmd_output["default_quota"],
        )

        # Test unset
        # NOTE(dtroyer): The unset command --default-quota option DOES NOT
        #                WORK after a default quota has been set once on a
        #                pool.  The error appears to be in a lower layer,
        #                once that is fixed add a test for subnet pool unset
        #                --default-quota.
        #                The unset command of --pool-prefixes also doesn't work
        #                right now. It would be fixed in a separate patch once
        #                the lower layer is fixed.
        # cmd_output = self.openstack(
        #    '--debug ' +
        #    'subnet pool unset ' +
        #    ' --pool-prefix 10.110.0.0/16 ' +
        #    new_name,
        # )
        # self.assertOutput('', cmd_output)
        # self.assertNone(cmd_output["prefixes"])

    def _subnet_pool_create(self, cmd, name, is_type_ipv4=True):
        """Make a random subnet pool

        :param string cmd:
            The options for a subnet pool create command, not including
            --pool-prefix and <name>
        :param string name:
            The name of the subnet pool
        :param bool is_type_ipv4:
            Creates an IPv4 pool if True, creates an IPv6 pool otherwise

        Try random subnet ranges because we can not determine ahead of time
        what subnets are already in use, possibly by another test running in
        parallel, try 4 times before failing.
        """
        for i in range(4):
            # Create a random prefix
            if is_type_ipv4:
                pool_prefix = (
                    ".".join(
                        map(
                            str,
                            (random.randint(0, 223) for _ in range(2)),
                        )
                    )
                    + ".0.0/16"
                )
            else:
                pool_prefix = (
                    ":".join(
                        map(
                            str,
                            (
                                hex(random.randint(0, 65535))[2:]
                                for _ in range(6)
                            ),
                        )
                    )
                    + ":0:0/96"
                )

            try:
                cmd_output = self.openstack(
                    'subnet pool create '
                    + cmd
                    + ' '
                    + '--pool-prefix '
                    + pool_prefix
                    + ' '
                    + name,
                    parse_output=True,
                )
            except Exception:
                if i == 3:
                    # Raise the exception the last time
                    raise
                pass
            else:
                # Break and no longer retry if create is successful
                break

        return cmd_output, pool_prefix

    def _create_resource_for_tag_test(self, name, args):
        cmd_output, _pool_prefix = self._subnet_pool_create(args, name)
        return cmd_output
