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

from openstackclient.common import utils
from openstackclient.tests import fakes
from openstackclient.tests.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import qos_specs


class TestQos(volume_fakes.TestVolume):

    def setUp(self):
        super(TestQos, self).setUp()

        self.qos_mock = self.app.client_manager.volume.qos_specs
        self.qos_mock.reset_mock()

        self.types_mock = self.app.client_manager.volume.volume_types
        self.types_mock.reset_mock()


class TestQosAssociate(TestQos):
    def setUp(self):
        super(TestQosAssociate, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.AssociateQos(self.app, None)

    def test_qos_associate(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )
        self.types_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.TYPE),
            loaded=True
        )
        arglist = [
            volume_fakes.qos_id,
            volume_fakes.type_id
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id),
            ('volume_type', volume_fakes.type_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.qos_mock.associate.assert_called_with(
            volume_fakes.qos_id,
            volume_fakes.type_id
        )


class TestQosCreate(TestQos):
    def setUp(self):
        super(TestQosCreate, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.CreateQos(self.app, None)

    def test_qos_create_without_properties(self):
        self.qos_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_DEFAULT_CONSUMER),
            loaded=True
        )

        arglist = [
            volume_fakes.qos_name,
        ]
        verifylist = [
            ('name', volume_fakes.qos_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.qos_mock.create.assert_called_with(
            volume_fakes.qos_name,
            {'consumer': volume_fakes.qos_default_consumer}
        )

        collist = (
            'consumer',
            'id',
            'name'
        )
        self.assertEqual(collist, columns)
        datalist = (
            volume_fakes.qos_default_consumer,
            volume_fakes.qos_id,
            volume_fakes.qos_name
        )
        self.assertEqual(datalist, data)

    def test_qos_create_with_consumer(self):
        self.qos_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )

        arglist = [
            volume_fakes.qos_name,
            '--consumer', volume_fakes.qos_consumer
        ]
        verifylist = [
            ('name', volume_fakes.qos_name),
            ('consumer', volume_fakes.qos_consumer)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.qos_mock.create.assert_called_with(
            volume_fakes.qos_name,
            {'consumer': volume_fakes.qos_consumer}
        )

        collist = (
            'consumer',
            'id',
            'name'
        )
        self.assertEqual(collist, columns)
        datalist = (
            volume_fakes.qos_consumer,
            volume_fakes.qos_id,
            volume_fakes.qos_name
        )
        self.assertEqual(datalist, data)

    def test_qos_create_with_properties(self):
        self.qos_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_WITH_SPECS),
            loaded=True
        )

        arglist = [
            volume_fakes.qos_name,
            '--consumer', volume_fakes.qos_consumer,
            '--property', 'foo=bar',
            '--property', 'iops=9001'
        ]
        verifylist = [
            ('name', volume_fakes.qos_name),
            ('consumer', volume_fakes.qos_consumer),
            ('property', volume_fakes.qos_specs)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        specs = volume_fakes.qos_specs.copy()
        specs.update({'consumer': volume_fakes.qos_consumer})
        self.qos_mock.create.assert_called_with(
            volume_fakes.qos_name,
            specs
        )

        collist = (
            'consumer',
            'id',
            'name',
            'specs',
        )
        self.assertEqual(collist, columns)
        datalist = (
            volume_fakes.qos_consumer,
            volume_fakes.qos_id,
            volume_fakes.qos_name,
            volume_fakes.qos_specs,
        )
        self.assertEqual(datalist, data)


class TestQosDelete(TestQos):
    def setUp(self):
        super(TestQosDelete, self).setUp()

        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = qos_specs.DeleteQos(self.app, None)

    def test_qos_delete_with_id(self):
        arglist = [
            volume_fakes.qos_id
        ]
        verifylist = [
            ('qos_specs', [volume_fakes.qos_id])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.qos_mock.delete.assert_called_with(volume_fakes.qos_id)

    def test_qos_delete_with_name(self):
        arglist = [
            volume_fakes.qos_name
        ]
        verifylist = [
            ('qos_specs', [volume_fakes.qos_name])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.qos_mock.delete.assert_called_with(volume_fakes.qos_id)


class TestQosDisassociate(TestQos):
    def setUp(self):
        super(TestQosDisassociate, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.DisassociateQos(self.app, None)

    def test_qos_disassociate_with_volume_type(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )
        self.types_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.TYPE),
            loaded=True
        )
        arglist = [
            volume_fakes.qos_id,
            '--volume-type', volume_fakes.type_id
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id),
            ('volume_type', volume_fakes.type_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.qos_mock.disassociate.assert_called_with(
            volume_fakes.qos_id,
            volume_fakes.type_id
        )

    def test_qos_disassociate_with_all_volume_types(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )

        arglist = [
            volume_fakes.qos_id,
            '--all'
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.qos_mock.disassociate_all.assert_called_with(volume_fakes.qos_id)


class TestQosList(TestQos):
    def setUp(self):
        super(TestQosList, self).setUp()

        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_WITH_ASSOCIATIONS),
            loaded=True,
        )
        self.qos_mock.list.return_value = [self.qos_mock.get.return_value]
        self.qos_mock.get_associations.return_value = [fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.qos_association),
            loaded=True,
        )]

        # Get the command object to test
        self.cmd = qos_specs.ListQos(self.app, None)

    def test_qos_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.qos_mock.list.assert_called_with()

        collist = (
            'ID',
            'Name',
            'Consumer',
            'Associations',
            'Specs',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            volume_fakes.qos_id,
            volume_fakes.qos_name,
            volume_fakes.qos_consumer,
            volume_fakes.type_name,
            utils.format_dict(volume_fakes.qos_specs),
        ), )
        self.assertEqual(datalist, tuple(data))


