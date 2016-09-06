#   Copyright 2014 CERN.
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

import copy
import mock

from osc_lib import exceptions

from openstackclient.identity.v3 import mapping
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestMapping(identity_fakes.TestFederatedIdentity):

    def setUp(self):
        super(TestMapping, self).setUp()

        federation_lib = self.app.client_manager.identity.federation
        self.mapping_mock = federation_lib.mappings
        self.mapping_mock.reset_mock()


class TestMappingCreate(TestMapping):

    def setUp(self):
        super(TestMappingCreate, self).setUp()
        self.mapping_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.MAPPING_RESPONSE),
            loaded=True
        )
        self.cmd = mapping.CreateMapping(self.app, None)

    def test_create_mapping(self):
        arglist = [
            '--rules', identity_fakes.mapping_rules_file_path,
            identity_fakes.mapping_id
        ]
        verifylist = [
            ('mapping', identity_fakes.mapping_id),
            ('rules', identity_fakes.mapping_rules_file_path)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = identity_fakes.MAPPING_RULES
        with mock.patch("openstackclient.identity.v3.mapping."
                        "CreateMapping._read_rules", mocker):
            columns, data = self.cmd.take_action(parsed_args)

        self.mapping_mock.create.assert_called_with(
            mapping_id=identity_fakes.mapping_id,
            rules=identity_fakes.MAPPING_RULES)

        collist = ('id', 'rules')
        self.assertEqual(collist, columns)

        datalist = (identity_fakes.mapping_id,
                    identity_fakes.MAPPING_RULES)
        self.assertEqual(datalist, data)


class TestMappingDelete(TestMapping):

    def setUp(self):
        super(TestMappingDelete, self).setUp()
        self.mapping_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.MAPPING_RESPONSE),
            loaded=True)

        self.mapping_mock.delete.return_value = None
        self.cmd = mapping.DeleteMapping(self.app, None)

    def test_delete_mapping(self):
        arglist = [
            identity_fakes.mapping_id
        ]
        verifylist = [
            ('mapping', [identity_fakes.mapping_id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.mapping_mock.delete.assert_called_with(
            identity_fakes.mapping_id)
        self.assertIsNone(result)


class TestMappingList(TestMapping):

    def setUp(self):
        super(TestMappingList, self).setUp()
        self.mapping_mock.get.return_value = fakes.FakeResource(
            None,
            {'id': identity_fakes.mapping_id},
            loaded=True)
        # Pretend list command returns list of two mappings.
        # NOTE(marek-denis): We are returning FakeResources with mapping id
        # only as ShowMapping class is implemented in a way where rules will
        # not be displayed, only mapping ids.
        self.mapping_mock.list.return_value = [
            fakes.FakeResource(
                None,
                {'id': identity_fakes.mapping_id},
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                {'id': 'extra_mapping'},
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = mapping.ListMapping(self.app, None)

    def test_mapping_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.mapping_mock.list.assert_called_with()

        collist = ('ID',)
        self.assertEqual(collist, columns)

        datalist = [(identity_fakes.mapping_id,), ('extra_mapping',)]
        self.assertEqual(datalist, data)


class TestMappingSet(TestMapping):

    def setUp(self):
        super(TestMappingSet, self).setUp()

        self.mapping_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.MAPPING_RESPONSE),
            loaded=True
        )

        self.mapping_mock.update.return_value = fakes.FakeResource(
            None,
            identity_fakes.MAPPING_RESPONSE_2,
            loaded=True
        )

        # Get the command object to test
        self.cmd = mapping.SetMapping(self.app, None)

    def test_set_new_rules(self):
        arglist = [
            '--rules', identity_fakes.mapping_rules_file_path,
            identity_fakes.mapping_id
        ]
        verifylist = [
            ('mapping', identity_fakes.mapping_id),
            ('rules', identity_fakes.mapping_rules_file_path)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = identity_fakes.MAPPING_RULES_2
        with mock.patch("openstackclient.identity.v3.mapping."
                        "SetMapping._read_rules", mocker):
            columns, data = self.cmd.take_action(parsed_args)
        self.mapping_mock.update.assert_called_with(
            mapping=identity_fakes.mapping_id,
            rules=identity_fakes.MAPPING_RULES_2)

        collist = ('id', 'rules')
        self.assertEqual(collist, columns)
        datalist = (identity_fakes.mapping_id,
                    identity_fakes.MAPPING_RULES_2)
        self.assertEqual(datalist, data)

    def test_set_rules_wrong_file_path(self):
        arglist = [
            '--rules', identity_fakes.mapping_rules_file_path,
            identity_fakes.mapping_id
        ]
        verifylist = [
            ('mapping', identity_fakes.mapping_id),
            ('rules', identity_fakes.mapping_rules_file_path)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)


class TestMappingShow(TestMapping):

    def setUp(self):
        super(TestMappingShow, self).setUp()

        self.mapping_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.MAPPING_RESPONSE),
            loaded=True
        )

        self.cmd = mapping.ShowMapping(self.app, None)

    def test_mapping_show(self):
        arglist = [
            identity_fakes.mapping_id
        ]
        verifylist = [
            ('mapping', identity_fakes.mapping_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.mapping_mock.get.assert_called_with(
            identity_fakes.mapping_id)

        collist = ('id', 'rules')
        self.assertEqual(collist, columns)

        datalist = (identity_fakes.mapping_id,
                    identity_fakes.MAPPING_RULES)
        self.assertEqual(datalist, data)
