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

import six

from openstackclient.common import availability_zone
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests import utils


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
                    host,
                    service,
                    'enabled :-) ' + state['updated_at'],
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


class TestAvailabilityZoneList(TestAvailabilityZone):

    compute_azs = \
        compute_fakes.FakeAvailabilityZone.create_availability_zones()

    def setUp(self):
        super(TestAvailabilityZoneList, self).setUp()

        self.compute_azs_mock.list.return_value = self.compute_azs

        # Get the command object to test
        self.cmd = availability_zone.ListAvailabilityZone(self.app, None)

    def test_availability_zone_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_azs_mock.list.assert_called_with()

        columnslist = ('Zone Name', 'Zone Status')
        self.assertEqual(columnslist, columns)
        datalist = ()
        for compute_az in self.compute_azs:
            datalist += _build_compute_az_datalist(compute_az)
        self.assertEqual(datalist, tuple(data))

    def test_availability_zone_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_azs_mock.list.assert_called_with()

        columnslist = (
            'Zone Name',
            'Zone Status',
            'Host Name',
            'Service Name',
            'Service Status',
        )
        self.assertEqual(columnslist, columns)
        datalist = ()
        for compute_az in self.compute_azs:
            datalist += _build_compute_az_datalist(compute_az,
                                                   long_datalist=True)
        self.assertEqual(datalist, tuple(data))
