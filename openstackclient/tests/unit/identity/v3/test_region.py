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

import copy

from openstackclient.identity.v3 import region
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestRegion(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestRegion, self).setUp()

        # Get a shortcut to the RegionManager Mock
        self.regions_mock = self.app.client_manager.identity.regions
        self.regions_mock.reset_mock()


class TestRegionCreate(TestRegion):

    columns = (
        'description',
        'parent_region',
        'region',
    )
    datalist = (
        identity_fakes.region_description,
        identity_fakes.region_parent_region_id,
        identity_fakes.region_id,
    )

    def setUp(self):
        super(TestRegionCreate, self).setUp()

        self.regions_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGION),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = region.CreateRegion(self.app, None)

    def test_region_create_description(self):
        arglist = [
            identity_fakes.region_id,
            '--description', identity_fakes.region_description,
        ]
        verifylist = [
            ('region', identity_fakes.region_id),
            ('description', identity_fakes.region_description)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': identity_fakes.region_description,
            'id': identity_fakes.region_id,
            'parent_region': None,
        }
        self.regions_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_region_create_no_options(self):
        arglist = [
            identity_fakes.region_id,
        ]
        verifylist = [
            ('region', identity_fakes.region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'id': identity_fakes.region_id,
            'parent_region': None,
        }
        self.regions_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_region_create_parent_region_id(self):
        arglist = [
            identity_fakes.region_id,
            '--parent-region', identity_fakes.region_parent_region_id,
        ]
        verifylist = [
            ('region', identity_fakes.region_id),
            ('parent_region', identity_fakes.region_parent_region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'id': identity_fakes.region_id,
            'parent_region': identity_fakes.region_parent_region_id,
        }
        self.regions_mock.create.assert_called_with(
            **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestRegionDelete(TestRegion):

    def setUp(self):
        super(TestRegionDelete, self).setUp()

        self.regions_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = region.DeleteRegion(self.app, None)

    def test_region_delete_no_options(self):
        arglist = [
            identity_fakes.region_id,
        ]
        verifylist = [
            ('region', [identity_fakes.region_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.regions_mock.delete.assert_called_with(
            identity_fakes.region_id,
        )
        self.assertIsNone(result)


class TestRegionList(TestRegion):

    columns = (
        'Region',
        'Parent Region',
        'Description',
    )
    datalist = (
        (
            identity_fakes.region_id,
            identity_fakes.region_parent_region_id,
            identity_fakes.region_description,
        ),
    )

    def setUp(self):
        super(TestRegionList, self).setUp()

        self.regions_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.REGION),
                loaded=True,
            ),
        ]

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
        self.regions_mock.list.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_region_list_parent_region_id(self):
        arglist = [
            '--parent-region', identity_fakes.region_parent_region_id,
        ]
        verifylist = [
            ('parent_region', identity_fakes.region_parent_region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.regions_mock.list.assert_called_with(
            parent_region_id=identity_fakes.region_parent_region_id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestRegionSet(TestRegion):

    def setUp(self):
        super(TestRegionSet, self).setUp()

        self.regions_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGION),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = region.SetRegion(self.app, None)

    def test_region_set_no_options(self):
        arglist = [
            identity_fakes.region_id,
        ]
        verifylist = [
            ('region', identity_fakes.region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {}
        self.regions_mock.update.assert_called_with(
            identity_fakes.region_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_region_set_description(self):
        arglist = [
            '--description', 'qwerty',
            identity_fakes.region_id,
        ]
        verifylist = [
            ('description', 'qwerty'),
            ('region', identity_fakes.region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'qwerty',
        }
        self.regions_mock.update.assert_called_with(
            identity_fakes.region_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_region_set_parent_region_id(self):
        arglist = [
            '--parent-region', 'new_parent',
            identity_fakes.region_id,
        ]
        verifylist = [
            ('parent_region', 'new_parent'),
            ('region', identity_fakes.region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'parent_region': 'new_parent',
        }
        self.regions_mock.update.assert_called_with(
            identity_fakes.region_id,
            **kwargs
        )
        self.assertIsNone(result)


class TestRegionShow(TestRegion):

    def setUp(self):
        super(TestRegionShow, self).setUp()

        self.regions_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGION),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = region.ShowRegion(self.app, None)

    def test_region_show(self):
        arglist = [
            identity_fakes.region_id,
        ]
        verifylist = [
            ('region', identity_fakes.region_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.regions_mock.get.assert_called_with(
            identity_fakes.region_id,
        )

        collist = ('description', 'parent_region', 'region')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.region_description,
            identity_fakes.region_parent_region_id,
            identity_fakes.region_id,
        )
        self.assertEqual(datalist, data)
