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


from openstack.identity.v3 import region as _region
from openstack.test import fakes as sdk_fakes

from openstackclient.identity.v3 import region
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestRegionCreate(identity_fakes.TestIdentityv3):
    region = sdk_fakes.generate_fake_resource(_region.Region)
    columns = (
        'region',
        'description',
        'parent_region',
    )
    datalist = (
        region.id,
        region.description,
        region.parent_region_id,
    )

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.create_region.return_value = self.region

        # Get the command object to test
        self.cmd = region.CreateRegion(self.app, None)

    def test_region_create_description(self):
        arglist = [
            self.region.id,
            '--description',
            self.region.description,
        ]
        verifylist = [
            ('region', self.region.id),
            ('description', self.region.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.region.description,
            'id': self.region.id,
            'parent_region_id': None,
        }
        self.identity_sdk_client.create_region.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_region_create_no_options(self):
        arglist = [
            self.region.id,
        ]
        verifylist = [
            ('region', self.region.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'id': self.region.id,
            'parent_region_id': None,
        }
        self.identity_sdk_client.create_region.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_region_create_parent_region_id(self):
        arglist = [
            self.region.id,
            '--parent-region',
            self.region.parent_region_id,
        ]
        verifylist = [
            ('region', self.region.id),
            ('parent_region', self.region.parent_region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'id': self.region.id,
            'parent_region_id': self.region.parent_region_id,
        }
        self.identity_sdk_client.create_region.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestRegionDelete(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.region = sdk_fakes.generate_fake_resource(_region.Region)
        self.identity_sdk_client.delete_region.return_value = None

        # Get the command object to test
        self.cmd = region.DeleteRegion(self.app, None)

    def test_region_delete_no_options(self):
        arglist = [
            self.region.id,
        ]
        verifylist = [
            ('region', [self.region.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_region.assert_called_with(
            self.region.id,
        )
        self.assertIsNone(result)


class TestRegionList(identity_fakes.TestIdentityv3):
    region = sdk_fakes.generate_fake_resource(_region.Region)
    columns = (
        'Region',
        'Parent Region',
        'Description',
    )
    datalist = (
        (
            region.id,
            region.parent_region_id,
            region.description,
        ),
    )

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.regions.return_value = [self.region]

        # Get the command object to test
        self.cmd = region.ListRegion(self.app, None)

    def test_region_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.regions.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_region_list_parent_region_id(self):
        arglist = [
            '--parent-region',
            self.region.parent_region_id,
        ]
        verifylist = [
            ('parent_region', self.region.parent_region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.regions.assert_called_with(
            parent_region_id=self.region.parent_region_id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestRegionSet(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.region = sdk_fakes.generate_fake_resource(_region.Region)

        # Get the command object to test
        self.cmd = region.SetRegion(self.app, None)

    def test_region_set_no_options(self):
        arglist = [
            self.region.id,
        ]
        verifylist = [
            ('region', self.region.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {}
        self.identity_sdk_client.update_region.assert_called_with(
            self.region.id, **kwargs
        )
        self.assertIsNone(result)

    def test_region_set_description(self):
        arglist = [
            '--description',
            'qwerty',
            self.region.id,
        ]
        verifylist = [
            ('description', 'qwerty'),
            ('region', self.region.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'qwerty',
        }
        self.identity_sdk_client.update_region.assert_called_with(
            self.region.id, **kwargs
        )
        self.assertIsNone(result)

    def test_region_set_parent_region_id(self):
        arglist = [
            '--parent-region',
            'new_parent',
            self.region.id,
        ]
        verifylist = [
            ('parent_region', 'new_parent'),
            ('region', self.region.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'parent_region_id': 'new_parent',
        }
        self.identity_sdk_client.update_region.assert_called_with(
            self.region.id, **kwargs
        )
        self.assertIsNone(result)


class TestRegionShow(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.region = sdk_fakes.generate_fake_resource(_region.Region)
        self.identity_sdk_client.get_region.return_value = self.region

        # Get the command object to test
        self.cmd = region.ShowRegion(self.app, None)

    def test_region_show(self):
        arglist = [
            self.region.id,
        ]
        verifylist = [
            ('region', self.region.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.get_region.assert_called_with(
            self.region.id,
        )

        collist = ('region', 'description', 'parent_region')
        self.assertEqual(collist, columns)
        datalist = (
            self.region.id,
            self.region.description,
            self.region.parent_region_id,
        )
        self.assertEqual(datalist, data)
