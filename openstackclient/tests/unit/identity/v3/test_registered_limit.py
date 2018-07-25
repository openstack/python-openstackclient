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

from keystoneauth1.exceptions import http as ksa_exceptions
from osc_lib import exceptions

from openstackclient.identity.v3 import registered_limit
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestRegisteredLimit(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestRegisteredLimit, self).setUp()

        identity_manager = self.app.client_manager.identity
        self.registered_limit_mock = identity_manager.registered_limits

        self.services_mock = identity_manager.services
        self.services_mock.reset_mock()

        self.regions_mock = identity_manager.regions
        self.regions_mock.reset_mock()


class TestRegisteredLimitCreate(TestRegisteredLimit):

    def setUp(self):
        super(TestRegisteredLimitCreate, self).setUp()

        self.service = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True
        )
        self.services_mock.get.return_value = self.service

        self.region = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGION),
            loaded=True
        )
        self.regions_mock.get.return_value = self.region

        self.cmd = registered_limit.CreateRegisteredLimit(self.app, None)

    def test_registered_limit_create_without_options(self):
        self.registered_limit_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGISTERED_LIMIT),
            loaded=True
        )

        resource_name = identity_fakes.registered_limit_resource_name
        default_limit = identity_fakes.registered_limit_default_limit
        arglist = [
            '--service', identity_fakes.service_id,
            '--default-limit', '10',
            resource_name,
        ]

        verifylist = [
            ('service', identity_fakes.service_id),
            ('default_limit', default_limit),
            ('resource_name', resource_name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'description': None, 'region': None}
        self.registered_limit_mock.create.assert_called_with(
            self.service, resource_name, default_limit, **kwargs
        )

        collist = ('default_limit', 'description', 'id', 'region_id',
                   'resource_name', 'service_id')

        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.registered_limit_default_limit,
            None,
            identity_fakes.registered_limit_id,
            None,
            identity_fakes.registered_limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_create_with_options(self):
        self.registered_limit_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGISTERED_LIMIT_OPTIONS),
            loaded=True
        )

        resource_name = identity_fakes.registered_limit_resource_name
        default_limit = identity_fakes.registered_limit_default_limit
        description = identity_fakes.registered_limit_description
        arglist = [
            '--region', identity_fakes.region_id,
            '--description', description,
            '--service', identity_fakes.service_id,
            '--default-limit', '10',
            resource_name
        ]

        verifylist = [
            ('region', identity_fakes.region_id),
            ('description', description),
            ('service', identity_fakes.service_id),
            ('default_limit', default_limit),
            ('resource_name', resource_name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'description': description, 'region': self.region}
        self.registered_limit_mock.create.assert_called_with(
            self.service, resource_name, default_limit, **kwargs
        )

        collist = ('default_limit', 'description', 'id', 'region_id',
                   'resource_name', 'service_id')

        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.registered_limit_default_limit,
            description,
            identity_fakes.registered_limit_id,
            identity_fakes.region_id,
            identity_fakes.registered_limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)


