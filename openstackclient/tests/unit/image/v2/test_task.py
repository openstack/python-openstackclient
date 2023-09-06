# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from osc_lib.cli import format_columns

from openstackclient.image.v2 import task
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestTaskShow(image_fakes.TestImagev2):
    task = image_fakes.create_one_task()

    columns = (
        'created_at',
        'expires_at',
        'id',
        'input',
        'message',
        'owner_id',
        'properties',
        'result',
        'status',
        'type',
        'updated_at',
    )
    data = (
        task.created_at,
        task.expires_at,
        task.id,
        task.input,
        task.message,
        task.owner_id,
        format_columns.DictColumn({}),
        task.result,
        task.status,
        task.type,
        task.updated_at,
    )

    def setUp(self):
        super().setUp()

        self.image_client.get_task.return_value = self.task

        # Get the command object to test
        self.cmd = task.ShowTask(self.app, None)

    def test_task_show(self):
        arglist = [self.task.id]
        verifylist = [
            ('task', self.task.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.get_task.assert_called_with(self.task.id)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestTaskList(image_fakes.TestImagev2):
    tasks = image_fakes.create_tasks()

    columns = (
        'ID',
        'Type',
        'Status',
        'Owner',
    )
    datalist = [
        (
            task.id,
            task.type,
            task.status,
            task.owner_id,
        )
        for task in tasks
    ]

    def setUp(self):
        super().setUp()

        self.image_client.tasks.side_effect = [self.tasks, []]

        # Get the command object to test
        self.cmd = task.ListTask(self.app, None)

    def test_task_list_no_options(self):
        arglist = []
        verifylist = [
            ('sort_key', None),
            ('sort_dir', None),
            ('limit', None),
            ('marker', None),
            ('type', None),
            ('status', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.tasks.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_task_list_sort_key_option(self):
        arglist = ['--sort-key', 'created_at']
        verifylist = [('sort_key', 'created_at')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.tasks.assert_called_with(
            sort_key=parsed_args.sort_key,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_task_list_sort_dir_option(self):
        arglist = ['--sort-dir', 'desc']
        verifylist = [('sort_dir', 'desc')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.tasks.assert_called_with(
            sort_dir=parsed_args.sort_dir,
        )

    def test_task_list_pagination_options(self):
        arglist = ['--limit', '1', '--marker', self.tasks[0].id]
        verifylist = [('limit', 1), ('marker', self.tasks[0].id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.tasks.assert_called_with(
            limit=parsed_args.limit,
            marker=parsed_args.marker,
        )

    def test_task_list_type_option(self):
        arglist = ['--type', self.tasks[0].type]
        verifylist = [('type', self.tasks[0].type)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.tasks.assert_called_with(
            type=self.tasks[0].type,
        )

    def test_task_list_status_option(self):
        arglist = ['--status', self.tasks[0].status]
        verifylist = [('status', self.tasks[0].status)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.tasks.assert_called_with(
            status=self.tasks[0].status,
        )
