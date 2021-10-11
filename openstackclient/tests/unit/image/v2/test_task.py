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


class TestTask(image_fakes.TestImagev2):
    def setUp(self):
        super().setUp()

        # Get shortcuts to mocked image client
        self.client = self.app.client_manager.image


class TestTaskShow(TestTask):

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

        self.client.get_task.return_value = self.task

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
        self.client.get_task.assert_called_with(self.task.id)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)
