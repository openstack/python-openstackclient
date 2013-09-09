#   Copyright 2013 Nebula Inc.
#
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
#

from openstackclient.tests.identity.v3 import fakes
from openstackclient.tests import utils


AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"


class TestIdentityv3(utils.TestCommand):
    def setUp(self):
        super(TestIdentityv3, self).setUp()

        self.app.client_manager.identity = fakes.FakeIdentityv3Client(
            endpoint=AUTH_URL,
            token=AUTH_TOKEN,
        )
