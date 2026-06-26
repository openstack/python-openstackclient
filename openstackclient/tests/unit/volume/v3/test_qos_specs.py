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

from unittest.mock import call

from openstack.block_storage.v3 import qos_spec as _qos_spec
from openstack.block_storage.v3 import type as _type
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import qos_specs


class TestQosAssociate(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.qos_spec = sdk_fakes.generate_fake_resource(
            _qos_spec.QoSSpec,
            consumer='front-end',
            specs={'foo': 'bar', 'iops': '9001'},
        )

        self.volume_sdk_client.find_qos_spec.return_value = self.qos_spec
        self.volume_sdk_client.find_type.return_value = self.volume_type
        self.cmd = qos_specs.AssociateQos(self.app, None)

    def test_qos_associate(self):
        arglist = [self.qos_spec.id, self.volume_type.id]
        verifylist = [
            ('qos_spec', self.qos_spec.id),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_qos_spec.assert_called_once_with(
            self.qos_spec.id, ignore_missing=False
        )
        self.volume_sdk_client.find_type.assert_called_once_with(
            self.volume_type.id, ignore_missing=False
        )
        self.volume_sdk_client.associate_qos_spec.assert_called_once_with(
            self.qos_spec.id, self.volume_type.id
        )
        self.assertIsNone(result)


class TestQosCreate(volume_fakes.TestVolume):
    columns = ('consumer', 'id', 'name', 'properties')

    def setUp(self):
        super().setUp()

        self.new_qos_spec = sdk_fakes.generate_fake_resource(
            _qos_spec.QoSSpec,
            consumer='front-end',
            specs={'foo': 'bar', 'iops': '9001'},
        )
        self.volume_sdk_client.create_qos_spec.return_value = self.new_qos_spec

        self.data = (
            self.new_qos_spec.consumer,
            self.new_qos_spec.id,
            self.new_qos_spec.name,
            format_columns.DictColumn(self.new_qos_spec.specs),
        )

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

        self.volume_sdk_client.create_qos_spec.assert_called_once_with(
            name=self.new_qos_spec.name, consumer='both'
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

        self.volume_sdk_client.create_qos_spec.assert_called_once_with(
            name=self.new_qos_spec.name,
            consumer=self.new_qos_spec.consumer,
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
            ('properties', self.new_qos_spec.specs),
            ('name', self.new_qos_spec.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_qos_spec.assert_called_once_with(
            name=self.new_qos_spec.name,
            consumer=self.new_qos_spec.consumer,
            foo='bar',
            iops='9001',
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestQosDelete(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.qos_specs = [
            sdk_fakes.generate_fake_resource(_qos_spec.QoSSpec, specs={}),
            sdk_fakes.generate_fake_resource(_qos_spec.QoSSpec, specs={}),
        ]
        qos_by_id = {q.id: q for q in self.qos_specs}
        self.volume_sdk_client.find_qos_spec.side_effect = lambda x, **kwargs: (
            qos_by_id[x]
        )
        self.cmd = qos_specs.DeleteQos(self.app, None)

    def test_qos_delete(self):
        arglist = [self.qos_specs[0].id]
        verifylist = [('qos_specs', [self.qos_specs[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_qos_spec.assert_called_once_with(
            self.qos_specs[0].id, ignore_missing=False, force=False
        )
        self.assertIsNone(result)

    def test_qos_delete_with_force(self):
        arglist = ['--force', self.qos_specs[0].id]
        verifylist = [('force', True), ('qos_specs', [self.qos_specs[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_qos_spec.assert_called_once_with(
            self.qos_specs[0].id, ignore_missing=False, force=True
        )
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
            calls.append(call(q.id, ignore_missing=False, force=False))
        self.volume_sdk_client.delete_qos_spec.assert_has_calls(calls)
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

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 QoS specifications failed to delete.', str(e)
            )

        self.volume_sdk_client.delete_qos_spec.assert_called_once_with(
            self.qos_specs[0].id, ignore_missing=False, force=False
        )


class TestQosDisassociate(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.qos_spec = sdk_fakes.generate_fake_resource(
            _qos_spec.QoSSpec, consumer='front-end', specs={}
        )

        self.volume_sdk_client.find_qos_spec.return_value = self.qos_spec
        self.volume_sdk_client.find_type.return_value = self.volume_type
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

        self.volume_sdk_client.disassociate_qos_spec.assert_called_once_with(
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

        self.volume_sdk_client.disassociate_all_qos_spec.assert_called_once_with(
            self.qos_spec.id
        )
        self.assertIsNone(result)


class TestQosList(volume_fakes.TestVolume):
    columns = (
        'ID',
        'Name',
        'Consumer',
        'Associations',
        'Properties',
    )

    def setUp(self):
        super().setUp()

        self.qos_specs = [
            sdk_fakes.generate_fake_resource(
                _qos_spec.QoSSpec,
                consumer='front-end',
                specs={'foo': 'bar', 'iops': '9001'},
            ),
            sdk_fakes.generate_fake_resource(
                _qos_spec.QoSSpec,
                consumer='front-end',
                specs={'foo': 'bar', 'iops': '9001'},
            ),
        ]
        self.qos_association = sdk_fakes.generate_fake_resource(
            _qos_spec.QoSSpecAssociation
        )
        self.volume_sdk_client.qos_specs.return_value = self.qos_specs
        self.volume_sdk_client.qos_spec_associations.return_value = [
            self.qos_association
        ]

        self.data = []
        for q in self.qos_specs:
            self.data.append(
                (
                    q.id,
                    q.name,
                    q.consumer,
                    format_columns.ListColumn([self.qos_association.name]),
                    format_columns.DictColumn(q.specs),
                )
            )

        self.cmd = qos_specs.ListQos(self.app, None)

    def test_qos_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.qos_specs.assert_called_once_with()

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))


class TestQosSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.qos_spec = sdk_fakes.generate_fake_resource(
            _qos_spec.QoSSpec,
            consumer='front-end',
            specs={'foo': 'bar', 'iops': '9001'},
        )

        self.volume_sdk_client.find_qos_spec.return_value = self.qos_spec
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
            ('properties', new_property),
            ('qos_spec', self.qos_spec.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_qos_spec_metadata.assert_called_once_with(
            self.qos_spec.id,
            list(self.qos_spec.specs.keys()),
        )
        self.volume_sdk_client.update_qos_spec.assert_called_once_with(
            self.qos_spec.id, a='b', c='d'
        )
        self.assertIsNone(result)


class TestQosShow(volume_fakes.TestVolume):
    columns = ('associations', 'consumer', 'id', 'name', 'properties')

    def setUp(self):
        super().setUp()

        self.qos_spec = sdk_fakes.generate_fake_resource(
            _qos_spec.QoSSpec,
            consumer='front-end',
            specs={'foo': 'bar', 'iops': '9001'},
        )
        self.qos_association = sdk_fakes.generate_fake_resource(
            _qos_spec.QoSSpecAssociation
        )
        self.volume_sdk_client.find_qos_spec.return_value = self.qos_spec
        self.volume_sdk_client.qos_spec_associations.return_value = [
            self.qos_association
        ]

        self.data = (
            format_columns.ListColumn([self.qos_association.name]),
            self.qos_spec.consumer,
            self.qos_spec.id,
            self.qos_spec.name,
            format_columns.DictColumn(self.qos_spec.specs),
        )

        self.cmd = qos_specs.ShowQos(self.app, None)

    def test_qos_show(self):
        arglist = [self.qos_spec.id]
        verifylist = [('qos_spec', self.qos_spec.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.find_qos_spec.assert_called_once_with(
            self.qos_spec.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, tuple(data))


class TestQosUnset(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.qos_spec = sdk_fakes.generate_fake_resource(
            _qos_spec.QoSSpec, consumer='front-end', specs={}
        )
        self.volume_sdk_client.find_qos_spec.return_value = self.qos_spec
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
            ('properties', ['iops', 'foo']),
            ('qos_spec', self.qos_spec.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_qos_spec_metadata.assert_called_once_with(
            self.qos_spec.id, ['iops', 'foo']
        )
        self.assertIsNone(result)
