# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.block_storage.v3 import cluster as _cluster
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import block_storage_cluster


class TestBlockStorageClusterList(volume_fakes.TestVolume):
    fake_clusters = list(
        sdk_fakes.generate_fake_resources(_cluster.Cluster, count=2)
    )

    def setUp(self):
        super().setUp()

        self.volume_client.clusters.return_value = self.fake_clusters

        self.cmd = block_storage_cluster.ListBlockStorageCluster(
            self.app, None
        )

    def test_cluster_list(self):
        self.set_volume_api_version('3.7')

        arglist = []
        verifylist = [
            ('cluster', None),
            ('binary', None),
            ('is_up', None),
            ('is_disabled', None),
            ('num_hosts', None),
            ('num_down_hosts', None),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = ('Name', 'Binary', 'State', 'Status')
        expected_data = tuple(
            (
                cluster.name,
                cluster.binary,
                cluster.state,
                cluster.status,
            )
            for cluster in self.fake_clusters
        )
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_client.clusters.assert_called_once_with(
            name=None,
            binary=None,
            is_up=None,
            disabled=None,
            num_hosts=None,
            num_down_hosts=None,
            details=False,
        )

    def test_cluster_list_with_full_options(self):
        self.set_volume_api_version('3.7')

        arglist = [
            '--cluster',
            'foo',
            '--binary',
            'bar',
            '--up',
            '--disabled',
            '--num-hosts',
            '5',
            '--num-down-hosts',
            '0',
            '--long',
        ]
        verifylist = [
            ('cluster', 'foo'),
            ('binary', 'bar'),
            ('is_up', True),
            ('is_disabled', True),
            ('num_hosts', 5),
            ('num_down_hosts', 0),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = (
            'Name',
            'Binary',
            'State',
            'Status',
            'Num Hosts',
            'Num Down Hosts',
            'Last Heartbeat',
            'Disabled Reason',
            'Created At',
            'Updated At',
        )
        expected_data = tuple(
            (
                cluster.name,
                cluster.binary,
                cluster.state,
                cluster.status,
                cluster.num_hosts,
                cluster.num_down_hosts,
                cluster.last_heartbeat,
                cluster.disabled_reason,
                cluster.created_at,
                cluster.updated_at,
            )
            for cluster in self.fake_clusters
        )
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_client.clusters.assert_called_once_with(
            name='foo',
            binary='bar',
            is_up=True,
            disabled=True,
            num_hosts=5,
            num_down_hosts=0,
            details=True,
        )

    def test_cluster_list_pre_v37(self):
        self.set_volume_api_version('3.6')

        arglist = []
        verifylist = [
            ('cluster', None),
            ('binary', None),
            ('is_up', None),
            ('is_disabled', None),
            ('num_hosts', None),
            ('num_down_hosts', None),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.7 or greater is required', str(exc)
        )


class TestBlockStorageClusterSet(volume_fakes.TestVolume):
    cluster = sdk_fakes.generate_fake_resource(_cluster.Cluster)
    columns = (
        'Name',
        'Binary',
        'State',
        'Status',
        'Disabled Reason',
        'Hosts',
        'Down Hosts',
        'Last Heartbeat',
        'Created At',
        'Updated At',
        'Replication Status',
        'Frozen',
        'Active Backend ID',
    )
    data = (
        cluster.name,
        cluster.binary,
        cluster.state,
        cluster.status,
        cluster.disabled_reason,
        cluster.num_hosts,
        cluster.num_down_hosts,
        cluster.last_heartbeat,
        cluster.created_at,
        cluster.updated_at,
        cluster.replication_status,
        cluster.frozen,
        cluster.active_backend_id,
    )

    def setUp(self):
        super().setUp()

        self.volume_client.enable_cluster.return_value = self.cluster
        self.volume_client.disable_cluster.return_value = self.cluster

        self.cmd = block_storage_cluster.SetBlockStorageCluster(self.app, None)

    def test_cluster_set_enable(self):
        self.set_volume_api_version('3.7')

        arglist = [
            '--enable',
            self.cluster.name,
        ]
        verifylist = [
            ('cluster', self.cluster.name),
            ('binary', 'cinder-volume'),
            ('disabled', False),
            ('disabled_reason', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

        self.volume_client.enable_cluster.assert_called_once_with(
            _cluster.Cluster(name=self.cluster.name, binary='cinder-volume')
        )
        self.volume_client.disable_cluster.assert_not_called()

    def test_cluster_set_disable_with_reason(self):
        self.set_volume_api_version('3.7')

        arglist = [
            '--binary',
            self.cluster.binary,
            '--disable',
            '--disable-reason',
            'foo',
            self.cluster.name,
        ]
        verifylist = [
            ('cluster', self.cluster.name),
            ('binary', self.cluster.binary),
            ('disabled', True),
            ('disabled_reason', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

        self.volume_client.disable_cluster.assert_called_once_with(
            _cluster.Cluster(
                name=self.cluster.name, binary=self.cluster.binary
            ),
            reason='foo',
        )
        self.volume_client.enable_cluster.assert_not_called()

    def test_cluster_set_only_with_disable_reason(self):
        self.set_volume_api_version('3.7')

        arglist = [
            '--disable-reason',
            'foo',
            self.cluster.name,
        ]
        verifylist = [
            ('cluster', self.cluster.name),
            ('binary', 'cinder-volume'),
            ('disabled', None),
            ('disabled_reason', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            "Cannot specify --disable-reason without --disable", str(exc)
        )

    def test_cluster_set_enable_with_disable_reason(self):
        self.set_volume_api_version('3.7')

        arglist = [
            '--enable',
            '--disable-reason',
            'foo',
            self.cluster.name,
        ]
        verifylist = [
            ('cluster', self.cluster.name),
            ('binary', 'cinder-volume'),
            ('disabled', False),
            ('disabled_reason', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            "Cannot specify --disable-reason without --disable", str(exc)
        )

    def test_cluster_set_pre_v37(self):
        self.set_volume_api_version('3.6')

        arglist = [
            '--enable',
            self.cluster.name,
        ]
        verifylist = [
            ('cluster', self.cluster.name),
            ('binary', 'cinder-volume'),
            ('disabled', False),
            ('disabled_reason', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.7 or greater is required', str(exc)
        )


class TestBlockStorageClusterShow(volume_fakes.TestVolume):
    cluster = sdk_fakes.generate_fake_resource(_cluster.Cluster)
    columns = (
        'Name',
        'Binary',
        'State',
        'Status',
        'Disabled Reason',
        'Hosts',
        'Down Hosts',
        'Last Heartbeat',
        'Created At',
        'Updated At',
        'Replication Status',
        'Frozen',
        'Active Backend ID',
    )
    data = (
        cluster.name,
        cluster.binary,
        cluster.state,
        cluster.status,
        cluster.disabled_reason,
        cluster.num_hosts,
        cluster.num_down_hosts,
        cluster.last_heartbeat,
        cluster.created_at,
        cluster.updated_at,
        cluster.replication_status,
        cluster.frozen,
        cluster.active_backend_id,
    )

    def setUp(self):
        super().setUp()

        self.volume_client.get_cluster.return_value = self.cluster

        self.cmd = block_storage_cluster.ShowBlockStorageCluster(
            self.app, None
        )

    def test_cluster_show(self):
        self.set_volume_api_version('3.7')

        arglist = [
            self.cluster.name,
        ]
        verifylist = [
            ('cluster', self.cluster.name),
            ('binary', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

        self.volume_client.get_cluster.assert_called_once_with(
            self.cluster.name
        )

    def test_cluster_show_pre_v37(self):
        self.set_volume_api_version('3.6')

        arglist = [
            self.cluster.name,
        ]
        verifylist = [
            ('cluster', self.cluster.name),
            ('binary', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.7 or greater is required', str(exc)
        )
