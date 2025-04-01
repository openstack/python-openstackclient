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

from openstackclient.common import availability_zone
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes


def _build_compute_az_datalist(compute_az, long_datalist=False):
    datalist = ()
    if not long_datalist:
        datalist = (
            compute_az.name,
            'available',
        )
    else:
        for host, services in compute_az.hosts.items():
            for service, state in services.items():
                datalist += (
                    compute_az.name,
                    'available',
                    '',
                    host,
                    service,
                    'enabled :-) ' + state['updated_at'],
                )
    return (datalist,)


def _build_volume_az_datalist(volume_az, long_datalist=False):
    datalist = ()
    if not long_datalist:
        datalist = (
            volume_az.name,
            'available',
        )
    else:
        datalist = (
            volume_az.name,
            'available',
            '',
            '',
            '',
            '',
        )
    return (datalist,)


def _build_network_az_datalist(network_az, long_datalist=False):
    datalist = ()
    if not long_datalist:
        datalist = (
            network_az.name,
            network_az.state,
        )
    else:
        datalist = (
            network_az.name,
            network_az.state,
            network_az.resource,
            '',
            '',
            '',
        )
    return (datalist,)


class TestAvailabilityZoneList(
    network_fakes.FakeClientMixin,
    volume_fakes.FakeClientMixin,
    compute_fakes.FakeClientMixin,
    utils.TestCommand,
):
    compute_azs = compute_fakes.create_availability_zones()
    volume_azs = volume_fakes.create_availability_zones(count=1)
    network_azs = network_fakes.create_availability_zones()

    short_columnslist = ('Zone Name', 'Zone Status')
    long_columnslist = (
        'Zone Name',
        'Zone Status',
        'Zone Resource',
        'Host Name',
        'Service Name',
        'Service Status',
    )

    def setUp(self):
        super().setUp()

        self.compute_client.availability_zones.return_value = self.compute_azs
        self.volume_sdk_client.availability_zones.return_value = (
            self.volume_azs
        )
        self.network_client.availability_zones.return_value = self.network_azs

        # Get the command object to test
        self.cmd = availability_zone.ListAvailabilityZone(self.app, None)

    def test_availability_zone_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.availability_zones.assert_called_with(details=True)
        self.volume_sdk_client.availability_zones.assert_called_with()
        self.network_client.availability_zones.assert_called_with()

        self.assertEqual(self.short_columnslist, columns)
        datalist = ()
        for compute_az in self.compute_azs:
            datalist += _build_compute_az_datalist(compute_az)
        for volume_az in self.volume_azs:
            datalist += _build_volume_az_datalist(volume_az)
        for network_az in self.network_azs:
            datalist += _build_network_az_datalist(network_az)
        self.assertEqual(datalist, tuple(data))

    def test_availability_zone_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.availability_zones.assert_called_with(details=True)
        self.volume_sdk_client.availability_zones.assert_called_with()
        self.network_client.availability_zones.assert_called_with()

        self.assertEqual(self.long_columnslist, columns)
        datalist = ()
        for compute_az in self.compute_azs:
            datalist += _build_compute_az_datalist(
                compute_az, long_datalist=True
            )
        for volume_az in self.volume_azs:
            datalist += _build_volume_az_datalist(
                volume_az, long_datalist=True
            )
        for network_az in self.network_azs:
            datalist += _build_network_az_datalist(
                network_az, long_datalist=True
            )
        self.assertEqual(datalist, tuple(data))

    def test_availability_zone_list_compute(self):
        arglist = [
            '--compute',
        ]
        verifylist = [
            ('compute', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.availability_zones.assert_called_with(details=True)
        self.volume_sdk_client.availability_zones.assert_not_called()
        self.network_client.availability_zones.assert_not_called()

        self.assertEqual(self.short_columnslist, columns)
        datalist = ()
        for compute_az in self.compute_azs:
            datalist += _build_compute_az_datalist(compute_az)
        self.assertEqual(datalist, tuple(data))

    def test_availability_zone_list_volume(self):
        arglist = [
            '--volume',
        ]
        verifylist = [
            ('volume', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.availability_zones.assert_not_called()
        self.volume_sdk_client.availability_zones.assert_called_with()
        self.network_client.availability_zones.assert_not_called()

        self.assertEqual(self.short_columnslist, columns)
        datalist = ()
        for volume_az in self.volume_azs:
            datalist += _build_volume_az_datalist(volume_az)
        self.assertEqual(datalist, tuple(data))

    def test_availability_zone_list_network(self):
        arglist = [
            '--network',
        ]
        verifylist = [
            ('network', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.availability_zones.assert_not_called()
        self.volume_sdk_client.availability_zones.assert_not_called()
        self.network_client.availability_zones.assert_called_with()

        self.assertEqual(self.short_columnslist, columns)
        datalist = ()
        for network_az in self.network_azs:
            datalist += _build_network_az_datalist(network_az)
        self.assertEqual(datalist, tuple(data))
