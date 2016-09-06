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

from openstackclient.identity.v3 import consumer
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestOAuth1(identity_fakes.TestOAuth1):

    def setUp(self):
        super(TestOAuth1, self).setUp()
        identity_client = self.app.client_manager.identity
        self.consumers_mock = identity_client.oauth1.consumers
        self.consumers_mock.reset_mock()


class TestConsumerCreate(TestOAuth1):

    def setUp(self):
        super(TestConsumerCreate, self).setUp()

        self.consumers_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.OAUTH_CONSUMER),
            loaded=True,
        )

        self.cmd = consumer.CreateConsumer(self.app, None)

    def test_create_consumer(self):
        arglist = [
            '--description', identity_fakes.consumer_description,
        ]
        verifylist = [
            ('description', identity_fakes.consumer_description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.consumers_mock.create.assert_called_with(
            identity_fakes.consumer_description,
        )

        collist = ('description', 'id', 'secret')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.consumer_description,
            identity_fakes.consumer_id,
            identity_fakes.consumer_secret,
        )
        self.assertEqual(datalist, data)


class TestConsumerDelete(TestOAuth1):

    def setUp(self):
        super(TestConsumerDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.consumers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.OAUTH_CONSUMER),
            loaded=True,
        )

        self.consumers_mock.delete.return_value = None
        self.cmd = consumer.DeleteConsumer(self.app, None)

    def test_delete_consumer(self):
        arglist = [
            identity_fakes.consumer_id,
        ]
        verifylist = [
            ('consumer', [identity_fakes.consumer_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.consumers_mock.delete.assert_called_with(
            identity_fakes.consumer_id,
        )
        self.assertIsNone(result)


class TestConsumerList(TestOAuth1):

    def setUp(self):
        super(TestConsumerList, self).setUp()

        self.consumers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.OAUTH_CONSUMER),
            loaded=True,
        )
        self.consumers_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.OAUTH_CONSUMER),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = consumer.ListConsumer(self.app, None)

    def test_consumer_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.consumers_mock.list.assert_called_with()

        collist = ('ID', 'Description')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.consumer_id,
            identity_fakes.consumer_description,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestConsumerSet(TestOAuth1):

    def setUp(self):
        super(TestConsumerSet, self).setUp()

        self.consumers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.OAUTH_CONSUMER),
            loaded=True,
        )

        consumer_updated = copy.deepcopy(identity_fakes.OAUTH_CONSUMER)
        consumer_updated['description'] = "consumer new description"
        self.consumers_mock.update.return_value = fakes.FakeResource(
            None,
            consumer_updated,
            loaded=True,
        )

        self.cmd = consumer.SetConsumer(self.app, None)

    def test_consumer_update(self):
        new_description = "consumer new description"

        arglist = [
            '--description', new_description,
            identity_fakes.consumer_id,
        ]
        verifylist = [
            ('description', new_description),
            ('consumer', identity_fakes.consumer_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {'description': new_description}
        self.consumers_mock.update.assert_called_with(
            identity_fakes.consumer_id,
            **kwargs
        )
        self.assertIsNone(result)


class TestConsumerShow(TestOAuth1):

    def setUp(self):
        super(TestConsumerShow, self).setUp()

        consumer_no_secret = copy.deepcopy(identity_fakes.OAUTH_CONSUMER)
        del consumer_no_secret['secret']
        self.consumers_mock.get.return_value = fakes.FakeResource(
            None,
            consumer_no_secret,
            loaded=True,
        )

        # Get the command object to test
        self.cmd = consumer.ShowConsumer(self.app, None)

    def test_consumer_show(self):
        arglist = [
            identity_fakes.consumer_id,
        ]
        verifylist = [
            ('consumer', identity_fakes.consumer_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.consumers_mock.get.assert_called_with(
            identity_fakes.consumer_id,
        )

        collist = ('description', 'id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.consumer_description,
            identity_fakes.consumer_id,
        )
        self.assertEqual(datalist, data)
