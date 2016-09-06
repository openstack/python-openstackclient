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

import six

from openstackclient.common import availability_zone
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


def _build_compute_az_datalist(compute_az, long_datalist=False):
    datalist = ()
    if not long_datalist:
        datalist = (
            compute_az.zoneName,
            'available',
        )
    else:
        for host, services in six.iteritems(compute_az.hosts):
            for service, state in six.iteritems(services):
                datalist += (
                    compute_az.zoneName,
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
            volume_az.zoneName,
            'available',
        )
    else:
        datalist = (
            volume_az.zoneName,
            'available',
            '', '', '', '',
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
            '', '', '',
        )
    return (datalist,)


class TestAvailabilityZone(utils.TestCommand):

    def setUp(self):
        super(TestAvailabilityZone, self).setUp()

        compute_client = compute_fakes.FakeComputev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.compute = compute_client

        self.compute_azs_mock = compute_client.availability_zones
        self.compute_azs_mock.reset_mock()

        volume_client = volume_fakes.FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.volume = volume_client

        self.volume_azs_mock = volume_client.availability_zones
        self.volume_azs_mock.reset_mock()

        network_client = network_fakes.FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.network = network_client

        network_client.availability_zones = mock.Mock()
        network_client.find_extension = mock.Mock()
        self.network_azs_mock = network_client.availability_zones


class TestAvailabilityZoneList(TestAvailabilityZone):

    compute_azs = \
        compute_fakes.FakeAvailabilityZone.create_availability_zones()
    volume_azs = \
        volume_fakes.FakeAvailabilityZone.create_availability_zones(count=1)
    network_azs = \
        network_fakes.FakeAvailabilityZone.create_availability_zones()

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
        super(TestAvailabilityZoneList, self).setUp()

        self.compute_azs_mock.list.return_value = self.compute_azs
        self.volume_azs_mock.list.return_value = self.volume_azs
        self.network_azs_mock.return_value = self.network_azs

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

        self.compute_azs_mock.list.assert_called_with()
        self.volume_azs_mock.list.assert_called_with()
        self.network_azs_mock.assert_called_with()

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

        self.compute_azs_mock.list.assert_called_with()
        self.volume_azs_mock.list.assert_called_with()
        self.network_azs_mock.assert_called_with()

        self.assertEqual(self.long_columnslist, columns)
        datalist = ()
        for compute_az in self.compute_azs:
            datalist += _build_compute_az_datalist(compute_az,
                                                   long_datalist=True)
        for volume_az in self.volume_azs:
            datalist += _build_volume_az_datalist(volume_az,
                                                  long_datalist=True)
        for network_az in self.network_azs:
            datalist += _build_network_az_datalist(network_az,
                                                   long_datalist=True)
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

        self.compute_azs_mock.list.assert_called_with()
        self.volume_azs_mock.list.assert_not_called()
        self.network_azs_mock.assert_not_called()

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

        self.compute_azs_mock.list.assert_not_called()
        self.volume_azs_mock.list.assert_called_with()
        self.network_azs_mock.assert_not_called()

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

        self.compute_azs_mock.list.assert_not_called()
        self.volume_azs_mock.list.assert_not_called()
        self.network_azs_mock.assert_called_with()

        self.assertEqual(self.short_columnslist, columns)
        datalist = ()
        for network_az in self.network_azs:
            datalist += _build_network_az_datalist(network_az)
        self.assertEqual(datalist, tuple(data))
