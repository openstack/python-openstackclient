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

from tempest.lib import exceptions

from openstackclient.tests.functional.object.v1 import common


class ContainerTests(common.ObjectStoreTests):
    """Functional tests for Object Store container commands."""

    def test_container(self):
        prefix = uuid.uuid4().hex
        names = [prefix + suffix for suffix in 'abc']
        for name in names:
            self.addCleanup(
                self.openstack, f'container delete {name}', fail_ok=True
            )

        # Create and show a container, then reuse its storage policy.
        name = names[0]
        data = self.openstack(f'container create {name}', parse_output=True)
        self.assertEqual(name, data[0]['container'])
        self.assertTrue(data[0]['account'])
        self.assertTrue(data[0]['x-trans-id'])
        data = self.openstack(f'container show {name}', parse_output=True)
        self.assertEqual(name, data['container'])
        self.assertTrue(data['account'])
        self.assertEqual(0, int(data['object_count']))
        self.assertEqual(0, int(data['bytes_used']))
        self.assertTrue(data['storage_policy'])
        policy = data['storage_policy']

        # Batch-create public containers using the discovered storage policy.
        data = self.openstack(
            f'container create --public --storage-policy {policy} '
            + ' '.join(names[1:]),
            parse_output=True,
        )
        self.assertEqual(names[1:], [item['container'] for item in data])
        data = self.openstack(f'container show {names[1]}', parse_output=True)
        self.assertEqual(
            {'.r:*', '.rlistings'}, set(data['read_acl'].split(','))
        )
        self.assertEqual(policy, data['storage_policy'])

        command = f'container list --prefix {prefix}'
        data = self.openstack(command + ' --long', parse_output=True)
        self.assertEqual(names, [item['Name'] for item in data])
        for item in data:
            self.assertEqual(0, int(item['Bytes']))
            self.assertEqual(0, int(item['Count']))

        for options, expected in (
            ('--limit 1', names[:1]),
            (f'--marker {names[0]}', names[1:]),
            (f'--end-marker {names[2]}', names[:2]),
            ('--all --limit 1', names),
        ):
            data = self.openstack(f'{command} {options}', parse_output=True)
            self.assertEqual(expected, [item['Name'] for item in data])

        self.assertEqual(
            '',
            self.openstack(
                f'container set {name} --property first=one '
                '--property second=two'
            ),
        )
        data = self.openstack(f'container show {name}', parse_output=True)
        self.assertEqual(
            {'first': 'one', 'second': 'two'}, self.get_properties(data)
        )
        self.openstack(f'container set {name} --property first=updated')
        data = self.openstack(f'container show {name}', parse_output=True)
        self.assertEqual(
            {'first': 'updated', 'second': 'two'}, self.get_properties(data)
        )
        self.assertEqual(
            '', self.openstack(f'container unset {name} --property first')
        )
        data = self.openstack(f'container show {name}', parse_output=True)
        self.assertEqual({'second': 'two'}, self.get_properties(data))
        self.openstack(f'container unset {name} --property second')
        data = self.openstack(f'container show {name}', parse_output=True)
        self.assertFalse(self.get_properties(data))

        # Exercise both single and batch deletion.
        self.assertEqual('', self.openstack(f'container delete {name}'))
        self.assertEqual(
            '', self.openstack('container delete ' + ' '.join(names[1:]))
        )
        for name in names:
            with self.assertRaises(exceptions.CommandFailed):
                self.openstack(f'container show {name}')
