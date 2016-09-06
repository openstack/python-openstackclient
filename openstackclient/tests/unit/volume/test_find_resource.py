#   Copyright 2013 Nebula Inc.
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

import mock

from cinderclient.v1 import volume_snapshots
from cinderclient.v1 import volumes
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit import utils as test_utils
from openstackclient.volume import client  # noqa


# Monkey patch for v1 cinderclient
# NOTE(dtroyer): Do here because openstackclient.volume.client
# doesn't do it until the client object is created now.
volumes.Volume.NAME_ATTR = 'display_name'
volume_snapshots.Snapshot.NAME_ATTR = 'display_name'


ID = '1after909'
NAME = 'PhilSpector'


class TestFindResourceVolumes(test_utils.TestCase):

    def setUp(self):
        super(TestFindResourceVolumes, self).setUp()
        api = mock.Mock()
        api.client = mock.Mock()
        api.client.get = mock.Mock()
        resp = mock.Mock()
        body = {"volumes": [{"id": ID, 'display_name': NAME}]}
        api.client.get.side_effect = [Exception("Not found"),
                                      Exception("Not found"),
                                      (resp, body)]
        self.manager = volumes.VolumeManager(api)

    def test_find(self):
        result = utils.find_resource(self.manager, NAME)
        self.assertEqual(ID, result.id)
        self.assertEqual(NAME, result.display_name)

    def test_not_find(self):
        self.assertRaises(exceptions.CommandError, utils.find_resource,
                          self.manager, 'GeorgeMartin')


class TestFindResourceVolumeSnapshots(test_utils.TestCase):

    def setUp(self):
        super(TestFindResourceVolumeSnapshots, self).setUp()
        api = mock.Mock()
        api.client = mock.Mock()
        api.client.get = mock.Mock()
        resp = mock.Mock()
        body = {"snapshots": [{"id": ID, 'display_name': NAME}]}
        api.client.get.side_effect = [Exception("Not found"),
                                      Exception("Not found"),
                                      (resp, body)]
        self.manager = volume_snapshots.SnapshotManager(api)

    def test_find(self):
        result = utils.find_resource(self.manager, NAME)
        self.assertEqual(ID, result.id)
        self.assertEqual(NAME, result.display_name)

    def test_not_find(self):
        self.assertRaises(exceptions.CommandError, utils.find_resource,
                          self.manager, 'GeorgeMartin')