class TestRegisteredLimitDelete(TestRegisteredLimit):

    def setUp(self):
        super(TestRegisteredLimitDelete, self).setUp()

        self.cmd = registered_limit.DeleteRegisteredLimit(self.app, None)

    def test_registered_limit_delete(self):
        self.registered_limit_mock.delete.return_value = None

        arglist = [identity_fakes.registered_limit_id]
        verifylist = [
            ('registered_limit_id', [identity_fakes.registered_limit_id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.registered_limit_mock.delete.assert_called_with(
            identity_fakes.registered_limit_id
        )
        self.assertIsNone(result)

    def test_registered_limit_delete_with_exception(self):
        return_value = ksa_exceptions.NotFound()
        self.registered_limit_mock.delete.side_effect = return_value

        arglist = ['fake-registered-limit-id']
        verifylist = [
            ('registered_limit_id', ['fake-registered-limit-id'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 1 registered limits failed to delete.', str(e)
            )


class TestRegisteredLimitShow(TestRegisteredLimit):

    def setUp(self):
        super(TestRegisteredLimitShow, self).setUp()

        self.registered_limit_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGISTERED_LIMIT),
            loaded=True
        )

        self.cmd = registered_limit.ShowRegisteredLimit(self.app, None)

    def test_registered_limit_show(self):
        arglist = [identity_fakes.registered_limit_id]
        verifylist = [
            ('registered_limit_id', identity_fakes.registered_limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.registered_limit_mock.get.assert_called_with(
            identity_fakes.registered_limit_id
        )

        collist = (
            'default_limit', 'description', 'id', 'region_id', 'resource_name',
            'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.registered_limit_default_limit,
            None,
            identity_fakes.registered_limit_id,
            None,
            identity_fakes.registered_limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)


class TestRegisteredLimitSet(TestRegisteredLimit):

    def setUp(self):
        super(TestRegisteredLimitSet, self).setUp()
        self.cmd = registered_limit.SetRegisteredLimit(self.app, None)

    def test_registered_limit_set_description(self):
        registered_limit = copy.deepcopy(identity_fakes.REGISTERED_LIMIT)
        registered_limit['description'] = (
            identity_fakes.registered_limit_description
        )
        self.registered_limit_mock.update.return_value = fakes.FakeResource(
            None, registered_limit, loaded=True
        )

        arglist = [
            '--description', identity_fakes.registered_limit_description,
            identity_fakes.registered_limit_id
        ]
        verifylist = [
            ('description', identity_fakes.registered_limit_description),
            ('registered_limit_id', identity_fakes.registered_limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.registered_limit_mock.update.assert_called_with(
            identity_fakes.registered_limit_id,
            service=None,
            resource_name=None,
            default_limit=None,
            description=identity_fakes.registered_limit_description,
            region=None
        )

        collist = (
            'default_limit', 'description', 'id', 'region_id', 'resource_name',
            'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.registered_limit_default_limit,
            identity_fakes.registered_limit_description,
            identity_fakes.registered_limit_id,
            None,
            identity_fakes.registered_limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_set_default_limit(self):
        registered_limit = copy.deepcopy(identity_fakes.REGISTERED_LIMIT)
        default_limit = 20
        registered_limit['default_limit'] = default_limit
        self.registered_limit_mock.update.return_value = fakes.FakeResource(
            None, registered_limit, loaded=True
        )

        arglist = [
            '--default-limit', str(default_limit),
            identity_fakes.registered_limit_id
        ]
        verifylist = [
            ('default_limit', default_limit),
            ('registered_limit_id', identity_fakes.registered_limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.registered_limit_mock.update.assert_called_with(
            identity_fakes.registered_limit_id,
            service=None,
            resource_name=None,
            default_limit=default_limit,
            description=None,
            region=None
        )

        collist = (
            'default_limit', 'description', 'id', 'region_id', 'resource_name',
            'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            default_limit,
            None,
            identity_fakes.registered_limit_id,
            None,
            identity_fakes.registered_limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_set_resource_name(self):
        registered_limit = copy.deepcopy(identity_fakes.REGISTERED_LIMIT)
        resource_name = 'volumes'
        registered_limit['resource_name'] = resource_name
        self.registered_limit_mock.update.return_value = fakes.FakeResource(
            None, registered_limit, loaded=True
        )

        arglist = [
            '--resource-name', resource_name,
            identity_fakes.registered_limit_id
        ]
        verifylist = [
            ('resource_name', resource_name),
            ('registered_limit_id', identity_fakes.registered_limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.registered_limit_mock.update.assert_called_with(
            identity_fakes.registered_limit_id,
            service=None,
            resource_name=resource_name,
            default_limit=None,
            description=None,
            region=None
        )

        collist = (
            'default_limit', 'description', 'id', 'region_id', 'resource_name',
            'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.registered_limit_default_limit,
            None,
            identity_fakes.registered_limit_id,
            None,
            resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_set_service(self):
        registered_limit = copy.deepcopy(identity_fakes.REGISTERED_LIMIT)
        service = identity_fakes.FakeService.create_one_service()
        registered_limit['service_id'] = service.id
        self.registered_limit_mock.update.return_value = fakes.FakeResource(
            None, registered_limit, loaded=True
        )
        self.services_mock.get.return_value = service

        arglist = [
            '--service', service.id,
            identity_fakes.registered_limit_id
        ]
        verifylist = [
            ('service', service.id),
            ('registered_limit_id', identity_fakes.registered_limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.registered_limit_mock.update.assert_called_with(
            identity_fakes.registered_limit_id,
            service=service,
            resource_name=None,
            default_limit=None,
            description=None,
            region=None
        )

        collist = (
            'default_limit', 'description', 'id', 'region_id', 'resource_name',
            'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.registered_limit_default_limit,
            None,
            identity_fakes.registered_limit_id,
            None,
            identity_fakes.registered_limit_resource_name,
            service.id
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_set_region(self):
        registered_limit = copy.deepcopy(identity_fakes.REGISTERED_LIMIT)
        region = identity_fakes.REGION
        region['id'] = 'RegionTwo'
        region = fakes.FakeResource(
            None,
            copy.deepcopy(region),
            loaded=True
        )
        registered_limit['region_id'] = region.id
        self.registered_limit_mock.update.return_value = fakes.FakeResource(
            None, registered_limit, loaded=True
        )
        self.regions_mock.get.return_value = region

        arglist = [
            '--region', region.id,
            identity_fakes.registered_limit_id
        ]
        verifylist = [
            ('region', region.id),
            ('registered_limit_id', identity_fakes.registered_limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.registered_limit_mock.update.assert_called_with(
            identity_fakes.registered_limit_id,
            service=None,
            resource_name=None,
            default_limit=None,
            description=None,
            region=region
        )

        collist = (
            'default_limit', 'description', 'id', 'region_id', 'resource_name',
            'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.registered_limit_default_limit,
            None,
            identity_fakes.registered_limit_id,
            region.id,
            identity_fakes.registered_limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)


class TestRegisteredLimitList(TestRegisteredLimit):

    def setUp(self):
        super(TestRegisteredLimitList, self).setUp()

        self.registered_limit_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGISTERED_LIMIT),
            loaded=True
        )

        self.cmd = registered_limit.ShowRegisteredLimit(self.app, None)

    def test_limit_show(self):
        arglist = [identity_fakes.registered_limit_id]
        verifylist = [
            ('registered_limit_id', identity_fakes.registered_limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.registered_limit_mock.get.assert_called_with(
            identity_fakes.registered_limit_id
        )

        collist = (
            'default_limit', 'description', 'id', 'region_id', 'resource_name',
            'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.registered_limit_default_limit,
            None,
            identity_fakes.registered_limit_id,
            None,
            identity_fakes.registered_limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)
