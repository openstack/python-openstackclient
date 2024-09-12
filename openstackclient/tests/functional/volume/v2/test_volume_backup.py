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

from openstackclient.tests.functional.volume.v2 import common


class VolumeBackupTests(common.BaseVolumeTests):
    """Functional tests for volume backups."""

    def setUp(self):
        super().setUp()
        self.backup_enabled = False
        serv_list = self.openstack('volume service list', parse_output=True)
        for service in serv_list:
            if service['Binary'] == 'cinder-backup':
                if service['Status'] == 'enabled':
                    self.backup_enabled = True

    def test_volume_backup_restore(self):
        """Test restore backup"""
        if not self.backup_enabled:
            self.skipTest('Backup service is not enabled')
        vol_id = uuid.uuid4().hex
        # create a volume
        self.openstack(
            'volume create ' + '--size 1 ' + vol_id,
            parse_output=True,
        )
        self.wait_for_status("volume", vol_id, "available")

        # create a backup
        backup = self.openstack(
            'volume backup create ' + vol_id,
            parse_output=True,
        )
        self.wait_for_status("volume backup", backup['id'], "available")

        # restore the backup
        backup_restored = self.openstack(
            'volume backup restore {} {}'.format(backup['id'], vol_id),
            parse_output=True,
        )
        self.assertEqual(backup_restored['backup_id'], backup['id'])
        self.wait_for_status("volume backup", backup['id'], "available")
        self.wait_for_status(
            "volume", backup_restored['volume_id'], "available"
        )
        self.addCleanup(self.openstack, f'volume delete {vol_id}')
