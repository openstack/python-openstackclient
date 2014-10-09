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

from openstackclient.identity.v3 import federation_protocol
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes


class TestProtocol(identity_fakes.TestFederatedIdentity):

    def setUp(self):
        super(TestProtocol, self).setUp()

        federation_lib = self.app.client_manager.identity.federation
        self.protocols_mock = federation_lib.protocols
        self.protocols_mock.reset_mock()


class TestProtocolCreate(TestProtocol):

    def setUp(self):
        super(TestProtocolCreate, self).setUp()

        proto = copy.deepcopy(identity_fakes.PROTOCOL_OUTPUT)
        resource = fakes.FakeResource(None, proto, loaded=True)
        self.protocols_mock.create.return_value = resource
        self.cmd = federation_protocol.CreateProtocol(self.app, None)

    def test_create_protocol(self):
        argslist = [
            identity_fakes.protocol_id,
            '--identity-provider', identity_fakes.idp_id,
            '--mapping', identity_fakes.mapping_id
        ]

        verifylist = [
            ('federation_protocol', identity_fakes.protocol_id),
            ('identity_provider', identity_fakes.idp_id),
            ('mapping', identity_fakes.mapping_id)
        ]
        parsed_args = self.check_parser(self.cmd, argslist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.protocols_mock.create.assert_called_with(
            protocol_id=identity_fakes.protocol_id,
            identity_provider=identity_fakes.idp_id,
            mapping=identity_fakes.mapping_id)

        collist = ('id', 'identity_provider', 'mapping')
        self.assertEqual(collist, columns)

        datalist = (identity_fakes.protocol_id,
                    identity_fakes.idp_id,
                    identity_fakes.mapping_id)
        self.assertEqual(datalist, data)


class TestProtocolDelete(TestProtocol):

    def setUp(self):
        super(TestProtocolDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.protocols_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROTOCOL_OUTPUT),
            loaded=True,
        )

        self.protocols_mock.delete.return_value = None
        self.cmd = federation_protocol.DeleteProtocol(self.app, None)

    def test_delete_identity_provider(self):
        arglist = [
            '--identity-provider', identity_fakes.idp_id,
            identity_fakes.protocol_id
        ]
        verifylist = [
            ('federation_protocol', identity_fakes.protocol_id),
            ('identity_provider', identity_fakes.idp_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.protocols_mock.delete.assert_called_with(
            identity_fakes.idp_id, identity_fakes.protocol_id)


class TestProtocolList(TestProtocol):

    def setUp(self):
        super(TestProtocolList, self).setUp()

        self.protocols_mock.get.return_value = fakes.FakeResource(
            None, identity_fakes.PROTOCOL_ID_MAPPING, loaded=True)

        self.protocols_mock.list.return_value = [fakes.FakeResource(
            None, identity_fakes.PROTOCOL_ID_MAPPING, loaded=True)]

        self.cmd = federation_protocol.ListProtocols(self.app, None)

    def test_list_protocols(self):
        arglist = ['--identity-provider', identity_fakes.idp_id]
        verifylist = [('identity_provider', identity_fakes.idp_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.protocols_mock.list.assert_called_with(identity_fakes.idp_id)


class TestProtocolSet(TestProtocol):

    def setUp(self):
        super(TestProtocolSet, self).setUp()
        self.protocols_mock.get.return_value = fakes.FakeResource(
            None, identity_fakes.PROTOCOL_OUTPUT, loaded=True)
        self.protocols_mock.update.return_value = fakes.FakeResource(
            None, identity_fakes.PROTOCOL_OUTPUT_UPDATED, loaded=True)

        self.cmd = federation_protocol.SetProtocol(self.app, None)

    def test_set_new_mapping(self):
        arglist = [
            identity_fakes.protocol_id,
            '--identity-provider', identity_fakes.idp_id,
            '--mapping', identity_fakes.mapping_id
        ]
        verifylist = [('identity_provider', identity_fakes.idp_id),
                      ('federation_protocol', identity_fakes.protocol_id),
                      ('mapping', identity_fakes.mapping_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.protocols_mock.update.assert_called_with(
            identity_fakes.idp_id, identity_fakes.protocol_id,
            identity_fakes.mapping_id)

        collist = ('id', 'identity_provider', 'mapping')
        self.assertEqual(collist, columns)

        datalist = (identity_fakes.protocol_id, identity_fakes.idp_id,
                    identity_fakes.mapping_id_updated)
        self.assertEqual(datalist, data)


class TestProtocolShow(TestProtocol):

    def setUp(self):
        super(TestProtocolShow, self).setUp()
        self.protocols_mock.get.return_value = fakes.FakeResource(
            None, identity_fakes.PROTOCOL_OUTPUT, loaded=False)

        self.cmd = federation_protocol.ShowProtocol(self.app, None)

    def test_show_protocol(self):
        arglist = [identity_fakes.protocol_id, '--identity-provider',
                   identity_fakes.idp_id]
        verifylist = [('federation_protocol', identity_fakes.protocol_id),
                      ('identity_provider', identity_fakes.idp_id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.protocols_mock.get.assert_called_with(identity_fakes.idp_id,
                                                   identity_fakes.protocol_id)

        collist = ('id', 'identity_provider', 'mapping')
        self.assertEqual(collist, columns)

        datalist = (identity_fakes.protocol_id,
                    identity_fakes.idp_id,
                    identity_fakes.mapping_id)
        self.assertEqual(datalist, data)
