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

import time
import uuid

from openstackclient.tests.functional.volume.v2 import common


class VolumeTypeTests(common.BaseVolumeTests):
    """Functional tests for volume type."""

    def test_volume_type_create_list(self):
        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume type create --private ' + name,
            parse_output=True,
        )
        self.addCleanup(
            self.openstack,
            'volume type delete ' + name,
        )
        self.assertEqual(name, cmd_output['name'])

        cmd_output = self.openstack(
            f'volume type show {name}',
            parse_output=True,
        )
        self.assertEqual(name, cmd_output['name'])

        cmd_output = self.openstack('volume type list', parse_output=True)
        self.assertIn(name, [t['Name'] for t in cmd_output])

        cmd_output = self.openstack(
            'volume type list --default',
            parse_output=True,
        )
        self.assertEqual(1, len(cmd_output))
        self.assertEqual('lvmdriver-1', cmd_output[0]['Name'])

    def test_volume_type_set_unset_properties(self):
        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume type create --private ' + name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'volume type delete ' + name)
        self.assertEqual(name, cmd_output['name'])

        raw_output = self.openstack(
            f'volume type set --property a=b --property c=d {name}'
        )
        self.assertEqual("", raw_output)
        cmd_output = self.openstack(
            f'volume type show {name}',
            parse_output=True,
        )
        self.assertEqual({'a': 'b', 'c': 'd'}, cmd_output['properties'])

        raw_output = self.openstack(f'volume type unset --property a {name}')
        self.assertEqual("", raw_output)
        cmd_output = self.openstack(
            f'volume type show {name}',
            parse_output=True,
        )
        self.assertEqual({'c': 'd'}, cmd_output['properties'])

    def test_volume_type_set_unset_multiple_properties(self):
        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume type create --private ' + name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'volume type delete ' + name)
        self.assertEqual(name, cmd_output['name'])

        raw_output = self.openstack(
            f'volume type set --property a=b --property c=d {name}'
        )
        self.assertEqual("", raw_output)
        cmd_output = self.openstack(
            f'volume type show {name}',
            parse_output=True,
        )
        self.assertEqual({'a': 'b', 'c': 'd'}, cmd_output['properties'])

        raw_output = self.openstack(
            f'volume type unset --property a --property c {name}'
        )
        self.assertEqual("", raw_output)
        cmd_output = self.openstack(
            f'volume type show {name}',
            parse_output=True,
        )
        self.assertEqual({}, cmd_output['properties'])

    def test_volume_type_set_unset_project(self):
        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume type create --private ' + name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'volume type delete ' + name)
        self.assertEqual(name, cmd_output['name'])

        raw_output = self.openstack(f'volume type set --project admin {name}')
        self.assertEqual("", raw_output)

        raw_output = self.openstack(
            f'volume type unset --project admin {name}'
        )
        self.assertEqual("", raw_output)

    def test_multi_delete(self):
        vol_type1 = uuid.uuid4().hex
        vol_type2 = uuid.uuid4().hex
        self.openstack(f'volume type create {vol_type1}')
        time.sleep(5)
        self.openstack(f'volume type create {vol_type2}')
        time.sleep(5)
        cmd = f'volume type delete {vol_type1} {vol_type2}'
        raw_output = self.openstack(cmd)
        self.assertOutput('', raw_output)

    # NOTE: Add some basic functional tests with the old format to
    #       make sure the command works properly, need to change
    #       these to new test format when beef up all tests for
    #       volume type commands.
    def test_encryption_type(self):
        name = uuid.uuid4().hex
        encryption_type = uuid.uuid4().hex
        # test create new encryption type
        cmd_output = self.openstack(
            'volume type create '
            '--encryption-provider LuksEncryptor '
            '--encryption-cipher aes-xts-plain64 '
            '--encryption-key-size 128 '
            '--encryption-control-location front-end ' + encryption_type,
            parse_output=True,
        )
        expected = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        for attr, value in expected.items():
            self.assertEqual(value, cmd_output['encryption'][attr])
        # test show encryption type
        cmd_output = self.openstack(
            'volume type show --encryption-type ' + encryption_type,
            parse_output=True,
        )
        expected = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        for attr, value in expected.items():
            self.assertEqual(value, cmd_output['encryption'][attr])
        # test list encryption type
        cmd_output = self.openstack(
            'volume type list --encryption-type',
            parse_output=True,
        )
        encryption_output = [
            t['Encryption'] for t in cmd_output if t['Name'] == encryption_type
        ][0]
        expected = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        for attr, value in expected.items():
            self.assertEqual(value, encryption_output[attr])
        # test set existing encryption type
        raw_output = self.openstack(
            'volume type set '
            '--encryption-key-size 256 '
            '--encryption-control-location back-end ' + encryption_type
        )
        self.assertEqual('', raw_output)
        cmd_output = self.openstack(
            'volume type show --encryption-type ' + encryption_type,
            parse_output=True,
        )
        expected = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 256,
            'control_location': 'back-end',
        }
        for attr, value in expected.items():
            self.assertEqual(value, cmd_output['encryption'][attr])
        # test set new encryption type
        cmd_output = self.openstack(
            'volume type create --private ' + name,
            parse_output=True,
        )
        self.addCleanup(
            self.openstack,
            'volume type delete ' + name,
        )
        self.assertEqual(name, cmd_output['name'])

        raw_output = self.openstack(
            'volume type set '
            '--encryption-provider LuksEncryptor '
            '--encryption-cipher aes-xts-plain64 '
            '--encryption-key-size 128 '
            '--encryption-control-location front-end ' + name
        )
        self.assertEqual('', raw_output)

        cmd_output = self.openstack(
            'volume type show --encryption-type ' + name,
            parse_output=True,
        )
        expected = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        for attr, value in expected.items():
            self.assertEqual(value, cmd_output['encryption'][attr])
        # test unset encryption type
        raw_output = self.openstack(
            'volume type unset --encryption-type ' + name
        )
        self.assertEqual('', raw_output)
        cmd_output = self.openstack(
            'volume type show --encryption-type ' + name,
            parse_output=True,
        )
        self.assertEqual({}, cmd_output['encryption'])
        # test delete encryption type
        raw_output = self.openstack('volume type delete ' + encryption_type)
        self.assertEqual('', raw_output)
