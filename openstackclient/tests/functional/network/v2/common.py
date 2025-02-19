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


class NetworkTests(base.TestCase):
    """Functional tests for Network commands"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.haz_network = cls.is_service_enabled('network')

    def setUp(self):
        super().setUp()

        if not self.haz_network:
            self.skipTest("No Network service present")


class NetworkTagTests(NetworkTests):
    """Functional tests with tag operation"""

    base_command: str

    def test_tag_operation(self):
        # Get project IDs
        cmd_output = self.openstack(
            'token issue ',
            parse_output=True,
        )
        auth_project_id = cmd_output['project_id']

        # Network create with no options
        name1 = self._create_resource_and_tag_check('', [])
        # Network create with tags
        name2 = self._create_resource_and_tag_check(
            '--tag red --tag blue', ['red', 'blue']
        )
        # Network create with no tag explicitly
        name3 = self._create_resource_and_tag_check('--no-tag', [])

        self._set_resource_and_tag_check(
            'set', name1, '--tag red --tag green', ['red', 'green']
        )

        list_expected: tuple[tuple[str, list[str]], ...] = (
            (name1, ['red', 'green']),
            (name2, ['red', 'blue']),
            (name3, []),
        )
        self._list_tag_check(auth_project_id, list_expected)

        self._set_resource_and_tag_check(
            'set', name1, '--tag blue', ['red', 'green', 'blue']
        )
        self._set_resource_and_tag_check(
            'set',
            name1,
            '--no-tag --tag yellow --tag orange --tag purple',
            ['yellow', 'orange', 'purple'],
        )
        self._set_resource_and_tag_check(
            'unset', name1, '--tag yellow', ['orange', 'purple']
        )
        self._set_resource_and_tag_check('unset', name1, '--all-tag', [])
        self._set_resource_and_tag_check('set', name2, '--no-tag', [])

    def _list_tag_check(self, project_id, expected):
        cmd_output = self.openstack(
            f'{self.base_command} list --long --project {project_id}',
            parse_output=True,
        )
        for name, tags in expected:
            net = [n for n in cmd_output if n['Name'] == name][0]
            self.assertEqual(set(tags), set(net['Tags']))

    def _create_resource_for_tag_test(self, name, args):
        return self.openstack(
            f'{self.base_command} create {args} {name}',
            parse_output=True,
        )

    def _create_resource_and_tag_check(
        self,
        args: str,
        expected: list[str],
    ) -> str:
        name = uuid.uuid4().hex
        cmd_output = self._create_resource_for_tag_test(name, args)
        self.addCleanup(self.openstack, f'{self.base_command} delete {name}')
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(set(expected), set(cmd_output['tags']))
        return name

    def _set_resource_and_tag_check(self, command, name, args, expected):
        cmd_output = self.openstack(
            f'{self.base_command} {command} {args} {name}'
        )
        self.assertFalse(cmd_output)
        cmd_output = self.openstack(
            f'{self.base_command} show {name}',
            parse_output=True,
        )
        self.assertEqual(set(expected), set(cmd_output['tags']))
