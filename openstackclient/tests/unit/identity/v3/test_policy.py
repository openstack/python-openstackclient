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

from unittest import mock

from osc_lib import exceptions

from openstack.identity.v3 import policy as _policy
from openstack.test import fakes as sdk_fakes
from openstackclient.identity.v3 import policy
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


POLICY_RULES_FILE_PATH = '/tmp/path/to/file'
# Copied from
# https://opendev.org/openstack/keystone/src/branch/stable/2026.1/keystone/tests/unit/mapping_fixtures.py
EMPLOYEE_GROUP_ID = "0cd5e9"
CONTRACTOR_GROUP_ID = "85a868"
TESTER_GROUP_ID = "123"
DEVELOPER_GROUP_ID = "xyz"
POLICY_RULES = [
    {
        "local": [
            {"group": {"id": EMPLOYEE_GROUP_ID}},
            {"user": {"name": "{0}"}},
        ],
        "remote": [
            {"type": "UserName"},
            {
                "type": "orgPersonType",
                "not_any_of": ["Contractor", "SubContractor"],
            },
            {"type": "LastName", "any_one_of": ["Bo"]},
        ],
    },
    {
        "local": [
            {"group": {"id": CONTRACTOR_GROUP_ID}},
            {"user": {"name": "{0}"}},
        ],
        "remote": [
            {"type": "UserName"},
            {
                "type": "orgPersonType",
                "any_one_of": ["Contractor", "SubContractor"],
            },
            {"type": "FirstName", "any_one_of": ["Jill"]},
        ],
    },
]
POLICY_RULES_2 = [
    {
        "local": [
            {
                "user": {"name": "{0} {1}", "email": "{2}"},
                "group": {"id": EMPLOYEE_GROUP_ID},
            }
        ],
        "remote": [
            {"type": "FirstName"},
            {"type": "LastName"},
            {"type": "Email"},
            {
                "type": "orgPersonType",
                "any_one_of": ["Admin", "Big Cheese"],
            },
        ],
    },
    {
        "local": [{"user": {"name": "{0}", "email": "{1}"}}],
        "remote": [
            {"type": "UserName"},
            {"type": "Email"},
            {
                "type": "orgPersonType",
                "not_any_of": [
                    "Admin",
                    "Employee",
                    "Contractor",
                    "Tester",
                ],
            },
        ],
    },
    {
        "local": [
            {"group": {"id": TESTER_GROUP_ID}},
            {"group": {"id": DEVELOPER_GROUP_ID}},
            {"user": {"name": "{0}"}},
        ],
        "remote": [
            {"type": "UserName"},
            {"type": "orgPersonType", "any_one_of": ["Tester"]},
            {
                "type": "Email",
                "any_one_of": [".*@example.com$"],
                "regex": True,
            },
        ],
    },
]


class TestPolicyCreate(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.policy = sdk_fakes.generate_fake_resource(
            _policy.Policy, blob=POLICY_RULES, type='application/json'
        )
        self.identity_sdk_client.create_policy.return_value = self.policy

        self.cmd = policy.CreatePolicy(self.app, None)

    def test_create_policy(self):
        arglist = [POLICY_RULES_FILE_PATH]
        verifylist = [
            ('rules', POLICY_RULES_FILE_PATH),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = POLICY_RULES
        with mock.patch(
            "osc_lib.utils.read_blob_file_contents",
            mocker,
        ):
            columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.create_policy.assert_called_with(
            blob=POLICY_RULES, type='application/json'
        )

        collist = ('id', 'rules', 'type')
        self.assertEqual(collist, columns)

        datalist = (self.policy.id, POLICY_RULES, 'application/json')
        self.assertEqual(datalist, data)


class TestPolicyDelete(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.policy = sdk_fakes.generate_fake_resource(
            _policy.Policy, blob=POLICY_RULES, type='application/json'
        )
        self.identity_sdk_client.delete_policy.return_value = None
        self.cmd = policy.DeletePolicy(self.app, None)

    def test_delete_policy(self):
        arglist = [self.policy.id]
        verifylist = [('policy', [self.policy.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_policy.assert_called_with(
            self.policy.id, ignore_missing=False
        )
        self.assertIsNone(result)


class TestPolicyList(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.policy = sdk_fakes.generate_fake_resource(
            _policy.Policy, blob=POLICY_RULES, type='application/json'
        )

        self.extra_policy = sdk_fakes.generate_fake_resource(
            _policy.Policy, blob=POLICY_RULES_2, type='text/json'
        )

        self.identity_sdk_client.policies.return_value = [
            self.policy,
            self.extra_policy,
        ]

        # Get the command object to test
        self.cmd = policy.ListPolicy(self.app, None)

    def test_policy_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.policies.assert_called_with()

        collist = ('ID', 'Type')
        self.assertEqual(collist, columns)

        datalist = [
            (self.policy.id, 'application/json'),
            (self.extra_policy.id, 'text/json'),
        ]
        self.assertEqual(datalist, data)

    def test_policy_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.policies.assert_called_with()

        collist = ('ID', 'Type', 'Rules')
        self.assertEqual(collist, columns)

        datalist = [
            (self.policy.id, 'application/json', POLICY_RULES),
            (self.extra_policy.id, 'text/json', POLICY_RULES_2),
        ]
        self.assertEqual(datalist, data)


class TestPolicySet(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.policy = sdk_fakes.generate_fake_resource(
            _policy.Policy, blob=POLICY_RULES, type='application/json'
        )
        self.policy_2 = sdk_fakes.generate_fake_resource(
            _policy.Policy,
            id=self.policy.id,
            blob=POLICY_RULES_2,
            type='text/json',
        )
        self.identity_sdk_client.get_policy.return_value = self.policy
        self.identity_sdk_client.update_policy.return_value = self.policy_2

        # Get the command object to test
        self.cmd = policy.SetPolicy(self.app, None)

    def test_policy_set_new_rules(self):
        arglist = [
            self.policy.id,
            '--rules',
            POLICY_RULES_FILE_PATH,
            '--type',
            'text/json',
        ]
        verifylist = [
            ('policy', self.policy.id),
            ('rules', POLICY_RULES_FILE_PATH),
            ('type', 'text/json'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = POLICY_RULES_2
        with mock.patch(
            "osc_lib.utils.read_blob_file_contents",
            mocker,
        ):
            result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_policy.assert_called_with(
            self.policy.id,
            blob=POLICY_RULES_2,
            type='text/json',
        )

        self.assertIsNone(result)

    def test_policy_set_rules_wrong_file_path(self):
        arglist = [
            '--rules',
            POLICY_RULES_FILE_PATH,
            self.policy.id,
        ]
        verifylist = [
            ('policy', self.policy.id),
            ('rules', POLICY_RULES_FILE_PATH),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestPolicyShow(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.policy = sdk_fakes.generate_fake_resource(
            _policy.Policy, blob=POLICY_RULES, type='application/json'
        )
        self.identity_sdk_client.get_policy.return_value = self.policy

        self.cmd = policy.ShowPolicy(self.app, None)

    def test_policy_show(self):
        arglist = [self.policy.id]
        verifylist = [('policy', self.policy.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.get_policy.assert_called_with(self.policy.id)

        collist = ('id', 'rules', 'type')
        self.assertEqual(collist, columns)

        datalist = (self.policy.id, POLICY_RULES, 'application/json')
        self.assertEqual(datalist, data)