class TestQosSet(TestQos):
    def setUp(self):
        super(TestQosSet, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.SetQos(self.app, None)

    def test_qos_set_with_properties_with_id(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_WITH_SPECS),
            loaded=True
        )
        arglist = [
            volume_fakes.qos_id,
            '--property', 'foo=bar',
            '--property', 'iops=9001'
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id),
            ('property', volume_fakes.qos_specs)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.qos_mock.set_keys.assert_called_with(
            volume_fakes.qos_id,
            volume_fakes.qos_specs
        )


class TestQosShow(TestQos):
    def setUp(self):
        super(TestQosShow, self).setUp()

        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_WITH_ASSOCIATIONS),
            loaded=True,
        )
        self.qos_mock.get_associations.return_value = [fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.qos_association),
            loaded=True,
        )]

        # Get the command object to test
        self.cmd = qos_specs.ShowQos(self.app, None)

    def test_qos_show(self):
        arglist = [
            volume_fakes.qos_id
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.qos_mock.get.assert_called_with(
            volume_fakes.qos_id
        )

        collist = (
            'associations',
            'consumer',
            'id',
            'name',
            'specs'
        )
        self.assertEqual(collist, columns)
        datalist = (
            volume_fakes.type_name,
            volume_fakes.qos_consumer,
            volume_fakes.qos_id,
            volume_fakes.qos_name,
            utils.format_dict(volume_fakes.qos_specs),
        )
        self.assertEqual(datalist, tuple(data))


class TestQosUnset(TestQos):
    def setUp(self):
        super(TestQosUnset, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.UnsetQos(self.app, None)

    def test_qos_unset_with_properties(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )
        arglist = [
            volume_fakes.qos_id,
            '--property', 'iops',
            '--property', 'foo'
        ]

        verifylist = [
            ('qos_spec', volume_fakes.qos_id),
            ('property', ['iops', 'foo'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.qos_mock.unset_keys.assert_called_with(
            volume_fakes.qos_id,
            ['iops', 'foo']
        )
