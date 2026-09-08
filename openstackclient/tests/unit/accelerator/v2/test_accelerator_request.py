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

from openstack.accelerator.v2 import (
    accelerator_request as _arq,
)
from openstack import exceptions as sdk_exceptions
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.accelerator.v2 import accelerator_request
from openstackclient.tests.unit.accelerator.v2 import (
    fakes as accelerator_fakes,
)

SHOW_COLUMNS = (
    "uuid",
    "state",
    "device_profile_name",
    "hostname",
    "device_rp_uuid",
    "instance_uuid",
    "attach_handle_type",
    "attach_handle_info",
)

LIST_COLUMNS_SHORT = (
    "uuid",
    "state",
    "device_profile_name",
    "instance_uuid",
    "attach_handle_type",
    "attach_handle_info",
)

LIST_COLUMNS_LONG = (*LIST_COLUMNS_SHORT, "hostname", "device_rp_uuid")


class TestAcceleratorRequest(accelerator_fakes.TestAccelerator):
    def setUp(self):
        super().setUp()

        self.fake_arq = sdk_fakes.generate_fake_resource(
            _arq.AcceleratorRequest
        )
        self.data = tuple(self.fake_arq[col] for col in SHOW_COLUMNS)


class TestBindAcceleratorRequest(TestAcceleratorRequest):
    def setUp(self):
        super().setUp()

        self.accelerator_client.get_accelerator_request.return_value = (
            self.fake_arq
        )
        self.cmd = accelerator_request.BindAcceleratorRequest(self.app, None)

    def test_bind(self):
        arglist = [
            self.fake_arq.uuid,
            'host1',
            'instance-uuid-1',
            'device-rp-uuid-1',
        ]
        verifylist = [
            ('accelerator_request', self.fake_arq.uuid),
            ('hostname', 'host1'),
            ('instance_uuid', 'instance-uuid-1'),
            ('device_rp_uuid', 'device-rp-uuid-1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        expected_patch = [
            {
                'op': 'add',
                'path': '/hostname',
                'value': 'host1',
            },
            {
                'op': 'add',
                'path': '/instance_uuid',
                'value': 'instance-uuid-1',
            },
            {
                'op': 'add',
                'path': '/device_rp_uuid',
                'value': 'device-rp-uuid-1',
            },
        ]
        self.accelerator_client.patch_accelerator_request.assert_called_once_with(
            self.fake_arq.uuid, expected_patch
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)


class TestCreateAcceleratorRequest(TestAcceleratorRequest):
    def setUp(self):
        super().setUp()

        self.accelerator_client.create_accelerator_request.return_value = (
            self.fake_arq
        )
        self.cmd = accelerator_request.CreateAcceleratorRequest(self.app, None)

    def test_create(self):
        arglist = ['dp1']
        verifylist = [
            ('device_profile_name', 'dp1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.create_accelerator_request.assert_called_once_with(
            device_profile_name='dp1',
            device_profile_group_id=None,
            image_uuid=None,
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_options(self):
        arglist = [
            'dp1',
            '--group-id',
            '0',
            '--image-uuid',
            'img-uuid-1',
        ]
        verifylist = [
            ('device_profile_name', 'dp1'),
            ('group_id', '0'),
            ('img_uuid', 'img-uuid-1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.create_accelerator_request.assert_called_once_with(
            device_profile_name='dp1',
            device_profile_group_id='0',
            image_uuid='img-uuid-1',
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)


class TestDeleteAcceleratorRequest(TestAcceleratorRequest):
    def setUp(self):
        super().setUp()

        self.fake_arqs = list(
            sdk_fakes.generate_fake_resources(_arq.AcceleratorRequest, 2)
        )
        self.cmd = accelerator_request.DeleteAcceleratorRequest(self.app, None)

    def test_delete(self):
        arglist = [self.fake_arqs[0].uuid]
        verifylist = [
            (
                'accelerator_requests',
                [self.fake_arqs[0].uuid],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.accelerator_client.delete_accelerator_request.assert_called_once_with(
            self.fake_arqs[0].uuid,
            ignore_missing=False,
        )

    def test_delete_multiple(self):
        arglist = [a.uuid for a in self.fake_arqs]
        verifylist = [
            ('accelerator_requests', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        calls = [call(a.uuid, ignore_missing=False) for a in self.fake_arqs]
        self.accelerator_client.delete_accelerator_request.assert_has_calls(
            calls
        )

    def test_delete_with_error(self):
        arglist = [
            self.fake_arqs[0].uuid,
            'nonexistent',
        ]
        verifylist = [
            ('accelerator_requests', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.accelerator_client.delete_accelerator_request.side_effect = [
            None,
            sdk_exceptions.NotFoundException,
        ]

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 accelerator requests failed to delete.',
                str(e),
            )


class TestListAcceleratorRequest(TestAcceleratorRequest):
    def setUp(self):
        super().setUp()

        self.accelerator_client.accelerator_requests.return_value = [
            self.fake_arq
        ]
        self.cmd = accelerator_request.ListAcceleratorRequest(self.app, None)

    def test_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.accelerator_requests.assert_called_once_with()

        self.assertEqual(LIST_COLUMNS_SHORT, columns)

        expected_data = (
            tuple(self.fake_arq[col] for col in LIST_COLUMNS_SHORT),
        )
        self.assertCountEqual(expected_data, tuple(data))

    def test_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(LIST_COLUMNS_LONG, columns)

        expected_data = (
            tuple(self.fake_arq[col] for col in LIST_COLUMNS_LONG),
        )
        self.assertCountEqual(expected_data, tuple(data))


class TestShowAcceleratorRequest(TestAcceleratorRequest):
    def setUp(self):
        super().setUp()

        self.accelerator_client.get_accelerator_request.return_value = (
            self.fake_arq
        )
        self.cmd = accelerator_request.ShowAcceleratorRequest(self.app, None)

    def test_show(self):
        arglist = [self.fake_arq.uuid]
        verifylist = [
            ('accelerator_request', self.fake_arq.uuid),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.get_accelerator_request.assert_called_once_with(
            self.fake_arq.uuid
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)


class TestUnbindAcceleratorRequest(TestAcceleratorRequest):
    def setUp(self):
        super().setUp()

        self.accelerator_client.get_accelerator_request.return_value = (
            self.fake_arq
        )
        self.cmd = accelerator_request.UnbindAcceleratorRequest(self.app, None)

    def test_unbind(self):
        arglist = [self.fake_arq.uuid]
        verifylist = [
            ('accelerator_request', self.fake_arq.uuid),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        expected_patch = [
            {'op': 'remove', 'path': '/hostname'},
            {'op': 'remove', 'path': '/instance_uuid'},
            {'op': 'remove', 'path': '/device_rp_uuid'},
        ]
        self.accelerator_client.patch_accelerator_request.assert_called_once_with(
            self.fake_arq.uuid, expected_patch
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)
