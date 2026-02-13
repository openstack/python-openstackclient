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

from openstack.identity.v3 import federation_protocol as _federation_protocol
from openstack.identity.v3 import mapping as _mapping
from openstack.test import fakes as sdk_fakes
from openstackclient.identity.v3 import federation_protocol
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestProtocolCreate(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.proto = sdk_fakes.generate_fake_resource(
            _federation_protocol.FederationProtocol
        )
        self.identity_sdk_client.create_federation_protocol.return_value = (
            self.proto
        )
        self.cmd = federation_protocol.CreateProtocol(self.app, None)

    def test_create_protocol(self):
        argslist = [
            self.proto.name,
            '--identity-provider',
            self.proto.idp_id,
            '--mapping',
            self.proto.mapping_id,
        ]

        verifylist = [
            ('federation_protocol', self.proto.name),
            ('identity_provider', self.proto.idp_id),
            ('mapping', self.proto.mapping_id),
        ]
        parsed_args = self.check_parser(self.cmd, argslist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.create_federation_protocol.assert_called_with(
            name=self.proto.id,
            idp_id=self.proto.idp_id,
            mapping_id=self.proto.mapping_id,
        )

        collist = ('id', 'identity_provider', 'mapping')
        self.assertEqual(collist, columns)

        datalist = (
            self.proto.id,
            self.proto.idp_id,
            self.proto.mapping_id,
        )
        self.assertEqual(datalist, data)


class TestProtocolDelete(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.proto = sdk_fakes.generate_fake_resource(
            _federation_protocol.FederationProtocol
        )
        self.identity_sdk_client.delete_federation_protocol.return_value = None
        self.cmd = federation_protocol.DeleteProtocol(self.app, None)

    def test_delete_protocol(self):
        arglist = [
            '--identity-provider',
            self.proto.idp_id,
            self.proto.name,
        ]
        verifylist = [
            ('federation_protocol', [self.proto.id]),
            ('identity_provider', self.proto.idp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_federation_protocol.assert_called_with(
            idp_id=self.proto.idp_id,
            protocol=self.proto.id,
            ignore_missing=False,
        )
        self.assertIsNone(result)


class TestProtocolList(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.proto1 = sdk_fakes.generate_fake_resource(
            _federation_protocol.FederationProtocol
        )
        self.proto2 = sdk_fakes.generate_fake_resource(
            _federation_protocol.FederationProtocol, idp_id=self.proto1
        )
        self.identity_sdk_client.federation_protocols.return_value = [
            self.proto1,
            self.proto2,
        ]
        self.cmd = federation_protocol.ListProtocols(self.app, None)

    def test_list_protocols(self):
        arglist = ['--identity-provider', self.proto1.idp_id]
        verifylist = [('identity_provider', self.proto1.idp_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.federation_protocols.assert_called_with(
            self.proto1.idp_id
        )

        self.assertEqual(columns, ('id', 'mapping'))
        datalist = (
            (
                self.proto1.name,
                self.proto1.mapping_id,
            ),
            (
                self.proto2.name,
                self.proto2.mapping_id,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestProtocolSet(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()
        self.proto = sdk_fakes.generate_fake_resource(
            _federation_protocol.FederationProtocol
        )
        self.mapping = sdk_fakes.generate_fake_resource(_mapping.Mapping)
        self.identity_sdk_client.update_federation_protocol.return_value = (
            self.proto
        )
        self.cmd = federation_protocol.SetProtocol(self.app, None)

    def test_set_new_mapping(self):
        arglist = [
            self.proto.name,
            '--identity-provider',
            self.proto.idp_id,
            '--mapping',
            self.mapping.name,
        ]
        verifylist = [
            ('identity_provider', self.proto.idp_id),
            ('federation_protocol', self.proto.name),
            ('mapping', self.mapping.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_federation_protocol.assert_called_with(
            idp_id=self.proto.idp_id,
            name=self.proto.name,
            mapping_id=self.mapping.id,
        )

        collist = ('id', 'identity_provider', 'mapping')
        self.assertEqual(collist, columns)

        datalist = (
            self.proto.name,
            self.proto.idp_id,
            self.proto.mapping_id,
        )
        self.assertEqual(datalist, data)


class TestProtocolShow(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()
        self.proto = sdk_fakes.generate_fake_resource(
            _federation_protocol.FederationProtocol
        )
        self.identity_sdk_client.get_federation_protocol.return_value = (
            self.proto
        )
        self.cmd = federation_protocol.ShowProtocol(self.app, None)

    def test_show_protocol(self):
        arglist = [
            self.proto.name,
            '--identity-provider',
            self.proto.idp_id,
        ]
        verifylist = [
            ('federation_protocol', self.proto.name),
            ('identity_provider', self.proto.idp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.get_federation_protocol.assert_called_with(
            idp_id=self.proto.idp_id, protocol=self.proto.name
        )

        collist = ('id', 'identity_provider', 'mapping')
        self.assertEqual(collist, columns)

        datalist = (
            self.proto.name,
            self.proto.idp_id,
            self.proto.mapping_id,
        )
        self.assertEqual(datalist, data)
