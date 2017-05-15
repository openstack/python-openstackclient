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
import time
import uuid

from openstackclient.tests.functional.volume.v1 import common


class VolumeTypeTests(common.BaseVolumeTests):
    """Functional tests for volume type. """

    def test_volume_type_create_list(self):
        name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume type create -f json --private ' +
            name,
        ))
        self.addCleanup(
            self.openstack,
            'volume type delete ' +
            name,
        )
        self.assertEqual(name, cmd_output['name'])

        cmd_output = json.loads(self.openstack(
            'volume type show -f json %s' % name
        ))
        self.assertEqual(self.NAME, cmd_output['name'])

        cmd_output = json.loads(self.openstack('volume type list -f json'))
        self.assertIn(self.NAME, [t['Name'] for t in cmd_output])

        cmd_output = json.loads(self.openstack(
            'volume type list -f json --default'
        ))
        self.assertEqual(1, len(cmd_output))
        self.assertEqual('lvmdriver-1', cmd_output[0]['Name'])

    def test_volume_type_set_unset_properties(self):
        name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume type create -f json --private ' +
            name,
        ))
        self.addCleanup(
            self.openstack,
            'volume type delete ' + name
        )
        self.assertEqual(name, cmd_output['name'])

        raw_output = self.openstack(
            'volume type set --property a=b --property c=d %s' % name
        )
        self.assertEqual("", raw_output)
        cmd_output = json.loads(self.openstack(
            'volume type show -f json %s' % name
        ))
        self.assertEqual({'a': 'b', 'c': 'd'}, cmd_output['properties'])

        raw_output = self.openstack(
            'volume type unset --property a %s' % name
        )
        self.assertEqual("", raw_output)
        cmd_output = json.loads(self.openstack(
            'volume type show -f json %s' % name
        ))
        self.assertEqual({'c': 'd'}, cmd_output['properties'])

    def test_volume_type_set_unset_multiple_properties(self):
        name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume type create -f json --private ' +
            name,
        ))
        self.addCleanup(
            self.openstack,
            'volume type delete ' + name
        )
        self.assertEqual(name, cmd_output['name'])

        raw_output = self.openstack(
            'volume type set --property a=b --property c=d %s' % name
        )
        self.assertEqual("", raw_output)
        cmd_output = json.loads(self.openstack(
            'volume type show -f json %s' % name
        ))
        self.assertEqual({'a': 'b', 'c': 'd'}, cmd_output['properties'])

        raw_output = self.openstack(
            'volume type unset --property a --property c %s' % name
        )
        self.assertEqual("", raw_output)
        cmd_output = json.loads(self.openstack(
            'volume type show -f json %s' % name
        ))
        self.assertEqual({}, cmd_output['properties'])

    def test_multi_delete(self):
        vol_type1 = uuid.uuid4().hex
        vol_type2 = uuid.uuid4().hex
        self.openstack('volume type create %s' % vol_type1)
        time.sleep(5)
        self.openstack('volume type create %s' % vol_type2)
        time.sleep(5)
        cmd = 'volume type delete %s %s' % (vol_type1, vol_type2)
        raw_output = self.openstack(cmd)
        self.assertOutput('', raw_output)

    # NOTE: Add some basic funtional tests with the old format to
    #       make sure the command works properly, need to change
    #       these to new test format when beef up all tests for
    #       volume tye commands.
    def test_encryption_type(self):
        encryption_type = uuid.uuid4().hex
        # test create new encryption type
        cmd_output = json.loads(self.openstack(
            'volume type create -f json '
            '--encryption-provider LuksEncryptor '
            '--encryption-cipher aes-xts-plain64 '
            '--encryption-key-size 128 '
            '--encryption-control-location front-end ' +
            encryption_type))
        expected = {'provider': 'LuksEncryptor',
                    'cipher': 'aes-xts-plain64',
                    'key_size': 128,
                    'control_location': 'front-end'}
        for attr, value in expected.items():
            self.assertEqual(value, cmd_output['encryption'][attr])
        # test show encryption type
        cmd_output = json.loads(self.openstack(
            'volume type show -f json --encryption-type ' + encryption_type))
        expected = {'provider': 'LuksEncryptor',
                    'cipher': 'aes-xts-plain64',
                    'key_size': 128,
                    'control_location': 'front-end'}
        for attr, value in expected.items():
            self.assertEqual(value, cmd_output['encryption'][attr])
        # test list encryption type
        cmd_output = json.loads(self.openstack(
            'volume type list -f json --encryption-type'))
        encryption_output = [t['Encryption'] for t in cmd_output
                             if t['Name'] == encryption_type][0]
        expected = {'provider': 'LuksEncryptor',
                    'cipher': 'aes-xts-plain64',
                    'key_size': 128,
                    'control_location': 'front-end'}
        for attr, value in expected.items():
            self.assertEqual(value, encryption_output[attr])
        # test set new encryption type
        raw_output = self.openstack(
            'volume type set '
            '--encryption-provider LuksEncryptor '
            '--encryption-cipher aes-xts-plain64 '
            '--encryption-key-size 128 '
            '--encryption-control-location front-end ' +
            self.NAME)
        self.assertEqual('', raw_output)

        name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume type create -f json --private ' +
            name,
        ))
        self.addCleanup(
            self.openstack,
            'volume type delete ' + name,
        )
        self.assertEqual(name, cmd_output['name'])

        cmd_output = json.loads(self.openstack(
            'volume type show -f json --encryption-type ' + name
        ))
        expected = {'provider': 'LuksEncryptor',
                    'cipher': 'aes-xts-plain64',
                    'key_size': 128,
                    'control_location': 'front-end'}
        for attr, value in expected.items():
            self.assertEqual(value, cmd_output['encryption'][attr])
        # test unset encryption type
        raw_output = self.openstack(
            'volume type unset --encryption-type ' + name
        )
        self.assertEqual('', raw_output)
        cmd_output = json.loads(self.openstack(
            'volume type show -f json --encryption-type ' + name
        ))
        self.assertEqual({}, cmd_output['encryption'])
        # test delete encryption type
        raw_output = self.openstack('volume type delete ' + encryption_type)
        self.assertEqual('', raw_output)
