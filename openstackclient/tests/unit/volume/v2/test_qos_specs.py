#   Copyright 2015 iWeb Technologies Inc.
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

import copy
from unittest import mock
from unittest.mock import call

from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import qos_specs


class TestQos(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.qos_mock = self.volume_client.qos_specs
        self.qos_mock.reset_mock()

        self.types_mock = self.volume_client.volume_types
        self.types_mock.reset_mock()


class TestQosAssociate(TestQos):
    volume_type = volume_fakes.create_one_volume_type()
    qos_spec = volume_fakes.create_one_qos()

    def setUp(self):
        super().setUp()

        self.qos_mock.get.return_value = self.qos_spec
        self.types_mock.get.return_value = self.volume_type
        # Get the command object to test
        self.cmd = qos_specs.AssociateQos(self.app, None)

    def test_qos_associate(self):
        arglist = [self.qos_spec.id, self.volume_type.id]
        verifylist = [
            ('qos_spec', self.qos_spec.id),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.associate.assert_called_with(
            self.qos_spec.id, self.volume_type.id
        )
        self.assertIsNone(result)


class TestQosCreate(TestQos):
    columns = ('consumer', 'id', 'name', 'properties')

    def setUp(self):
        super().setUp()

        self.new_qos_spec = volume_fakes.create_one_qos()
        self.qos_mock.create.return_value = self.new_qos_spec

        self.data = (
            self.new_qos_spec.consumer,
            self.new_qos_spec.id,
            self.new_qos_spec.name,
            format_columns.DictColumn(self.new_qos_spec.specs),
        )

        # Get the command object to test
        self.cmd = qos_specs.CreateQos(self.app, None)

    def test_qos_create_without_properties(self):
        arglist = [
            self.new_qos_spec.name,
        ]
        verifylist = [
            ('name', self.new_qos_spec.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.qos_mock.create.assert_called_with(
            self.new_qos_spec.name, {'consumer': 'both'}
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_qos_create_with_consumer(self):
        arglist = [
            '--consumer',
            self.new_qos_spec.consumer,
            self.new_qos_spec.name,
        ]
        verifylist = [
            ('consumer', self.new_qos_spec.consumer),
            ('name', self.new_qos_spec.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.qos_mock.create.assert_called_with(
            self.new_qos_spec.name, {'consumer': self.new_qos_spec.consumer}
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_qos_create_with_properties(self):
        arglist = [
            '--consumer',
            self.new_qos_spec.consumer,
            '--property',
            'foo=bar',
            '--property',
            'iops=9001',
            self.new_qos_spec.name,
        ]
        verifylist = [
            ('consumer', self.new_qos_spec.consumer),
            ('property', self.new_qos_spec.specs),
            ('name', self.new_qos_spec.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.qos_mock.create.assert_called_with(
            self.new_qos_spec.name,
            {
                'consumer': self.new_qos_spec.consumer,
                'foo': 'bar',
                'iops': '9001',
            },
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestQosDelete(TestQos):
    qos_specs = volume_fakes.create_qoses(count=2)

    def setUp(self):
        super().setUp()

        self.qos_mock.get = volume_fakes.get_qoses(self.qos_specs)
        # Get the command object to test
        self.cmd = qos_specs.DeleteQos(self.app, None)

    def test_qos_delete(self):
        arglist = [self.qos_specs[0].id]
        verifylist = [('qos_specs', [self.qos_specs[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.delete.assert_called_with(self.qos_specs[0].id, False)
        self.assertIsNone(result)

    def test_qos_delete_with_force(self):
        arglist = ['--force', self.qos_specs[0].id]
        verifylist = [('force', True), ('qos_specs', [self.qos_specs[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.delete.assert_called_with(self.qos_specs[0].id, True)
        self.assertIsNone(result)

    def test_delete_multiple_qoses(self):
        arglist = []
        for q in self.qos_specs:
            arglist.append(q.id)
        verifylist = [
            ('qos_specs', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for q in self.qos_specs:
            calls.append(call(q.id, False))
        self.qos_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_qoses_with_exception(self):
        arglist = [
            self.qos_specs[0].id,
            'unexist_qos',
        ]
        verifylist = [
            ('qos_specs', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.qos_specs[0], exceptions.CommandError]
        with mock.patch.object(
            utils, 'find_resource', side_effect=find_mock_result
        ) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual(
                    '1 of 2 QoS specifications failed to delete.', str(e)
                )

            find_mock.assert_any_call(self.qos_mock, self.qos_specs[0].id)
            find_mock.assert_any_call(self.qos_mock, 'unexist_qos')

            self.assertEqual(2, find_mock.call_count)
            self.qos_mock.delete.assert_called_once_with(
                self.qos_specs[0].id, False
            )


class TestQosDisassociate(TestQos):
    volume_type = volume_fakes.create_one_volume_type()
    qos_spec = volume_fakes.create_one_qos()

    def setUp(self):
        super().setUp()

        self.qos_mock.get.return_value = self.qos_spec
        self.types_mock.get.return_value = self.volume_type
        # Get the command object to test
        self.cmd = qos_specs.DisassociateQos(self.app, None)

    def test_qos_disassociate_with_volume_type(self):
        arglist = [
            '--volume-type',
            self.volume_type.id,
            self.qos_spec.id,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
            ('qos_spec', self.qos_spec.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.disassociate.assert_called_with(
            self.qos_spec.id, self.volume_type.id
        )
        self.assertIsNone(result)

    def test_qos_disassociate_with_all_volume_types(self):
        arglist = [
            '--all',
            self.qos_spec.id,
        ]
        verifylist = [('qos_spec', self.qos_spec.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.disassociate_all.assert_called_with(self.qos_spec.id)
        self.assertIsNone(result)


class TestQosList(TestQos):
    qos_specs = volume_fakes.create_qoses(count=2)
    qos_association = volume_fakes.create_one_qos_association()

    columns = (
        'ID',
        'Name',
        'Consumer',
        'Associations',
        'Properties',
    )
    data = []
    for q in qos_specs:
        data.append(
            (
                q.id,
                q.name,
                q.consumer,
                format_columns.ListColumn([qos_association.name]),
                format_columns.DictColumn(q.specs),
            )
        )

    def setUp(self):
        super().setUp()

        self.qos_mock.list.return_value = self.qos_specs
        self.qos_mock.get_associations.return_value = [self.qos_association]

        # Get the command object to test
        self.cmd = qos_specs.ListQos(self.app, None)

    def test_qos_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.qos_mock.list.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_qos_list_no_association(self):
        self.qos_mock.reset_mock()
        self.qos_mock.get_associations.side_effect = [
            [self.qos_association],
            exceptions.NotFound("NotFound"),
        ]

        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.qos_mock.list.assert_called_with()

        self.assertEqual(self.columns, columns)

        ex_data = copy.deepcopy(self.data)
        ex_data[1] = (
            self.qos_specs[1].id,
            self.qos_specs[1].name,
            self.qos_specs[1].consumer,
            format_columns.ListColumn(None),
            format_columns.DictColumn(self.qos_specs[1].specs),
        )
        self.assertCountEqual(ex_data, list(data))


class TestQosSet(TestQos):
    qos_spec = volume_fakes.create_one_qos()

    def setUp(self):
        super().setUp()

        self.qos_mock.get.return_value = self.qos_spec
        # Get the command object to test
        self.cmd = qos_specs.SetQos(self.app, None)

    def test_qos_set_with_properties_with_id(self):
        arglist = [
            '--no-property',
            '--property',
            'a=b',
            '--property',
            'c=d',
            self.qos_spec.id,
        ]
        new_property = {"a": "b", "c": "d"}
        verifylist = [
            ('no_property', True),
            ('property', new_property),
            ('qos_spec', self.qos_spec.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.unset_keys.assert_called_with(
            self.qos_spec.id,
            list(self.qos_spec.specs.keys()),
        )
        self.qos_mock.set_keys.assert_called_with(
            self.qos_spec.id, {"a": "b", "c": "d"}
        )
        self.assertIsNone(result)


class TestQosShow(TestQos):
    qos_spec = volume_fakes.create_one_qos()
    qos_association = volume_fakes.create_one_qos_association()

    columns = ('associations', 'consumer', 'id', 'name', 'properties')
    data = (
        format_columns.ListColumn([qos_association.name]),
        qos_spec.consumer,
        qos_spec.id,
        qos_spec.name,
        format_columns.DictColumn(qos_spec.specs),
    )

    def setUp(self):
        super().setUp()

        self.qos_mock.get.return_value = self.qos_spec
        self.qos_mock.get_associations.return_value = [self.qos_association]

        # Get the command object to test
        self.cmd = qos_specs.ShowQos(self.app, None)

    def test_qos_show(self):
        arglist = [self.qos_spec.id]
        verifylist = [('qos_spec', self.qos_spec.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.qos_mock.get.assert_called_with(self.qos_spec.id)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, tuple(data))


class TestQosUnset(TestQos):
    qos_spec = volume_fakes.create_one_qos()

    def setUp(self):
        super().setUp()

        self.qos_mock.get.return_value = self.qos_spec
        # Get the command object to test
        self.cmd = qos_specs.UnsetQos(self.app, None)

    def test_qos_unset_with_properties(self):
        arglist = [
            '--property',
            'iops',
            '--property',
            'foo',
            self.qos_spec.id,
        ]
        verifylist = [
            ('property', ['iops', 'foo']),
            ('qos_spec', self.qos_spec.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.unset_keys.assert_called_with(
            self.qos_spec.id, ['iops', 'foo']
        )
        self.assertIsNone(result)
