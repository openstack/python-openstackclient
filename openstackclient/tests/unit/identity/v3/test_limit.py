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

from openstack import exceptions as sdk_exc
from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import limit as _limit
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import region as _region
from openstack.identity.v3 import service as _service
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.identity.v3 import limit
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestLimitCreate(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.project = sdk_fakes.generate_fake_resource(
            _project.Project, domain_id=self.domain.id
        )
        self.region = sdk_fakes.generate_fake_resource(_region.Region)
        self.service = sdk_fakes.generate_fake_resource(_service.Service)

        self.resource_limit = 15

        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region
        self.identity_sdk_client.find_project.return_value = self.project
        self.identity_sdk_client.find_domain.return_value = self.domain

        self.limit = sdk_fakes.generate_fake_resource(
            resource_type=_limit.Limit,
            project_id=self.project.id,
            service_id=self.service.id,
            resource_name='foobars',
            description=None,
            resource_limit=self.resource_limit,
            region_id=None,
        )
        self.limit_with_options = sdk_fakes.generate_fake_resource(
            resource_type=_limit.Limit,
            project_id=self.project.id,
            service_id=self.service.id,
            resource_limit=self.resource_limit,
            resource_name='foobars',
            description='test description',
            region_id=self.region.id,
        )

        self.cmd = limit.CreateLimit(self.app, None)

    def test_limit_create_without_options(self):
        self.identity_sdk_client.create_limit.return_value = self.limit

        arglist = [
            '--project',
            self.project.id,
            '--service',
            self.service.id,
            '--resource-limit',
            str(self.resource_limit),
            self.limit.resource_name,
        ]
        verifylist = [
            ('project', self.project.id),
            ('service', self.service.id),
            ('resource_name', self.limit.resource_name),
            ('resource_limit', self.resource_limit),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.create_limit.assert_called_with(
            project_id=self.project.id,
            service_id=self.service.id,
            resource_name=self.limit.resource_name,
            resource_limit=self.resource_limit,
        )

        collist = (
            'description',
            'id',
            'project_id',
            'region_id',
            'resource_limit',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            None,
            self.limit.id,
            self.project.id,
            None,
            self.resource_limit,
            self.limit.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)

    def test_limit_create_with_options(self):
        self.identity_sdk_client.create_limit.return_value = (
            self.limit_with_options
        )

        resource_limit = 15
        arglist = [
            '--project',
            self.project.id,
            '--project-domain',
            self.domain.name,
            '--service',
            self.service.id,
            '--resource-limit',
            str(resource_limit),
            '--region',
            self.region.id,
            '--description',
            self.limit_with_options.description,
            self.limit_with_options.resource_name,
        ]
        verifylist = [
            ('project', self.project.id),
            ('project_domain', self.domain.name),
            ('service', self.service.id),
            ('resource_name', self.limit_with_options.resource_name),
            ('resource_limit', resource_limit),
            ('region', self.region.id),
            ('description', self.limit_with_options.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'project_id': self.project.id,
            'service_id': self.service.id,
            'region_id': self.region.id,
            'resource_name': self.limit_with_options.resource_name,
            'resource_limit': resource_limit,
            'description': self.limit_with_options.description,
        }
        self.identity_sdk_client.create_limit.assert_called_with(
            **kwargs,
        )

        collist = (
            'description',
            'id',
            'project_id',
            'region_id',
            'resource_limit',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.limit_with_options.description,
            self.limit_with_options.id,
            self.project.id,
            self.region.id,
            resource_limit,
            self.limit_with_options.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)


class TestLimitDelete(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()
        self.cmd = limit.DeleteLimit(self.app, None)

    def test_limit_delete(self):
        self.limit = sdk_fakes.generate_fake_resource(
            resource_type=_limit.Limit
        )
        self.identity_sdk_client.delete_limit.return_value = None

        arglist = [self.limit.id]
        verifylist = [('limit_id', [self.limit.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_limit.assert_called_with(self.limit.id)
        self.assertIsNone(result)

    def test_limit_delete_with_exception(self):
        self.identity_sdk_client.delete_limit.side_effect = (
            sdk_exc.ResourceNotFound
        )

        arglist = ['fake-limit-id']
        verifylist = [('limit_id', ['fake-limit-id'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 1 limits failed to delete.', str(e))


class TestLimitShow(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.region = sdk_fakes.generate_fake_resource(_region.Region)
        self.service = sdk_fakes.generate_fake_resource(_service.Service)

        self.resource_limit = 15

        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region
        self.identity_sdk_client.find_project.return_value = self.project

        self.limit = sdk_fakes.generate_fake_resource(
            resource_type=_limit.Limit,
            project_id=self.project.id,
            service_id=self.service.id,
            resource_name='foobars',
            description=None,
            resource_limit=self.resource_limit,
            region_id=None,
        )

        self.identity_sdk_client.get_limit.return_value = self.limit

        self.cmd = limit.ShowLimit(self.app, None)

    def test_limit_show(self):
        arglist = [self.limit.id]
        verifylist = [('limit_id', self.limit.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.get_limit.assert_called_with(self.limit.id)

        collist = (
            'description',
            'id',
            'project_id',
            'region_id',
            'resource_limit',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            None,
            self.limit.id,
            self.project.id,
            None,
            self.resource_limit,
            self.limit.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)


class TestLimitSet(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.region = sdk_fakes.generate_fake_resource(_region.Region)
        self.service = sdk_fakes.generate_fake_resource(_service.Service)

        self.resource_limit = 15

        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region
        self.identity_sdk_client.find_project.return_value = self.project

        self.cmd = limit.SetLimit(self.app, None)

    def test_limit_set_description(self):
        description = 'limit of foobars'
        limit = sdk_fakes.generate_fake_resource(
            resource_type=_limit.Limit,
            project_id=self.project.id,
            service_id=self.service.id,
            resource_name='foobars',
            description=description,
            resource_limit=self.resource_limit,
            region_id=None,
        )
        self.identity_sdk_client.update_limit.return_value = limit

        arglist = [
            '--description',
            description,
            limit.id,
        ]
        verifylist = [
            ('description', description),
            ('limit_id', limit.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_limit.assert_called_with(
            limit.id,
            description=description,
        )

        collist = (
            'description',
            'id',
            'project_id',
            'region_id',
            'resource_limit',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            description,
            limit.id,
            self.project.id,
            None,
            limit.resource_limit,
            limit.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)

    def test_limit_set_resource_limit(self):
        resource_limit = 20
        limit = sdk_fakes.generate_fake_resource(
            resource_type=_limit.Limit,
            project_id=self.project.id,
            service_id=self.service.id,
            resource_name='foobars',
            description=None,
            resource_limit=resource_limit,
            region_id=None,
        )
        self.identity_sdk_client.update_limit.return_value = limit

        arglist = [
            '--resource-limit',
            str(resource_limit),
            limit.id,
        ]
        verifylist = [
            ('resource_limit', resource_limit),
            ('limit_id', limit.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_limit.assert_called_with(
            limit.id,
            resource_limit=resource_limit,
        )

        collist = (
            'description',
            'id',
            'project_id',
            'region_id',
            'resource_limit',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            None,
            limit.id,
            self.project.id,
            None,
            resource_limit,
            limit.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)


class TestLimitList(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.region = sdk_fakes.generate_fake_resource(_region.Region)
        self.service = sdk_fakes.generate_fake_resource(_service.Service)

        self.resource_limit = 15

        self.limit = sdk_fakes.generate_fake_resource(
            resource_type=_limit.Limit,
            project_id=self.project.id,
            service_id=self.service.id,
            resource_name='foobars',
            description=None,
            resource_limit=self.resource_limit,
            region_id=None,
        )
        self.identity_sdk_client.limits.return_value = [self.limit]

        self.cmd = limit.ListLimit(self.app, None)

    def test_limit_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.limits.assert_called_with()

        collist = (
            'ID',
            'Project ID',
            'Service ID',
            'Resource Name',
            'Resource Limit',
            'Description',
            'Region ID',
        )
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.limit.id,
                self.project.id,
                self.service.id,
                self.limit.resource_name,
                self.limit.resource_limit,
                None,
                None,
            ),
        )
        self.assertEqual(datalist, tuple(data))
