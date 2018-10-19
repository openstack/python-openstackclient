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

from openstackclient.identity.v3 import limit
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestLimit(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestLimit, self).setUp()

        identity_manager = self.app.client_manager.identity

        self.limit_mock = identity_manager.limits

        self.services_mock = identity_manager.services
        self.services_mock.reset_mock()

        self.projects_mock = identity_manager.projects
        self.projects_mock.reset_mock()

        self.regions_mock = identity_manager.regions
        self.regions_mock.reset_mock()


class TestLimitCreate(TestLimit):

    def setUp(self):
        super(TestLimitCreate, self).setUp()

        self.service = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True
        )
        self.services_mock.get.return_value = self.service

        self.project = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True
        )
        self.projects_mock.get.return_value = self.project

        self.region = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.REGION),
            loaded=True
        )
        self.regions_mock.get.return_value = self.region

        self.cmd = limit.CreateLimit(self.app, None)

    def test_limit_create_without_options(self):
        self.limit_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.LIMIT),
            loaded=True
        )

        resource_limit = 15
        arglist = [
            '--project', identity_fakes.project_id,
            '--service', identity_fakes.service_id,
            '--resource-limit', str(resource_limit),
            identity_fakes.limit_resource_name
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
            ('service', identity_fakes.service_id),
            ('resource_name', identity_fakes.limit_resource_name),
            ('resource_limit', resource_limit)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'description': None, 'region': None}
        self.limit_mock.create.assert_called_with(
            self.project,
            self.service,
            identity_fakes.limit_resource_name,
            resource_limit,
            **kwargs
        )

        collist = ('description', 'id', 'project_id', 'region_id',
                   'resource_limit', 'resource_name', 'service_id')
        self.assertEqual(collist, columns)
        datalist = (
            None,
            identity_fakes.limit_id,
            identity_fakes.project_id,
            None,
            resource_limit,
            identity_fakes.limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)

    def test_limit_create_with_options(self):
        self.limit_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.LIMIT_OPTIONS),
            loaded=True
        )

        resource_limit = 15
        arglist = [
            '--project', identity_fakes.project_id,
            '--service', identity_fakes.service_id,
            '--resource-limit', str(resource_limit),
            '--region', identity_fakes.region_id,
            '--description', identity_fakes.limit_description,
            identity_fakes.limit_resource_name
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
            ('service', identity_fakes.service_id),
            ('resource_name', identity_fakes.limit_resource_name),
            ('resource_limit', resource_limit),
            ('region', identity_fakes.region_id),
            ('description', identity_fakes.limit_description)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'description': identity_fakes.limit_description,
            'region': self.region
        }
        self.limit_mock.create.assert_called_with(
            self.project,
            self.service,
            identity_fakes.limit_resource_name,
            resource_limit,
            **kwargs
        )

        collist = ('description', 'id', 'project_id', 'region_id',
                   'resource_limit', 'resource_name', 'service_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.limit_description,
            identity_fakes.limit_id,
            identity_fakes.project_id,
            identity_fakes.region_id,
            resource_limit,
            identity_fakes.limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)


class TestLimitDelete(TestLimit):

    def setUp(self):
        super(TestLimitDelete, self).setUp()
        self.cmd = limit.DeleteLimit(self.app, None)

    def test_limit_delete(self):
        self.limit_mock.delete.return_value = None

        arglist = [identity_fakes.limit_id]
        verifylist = [
            ('limit_id', [identity_fakes.limit_id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.limit_mock.delete.assert_called_with(
            identity_fakes.limit_id
        )
        self.assertIsNone(result)

    def test_limit_delete_with_exception(self):
        return_value = ksa_exceptions.NotFound()
        self.limit_mock.delete.side_effect = return_value

        arglist = ['fake-limit-id']
        verifylist = [
            ('limit_id', ['fake-limit-id'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 1 limits failed to delete.', str(e)
            )


class TestLimitShow(TestLimit):

    def setUp(self):
        super(TestLimitShow, self).setUp()

        self.limit_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.LIMIT),
            loaded=True
        )

        self.cmd = limit.ShowLimit(self.app, None)

    def test_limit_show(self):
        arglist = [identity_fakes.limit_id]
        verifylist = [('limit_id', identity_fakes.limit_id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.limit_mock.get.assert_called_with(identity_fakes.limit_id)

        collist = (
            'description', 'id', 'project_id', 'region_id', 'resource_limit',
            'resource_name', 'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            None,
            identity_fakes.limit_id,
            identity_fakes.project_id,
            None,
            identity_fakes.limit_resource_limit,
            identity_fakes.limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)


class TestLimitSet(TestLimit):

    def setUp(self):
        super(TestLimitSet, self).setUp()
        self.cmd = limit.SetLimit(self.app, None)

    def test_limit_set_description(self):
        limit = copy.deepcopy(identity_fakes.LIMIT)
        limit['description'] = identity_fakes.limit_description
        self.limit_mock.update.return_value = fakes.FakeResource(
            None, limit, loaded=True
        )

        arglist = [
            '--description', identity_fakes.limit_description,
            identity_fakes.limit_id
        ]
        verifylist = [
            ('description', identity_fakes.limit_description),
            ('limit_id', identity_fakes.limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.limit_mock.update.assert_called_with(
            identity_fakes.limit_id,
            description=identity_fakes.limit_description,
            resource_limit=None
        )

        collist = (
            'description', 'id', 'project_id', 'region_id', 'resource_limit',
            'resource_name', 'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.limit_description,
            identity_fakes.limit_id,
            identity_fakes.project_id,
            None,
            identity_fakes.limit_resource_limit,
            identity_fakes.limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)

    def test_limit_set_resource_limit(self):
        resource_limit = 20
        limit = copy.deepcopy(identity_fakes.LIMIT)
        limit['resource_limit'] = resource_limit
        self.limit_mock.update.return_value = fakes.FakeResource(
            None, limit, loaded=True
        )

        arglist = [
            '--resource-limit', str(resource_limit),
            identity_fakes.limit_id
        ]
        verifylist = [
            ('resource_limit', resource_limit),
            ('limit_id', identity_fakes.limit_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.limit_mock.update.assert_called_with(
            identity_fakes.limit_id,
            description=None,
            resource_limit=resource_limit
        )

        collist = (
            'description', 'id', 'project_id', 'region_id', 'resource_limit',
            'resource_name', 'service_id'
        )
        self.assertEqual(collist, columns)
        datalist = (
            None,
            identity_fakes.limit_id,
            identity_fakes.project_id,
            None,
            resource_limit,
            identity_fakes.limit_resource_name,
            identity_fakes.service_id
        )
        self.assertEqual(datalist, data)


class TestLimitList(TestLimit):

    def setUp(self):
        super(TestLimitList, self).setUp()

        self.limit_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.LIMIT),
                loaded=True
            )
        ]

        self.cmd = limit.ListLimit(self.app, None)

    def test_limit_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.limit_mock.list.assert_called_with(
            service=None, resource_name=None, region=None,
            project=None
        )

        collist = (
            'ID', 'Project ID', 'Service ID', 'Resource Name',
            'Resource Limit', 'Description', 'Region ID'
        )
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.limit_id,
            identity_fakes.project_id,
            identity_fakes.service_id,
            identity_fakes.limit_resource_name,
            identity_fakes.limit_resource_limit,
            None,
            None
        ), )
        self.assertEqual(datalist, tuple(data))
