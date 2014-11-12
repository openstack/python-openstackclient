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

from functional.common import test


class ExampleTests(test.TestCase):
    """Functional tests for running examples."""

    def test_common(self):
        # NOTE(stevemar): If an examples has a non-zero return
        # code, then execute will raise an error by default.
        test.execute('python', test.EXAMPLE_DIR + '/common.py --debug')
