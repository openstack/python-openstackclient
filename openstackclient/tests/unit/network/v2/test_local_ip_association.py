#   Copyright 2021 Huawei, Inc. All rights reserved.
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

from unittest import mock
from unittest.mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import local_ip_association
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes_v2
from openstackclient.tests.unit.network.v2 import fakes as network_fakes


class TestLocalIPAssociation(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()
        self.local_ip = network_fakes.create_one_local_ip()
        self.fixed_port = network_fakes.create_one_port()
        self.project = identity_fakes_v2.FakeProject.create_one_project()
        self.network_client.find_port = mock.Mock(return_value=self.fixed_port)


class TestCreateLocalIPAssociation(TestLocalIPAssociation):
    def setUp(self):
        super().setUp()
        self.new_local_ip_association = (
            network_fakes.create_one_local_ip_association(
                attrs={
                    'fixed_port_id': self.fixed_port.id,
                    'local_ip_id': self.local_ip.id,
                }
            )
        )
        self.network_client.create_local_ip_association = mock.Mock(
            return_value=self.new_local_ip_association
        )

        self.network_client.find_local_ip = mock.Mock(
            return_value=self.local_ip
        )

        # Get the command object to test
        self.cmd = local_ip_association.CreateLocalIPAssociation(
            self.app, None
        )

        self.columns = (
            'local_ip_address',
            'fixed_port_id',
            'fixed_ip',
            'host',
        )

        self.data = (
            self.new_local_ip_association.local_ip_address,
            self.new_local_ip_association.fixed_port_id,
            self.new_local_ip_association.fixed_ip,
            self.new_local_ip_association.host,
        )

    def test_create_no_options(self):
        arglist = [
            self.new_local_ip_association.local_ip_id,
            self.new_local_ip_association.fixed_port_id,
        ]
        verifylist = [
            ('local_ip', self.new_local_ip_association.local_ip_id),
            ('fixed_port', self.new_local_ip_association.fixed_port_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_local_ip_association.assert_called_once_with(
            self.new_local_ip_association.local_ip_id,
            **{
                'fixed_port_id': self.new_local_ip_association.fixed_port_id,
            },
        )
        self.assertEqual(set(self.columns), set(columns))
        self.assertEqual(set(self.data), set(data))

    def test_create_all_options(self):
        arglist = [
            self.new_local_ip_association.local_ip_id,
            self.new_local_ip_association.fixed_port_id,
            '--fixed-ip',
            self.new_local_ip_association.fixed_ip,
        ]
        verifylist = [
            ('local_ip', self.new_local_ip_association.local_ip_id),
            ('fixed_port', self.new_local_ip_association.fixed_port_id),
            ('fixed_ip', self.new_local_ip_association.fixed_ip),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_local_ip_association.assert_called_once_with(
            self.new_local_ip_association.local_ip_id,
            **{
                'fixed_port_id': self.new_local_ip_association.fixed_port_id,
                'fixed_ip': self.new_local_ip_association.fixed_ip,
            },
        )
        self.assertEqual(set(self.columns), set(columns))
        self.assertEqual(set(self.data), set(data))


class TestDeleteLocalIPAssociation(TestLocalIPAssociation):
    def setUp(self):
        super().setUp()
        self._local_ip_association = (
            network_fakes.create_local_ip_associations(
                count=2,
                attrs={
                    'local_ip_id': self.local_ip.id,
                },
            )
        )
        self.network_client.delete_local_ip_association = mock.Mock(
            return_value=None
        )

        self.network_client.find_local_ip = mock.Mock(
            return_value=self.local_ip
        )
        # Get the command object to test
        self.cmd = local_ip_association.DeleteLocalIPAssociation(
            self.app, None
        )

    def test_local_ip_association_delete(self):
        arglist = [
            self.local_ip.id,
            self._local_ip_association[0].fixed_port_id,
        ]
        verifylist = [
            ('local_ip', self.local_ip.id),
            ('fixed_port_id', [self._local_ip_association[0].fixed_port_id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_local_ip_association.assert_called_once_with(
            self.local_ip.id,
            self._local_ip_association[0].fixed_port_id,
            ignore_missing=False,
        )

        self.assertIsNone(result)

    def test_multi_local_ip_associations_delete(self):
        arglist = []
        fixed_port_id = []

        arglist.append(str(self.local_ip))

        for a in self._local_ip_association:
            arglist.append(a.fixed_port_id)
            fixed_port_id.append(a.fixed_port_id)

        verifylist = [
            ('local_ip', str(self.local_ip)),
            ('fixed_port_id', fixed_port_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self._local_ip_association:
            calls.append(
                call(a.local_ip_id, a.fixed_port_id, ignore_missing=False)
            )

        self.network_client.delete_local_ip_association.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_local_ip_association_delete_with_exception(self):
        arglist = [
            self.local_ip.id,
            self._local_ip_association[0].fixed_port_id,
            'unexist_fixed_port_id',
        ]
        verifylist = [
            ('local_ip', self.local_ip.id),
            (
                'fixed_port_id',
                [
                    self._local_ip_association[0].fixed_port_id,
                    'unexist_fixed_port_id',
                ],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        delete_mock_result = [None, exceptions.CommandError]

        self.network_client.delete_local_ip_association = mock.MagicMock(
            side_effect=delete_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 Local IP Associations failed to delete.', str(e)
            )

        self.network_client.delete_local_ip_association.assert_any_call(
            self.local_ip.id, 'unexist_fixed_port_id', ignore_missing=False
        )
        self.network_client.delete_local_ip_association.assert_any_call(
            self.local_ip.id,
            self._local_ip_association[0].fixed_port_id,
            ignore_missing=False,
        )


class TestListLocalIPAssociation(TestLocalIPAssociation):
    columns = (
        'Local IP ID',
        'Local IP Address',
        'Fixed port ID',
        'Fixed IP',
        'Host',
    )

    def setUp(self):
        super().setUp()
        self.local_ip_associations = (
            network_fakes.create_local_ip_associations(
                count=3,
                attrs={
                    'local_ip_id': self.local_ip.id,
                    'fixed_port_id': self.fixed_port.id,
                },
            )
        )
        self.data = []
        for lip_assoc in self.local_ip_associations:
            self.data.append(
                (
                    lip_assoc.local_ip_id,
                    lip_assoc.local_ip_address,
                    lip_assoc.fixed_port_id,
                    lip_assoc.fixed_ip,
                    lip_assoc.host,
                )
            )
        self.network_client.local_ip_associations = mock.Mock(
            return_value=self.local_ip_associations
        )
        self.network_client.find_local_ip = mock.Mock(
            return_value=self.local_ip
        )
        self.network_client.find_port = mock.Mock(return_value=self.fixed_port)
        # Get the command object to test
        self.cmd = local_ip_association.ListLocalIPAssociation(self.app, None)

    def test_local_ip_association_list(self):
        arglist = [self.local_ip.id]
        verifylist = [('local_ip', self.local_ip.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.local_ip_associations.assert_called_once_with(
            self.local_ip, **{}
        )
        self.assertEqual(set(self.columns), set(columns))
        self.assertEqual(set(self.data), set(list(data)))

    def test_local_ip_association_list_all_options(self):
        arglist = [
            '--fixed-port',
            self.local_ip_associations[0].fixed_port_id,
            '--fixed-ip',
            self.local_ip_associations[0].fixed_ip,
            '--host',
            self.local_ip_associations[0].host,
            self.local_ip_associations[0].local_ip_id,
        ]

        verifylist = [
            ('fixed_port', self.local_ip_associations[0].fixed_port_id),
            ('fixed_ip', self.local_ip_associations[0].fixed_ip),
            ('host', self.local_ip_associations[0].host),
            ('local_ip', self.local_ip_associations[0].local_ip_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        attrs = {
            'fixed_port_id': self.local_ip_associations[0].fixed_port_id,
            'fixed_ip': self.local_ip_associations[0].fixed_ip,
            'host': self.local_ip_associations[0].host,
        }

        self.network_client.local_ip_associations.assert_called_once_with(
            self.local_ip, **attrs
        )
        self.assertEqual(set(self.columns), set(columns))
        self.assertEqual(set(self.data), set(list(data)))
