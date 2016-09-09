#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstackclient.tests.functional import base


class ExampleTests(base.TestCase):
    """Functional tests for running examples."""

    def test_common(self):
        # NOTE(stevemar): If an examples has a non-zero return
        # code, then execute will raise an error by default.
        base.execute('python', base.EXAMPLE_DIR + '/common.py --debug')

    def test_object_api(self):
        base.execute('python', base.EXAMPLE_DIR + '/object_api.py --debug')

    def test_osc_lib(self):
        base.execute('python', base.EXAMPLE_DIR + '/osc-lib.py --debug')
