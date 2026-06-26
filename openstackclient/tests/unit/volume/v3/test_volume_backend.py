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

from openstack.block_storage.v3 import capabilities as _capabilities
from openstack.block_storage.v3 import stats as _stats
from osc_lib.cli import format_columns

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_backend


def _create_fake_capability():
    """Create a fake volume backend capability.

    :param dict attrs:
        A dictionary with all attributes of the Capabilities.
    :return:
        A FakeResource object with capability name and attrs.
    """
    # Set default attribute
    return _capabilities.Capabilities(
        namespace="OS::Storage::Capabilities::fake",
        vendor_name="OpenStack",
        volume_backend_name="lvmdriver-1",
        pool_name="pool",
        driver_version="2.0.0",
        storage_protocol="iSCSI",
        display_name="Capabilities of Cinder LVM driver",
        description="Blah, blah.",
        visibility="public",
        replication_targets=[],
        properties={
            "compression": {
                "title": "Compression",
                "description": "Enables compression.",
                "type": "boolean",
            },
            "qos": {
                "title": "QoS",
                "description": "Enables QoS.",
                "type": "boolean",
            },
            "replication": {
                "title": "Replication",
                "description": "Enables replication.",
                "type": "boolean",
            },
            "thin_provisioning": {
                "title": "Thin Provisioning",
                "description": "Sets thin provisioning.",
                "type": "boolean",
            },
        },
    )


def _create_fake_pool():
    return _stats.Pools(
        name='host@lvmdriver-1#lvmdriver-1',
        capabilities={
            'storage_protocol': 'iSCSI',
            'thick_provisioning_support': False,
            'thin_provisioning_support': True,
            'total_volumes': 99,
            'total_capacity_gb': 1000.00,
            'allocated_capacity_gb': 100,
            'max_over_subscription_ratio': 200.0,
        },
    )


class TestShowVolumeCapability(volume_fakes.TestVolume):
    """Test backend capability functionality."""

    def setUp(self):
        super().setUp()

        self.capability = _create_fake_capability()
        self.volume_client.get_capabilities.return_value = self.capability

        self.cmd = volume_backend.ShowCapability(self.app, None)

    def test_capability_show(self):
        self.set_volume_api_version('3.0')

        arglist = [
            'fake',
        ]
        verifylist = [
            ('host', 'fake'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'Title',
            'Key',
            'Type',
            'Description',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        capabilities = [
            'Compression',
            'Replication',
            'QoS',
            'Thin Provisioning',
        ]

        # confirming if all expected values are present in the result.
        for cap in data:
            self.assertIn(cap[0], capabilities)

        # checking if proper call was made to get capabilities
        self.volume_client.get_capabilities.assert_called_with(
            'fake',
        )


class TestListVolumePool(volume_fakes.TestVolume):
    """Tests for volume backend pool listing."""

    def setUp(self):
        super().setUp()

        self.pool = _create_fake_pool()
        self.volume_client.backend_pools.return_value = [self.pool]

        # Get the command object to test
        self.cmd = volume_backend.ListPool(self.app, None)

    def test_pool_list(self):
        self.set_volume_api_version('3.0')

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'Name',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = ((self.pool.name,),)

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to list pools
        self.volume_client.backend_pools.assert_called_with(
            detailed=False,
        )

        # checking if long columns are present in output
        self.assertNotIn("total_volumes", columns)
        self.assertNotIn("storage_protocol", columns)

    def test_service_list_with_long_option(self):
        self.set_volume_api_version('3.0')

        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'Name',
            'Capabilities',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = (
            (
                self.pool.name,
                format_columns.DictColumn(self.pool.capabilities),
            ),
        )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        self.volume_client.backend_pools.assert_called_with(
            detailed=True,
        )
