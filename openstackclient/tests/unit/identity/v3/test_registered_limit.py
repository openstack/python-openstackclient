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
from openstack.identity.v3 import region as _region
from openstack.identity.v3 import registered_limit as _registered_limit
from openstack.identity.v3 import service as _service
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.identity.v3 import registered_limit
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestRegisteredLimitCreate(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.region = sdk_fakes.generate_fake_resource(_region.Region)

        self.description = 'default limit of foobars'
        self.default_limit = 10
        self.resource_name = 'foobars'

        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region

        self.registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            description=None,
            region_id=None,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )
        self.registered_limit_with_options = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            description=self.description,
            region_id=self.region.id,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )

        self.cmd = registered_limit.CreateRegisteredLimit(self.app, None)

    def test_registered_limit_create_without_options(self):
        self.identity_sdk_client.create_registered_limit.return_value = (
            self.registered_limit
        )

        arglist = [
            '--service',
            self.service.id,
            '--default-limit',
            str(self.default_limit),
            self.resource_name,
        ]

        verifylist = [
            ('service', self.service.id),
            ('default_limit', self.default_limit),
            ('resource_name', self.resource_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'service_id': self.service.id,
            'default_limit': self.default_limit,
            'resource_name': self.resource_name,
        }
        self.identity_sdk_client.create_registered_limit.assert_called_with(
            **kwargs
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )

        self.assertEqual(collist, columns)
        datalist = (
            self.default_limit,
            None,
            self.registered_limit.id,
            None,
            self.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_create_with_options(self):
        self.identity_sdk_client.create_registered_limit.return_value = (
            self.registered_limit_with_options
        )

        arglist = [
            '--region',
            self.region.id,
            '--description',
            self.description,
            '--service',
            self.service.id,
            '--default-limit',
            str(self.default_limit),
            self.resource_name,
        ]

        verifylist = [
            ('region', self.region.id),
            ('description', self.description),
            ('service', self.service.id),
            ('default_limit', self.default_limit),
            ('resource_name', self.resource_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'description': self.description,
            'region_id': self.region.id,
            'service_id': self.service.id,
            'default_limit': self.default_limit,
            'resource_name': self.resource_name,
        }
        self.identity_sdk_client.create_registered_limit.assert_called_with(
            **kwargs
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )

        self.assertEqual(collist, columns)
        datalist = (
            self.default_limit,
            self.description,
            self.registered_limit_with_options.id,
            self.region.id,
            self.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)


class TestRegisteredLimitDelete(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.cmd = registered_limit.DeleteRegisteredLimit(self.app, None)

    def test_registered_limit_delete(self):
        self.registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
        )
        self.identity_sdk_client.delete_registered_limit.return_value = None

        arglist = [self.registered_limit.id]
        verifylist = [('registered_limits', [self.registered_limit.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_registered_limit.assert_called_with(
            self.registered_limit.id,
            ignore_missing=False,
        )
        self.assertIsNone(result)

    def test_registered_limit_delete_with_exception(self):
        self.identity_sdk_client.delete_registered_limit.side_effect = (
            sdk_exc.ResourceNotFound
        )

        arglist = ['fake-registered-limit-id']
        verifylist = [('registered_limits', ['fake-registered-limit-id'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 1 registered limits failed to delete.', str(e)
            )


class TestRegisteredLimitShow(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.region = sdk_fakes.generate_fake_resource(_region.Region)

        self.description = 'default limit of foobars'
        self.default_limit = 10
        self.resource_name = 'foobars'

        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region

        self.registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            description=None,
            region_id=None,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )
        self.registered_limit_with_options = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            description=self.description,
            region_id=self.region.id,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )

        self.cmd = registered_limit.ShowRegisteredLimit(self.app, None)

    def test_registered_limit_show(self):
        self.identity_sdk_client.get_registered_limit.return_value = (
            self.registered_limit
        )

        arglist = [self.registered_limit.id]
        verifylist = [('registered_limit_id', self.registered_limit.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.get_registered_limit.assert_called_with(
            self.registered_limit.id
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.default_limit,
            None,
            self.registered_limit.id,
            None,
            self.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_show_with_options(self):
        self.identity_sdk_client.get_registered_limit.return_value = (
            self.registered_limit_with_options
        )

        arglist = [self.registered_limit_with_options.id]
        verifylist = [
            ('registered_limit_id', self.registered_limit_with_options.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.get_registered_limit.assert_called_with(
            self.registered_limit_with_options.id
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.default_limit,
            self.description,
            self.registered_limit_with_options.id,
            self.region.id,
            self.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)


class TestRegisteredLimitSet(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.region = sdk_fakes.generate_fake_resource(_region.Region)

        self.default_limit = 10
        self.resource_name = 'foobars'

        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region

        self.registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            description=None,
            region_id=None,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )

        self.cmd = registered_limit.SetRegisteredLimit(self.app, None)

    def test_registered_limit_set_description(self):
        updated_description = 'default limit of foobars'
        updated_registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            id=self.registered_limit.id,
            description=updated_description,
            region_id=None,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )
        self.identity_sdk_client.update_registered_limit.return_value = (
            updated_registered_limit
        )

        arglist = [
            '--description',
            updated_description,
            self.registered_limit.id,
        ]
        verifylist = [
            ('description', updated_description),
            ('registered_limit_id', self.registered_limit.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_registered_limit.assert_called_with(
            self.registered_limit.id,
            description=updated_description,
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.default_limit,
            updated_description,
            self.registered_limit.id,
            None,
            self.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_set_default_limit(self):
        updated_default_limit = 20
        updated_registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            id=self.registered_limit.id,
            description=None,
            region_id=None,
            service_id=self.service.id,
            default_limit=updated_default_limit,
            resource_name=self.resource_name,
        )
        self.identity_sdk_client.update_registered_limit.return_value = (
            updated_registered_limit
        )

        arglist = [
            '--default-limit',
            str(updated_default_limit),
            self.registered_limit.id,
        ]
        verifylist = [
            ('default_limit', updated_default_limit),
            ('registered_limit_id', self.registered_limit.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_registered_limit.assert_called_with(
            self.registered_limit.id,
            default_limit=updated_default_limit,
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            updated_default_limit,
            None,
            self.registered_limit.id,
            None,
            self.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_set_resource_name(self):
        updated_resource_name = 'volumes'
        updated_registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            id=self.registered_limit.id,
            description=None,
            region_id=None,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=updated_resource_name,
        )
        self.identity_sdk_client.update_registered_limit.return_value = (
            updated_registered_limit
        )

        arglist = [
            '--resource-name',
            updated_resource_name,
            self.registered_limit.id,
        ]
        verifylist = [
            ('resource_name', updated_resource_name),
            ('registered_limit_id', self.registered_limit.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_registered_limit.assert_called_with(
            self.registered_limit.id,
            resource_name=updated_resource_name,
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.default_limit,
            None,
            self.registered_limit.id,
            None,
            updated_resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_set_service(self):
        updated_service = sdk_fakes.generate_fake_resource(_service.Service)
        self.identity_sdk_client.find_service.return_value = updated_service
        updated_registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            id=self.registered_limit.id,
            description=None,
            region_id=None,
            service_id=updated_service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )
        self.identity_sdk_client.update_registered_limit.return_value = (
            updated_registered_limit
        )

        arglist = ['--service', updated_service.id, self.registered_limit.id]
        verifylist = [
            ('service', updated_service.id),
            ('registered_limit_id', self.registered_limit.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_registered_limit.assert_called_with(
            self.registered_limit.id,
            service_id=updated_service.id,
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.default_limit,
            None,
            self.registered_limit.id,
            None,
            self.resource_name,
            updated_service.id,
        )
        self.assertEqual(datalist, data)

    def test_registered_limit_set_region(self):
        updated_region = sdk_fakes.generate_fake_resource(_region.Region)
        self.identity_sdk_client.get_region.return_value = updated_region
        updated_registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            id=self.registered_limit.id,
            description=None,
            region_id=updated_region.id,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )
        self.identity_sdk_client.update_registered_limit.return_value = (
            updated_registered_limit
        )

        arglist = ['--region', updated_region.id, self.registered_limit.id]
        verifylist = [
            ('region', updated_region.id),
            ('registered_limit_id', self.registered_limit.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_registered_limit.assert_called_with(
            self.registered_limit.id,
            region_id=updated_region.id,
        )

        collist = (
            'default_limit',
            'description',
            'id',
            'region_id',
            'resource_name',
            'service_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.default_limit,
            None,
            self.registered_limit.id,
            updated_region.id,
            self.resource_name,
            self.service.id,
        )
        self.assertEqual(datalist, data)


class TestRegisteredLimitList(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.region = sdk_fakes.generate_fake_resource(_region.Region)

        self.description = 'default limit of foobars'
        self.default_limit = 10
        self.resource_name = 'foobars'

        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region

        self.registered_limit = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            description=None,
            region_id=None,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )
        self.registered_limit_with_options = sdk_fakes.generate_fake_resource(
            resource_type=_registered_limit.RegisteredLimit,
            description=self.description,
            region_id=self.region.id,
            service_id=self.service.id,
            default_limit=self.default_limit,
            resource_name=self.resource_name,
        )
        self.identity_sdk_client.registered_limits.return_value = [
            self.registered_limit,
            self.registered_limit_with_options,
        ]

        self.cmd = registered_limit.ListRegisteredLimit(self.app, None)

    def test_registered_limit_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.registered_limits.assert_called_with()
        collist = (
            "ID",
            "Service ID",
            "Resource Name",
            "Default Limit",
            "Description",
            "Region ID",
        )
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.registered_limit.id,
                self.service.id,
                self.resource_name,
                self.default_limit,
                None,
                None,
            ),
            (
                self.registered_limit_with_options.id,
                self.service.id,
                self.resource_name,
                self.default_limit,
                self.description,
                self.region.id,
            ),
        )
        self.assertEqual(datalist, tuple(data))
