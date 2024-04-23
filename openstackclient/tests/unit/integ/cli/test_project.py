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

from osc_lib.tests import utils as osc_lib_utils

from openstackclient import shell
from openstackclient.tests.unit.integ import base as test_base
from openstackclient.tests.unit import test_shell


class TestIntegV2ProjectID(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V2_AUTH_URL,
            "OS_PROJECT_ID": test_shell.DEFAULT_PROJECT_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_IDENTITY_API_VERSION": "2",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v2_token(self.requests_mock)

    def test_project_id_env(self):
        _shell = shell.OpenStackShell()
        _shell.run("extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V2_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            test_shell.DEFAULT_PROJECT_ID,
            auth_req['auth']['tenantId'],
        )

    def test_project_id_arg(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-project-id wsx extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V2_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            "wsx",
            auth_req['auth']['tenantId'],
        )


class TestIntegV2ProjectName(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V2_AUTH_URL,
            "OS_PROJECT_NAME": test_shell.DEFAULT_PROJECT_NAME,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_IDENTITY_API_VERSION": "2",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v2_token(self.requests_mock)

    def test_project_name_env(self):
        _shell = shell.OpenStackShell()
        _shell.run("extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V2_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            test_shell.DEFAULT_PROJECT_NAME,
            auth_req['auth']['tenantName'],
        )

    def test_project_name_arg(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-project-name qaz extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V2_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            "qaz",
            auth_req['auth']['tenantName'],
        )


class TestIntegV3ProjectID(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V3_AUTH_URL,
            "OS_PROJECT_ID": test_shell.DEFAULT_PROJECT_NAME,
            # "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            # "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_IDENTITY_API_VERSION": "3",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v3_token(self.requests_mock)

    def test_project_id_env(self):
        _shell = shell.OpenStackShell()
        _shell.run("extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V3_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertIsNone(auth_req['auth'].get('tenantId', None))
        self.assertIsNone(auth_req['auth'].get('tenantName', None))

    def test_project_id_arg(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-project-id wsx extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V3_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertIsNone(auth_req['auth'].get('tenantId', None))
        self.assertIsNone(auth_req['auth'].get('tenantName', None))


class TestIntegV3ProjectName(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V3_AUTH_URL,
            "OS_PROJECT_NAME": test_shell.DEFAULT_PROJECT_NAME,
            # "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            # "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_IDENTITY_API_VERSION": "3",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v3_token(self.requests_mock)

    def test_project_name_env(self):
        _shell = shell.OpenStackShell()
        _shell.run("extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V3_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            test_shell.DEFAULT_PROJECT_NAME,
            auth_req['auth']['scope']['project']['name'],
        )

        self.assertIsNone(auth_req['auth'].get('tenantId', None))
        self.assertIsNone(auth_req['auth'].get('tenantName', None))

    def test_project_name_arg(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-project-name wsx extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V3_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            "wsx",
            auth_req['auth']['scope']['project']['name'],
        )

        self.assertIsNone(auth_req['auth'].get('tenantId', None))
        self.assertIsNone(auth_req['auth'].get('tenantName', None))
