#   Copyright 2014 CERN.
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

from unittest import mock

from osc_lib import exceptions

from openstack.identity.v3 import mapping as _mapping
from openstack.test import fakes as sdk_fakes
from openstackclient.identity.v3 import mapping
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


MAPPING_RULES_FILE_PATH = '/tmp/path/to/file'
# Copied from
# https://opendev.org/openstack/keystone/src/branch/stable/2026.1/keystone/tests/unit/mapping_fixtures.py
EMPLOYEE_GROUP_ID = "0cd5e9"
CONTRACTOR_GROUP_ID = "85a868"
TESTER_GROUP_ID = "123"
DEVELOPER_GROUP_ID = "xyz"
MAPPING_RULES = [
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
MAPPING_RULES_2 = {
    "rules": [
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
}


class TestMappingCreate(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.mapping = sdk_fakes.generate_fake_resource(
            _mapping.Mapping, rules=MAPPING_RULES, schema_version=None
        )
        self.identity_sdk_client.create_mapping.return_value = self.mapping

        self.cmd = mapping.CreateMapping(self.app, None)

    def test_create_mapping(self):
        arglist = [
            '--rules',
            MAPPING_RULES_FILE_PATH,
            self.mapping.id,
        ]
        verifylist = [
            ('mapping', self.mapping.id),
            ('rules', MAPPING_RULES_FILE_PATH),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = MAPPING_RULES
        with mock.patch(
            "openstackclient.identity.v3.mapping.CreateMapping._read_rules",
            mocker,
        ):
            columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.create_mapping.assert_called_with(
            id=self.mapping.id, rules=MAPPING_RULES, schema_version=None
        )

        collist = ('id', 'rules', 'schema_version')
        self.assertEqual(collist, columns)

        datalist = (self.mapping.id, MAPPING_RULES, None)
        self.assertEqual(datalist, data)


class TestMappingDelete(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.mapping = sdk_fakes.generate_fake_resource(
            _mapping.Mapping, rules=MAPPING_RULES, schema_version=None
        )
        self.identity_sdk_client.delete_mapping.return_value = None
        self.cmd = mapping.DeleteMapping(self.app, None)

    def test_delete_mapping(self):
        arglist = [self.mapping.id]
        verifylist = [('mapping', [self.mapping.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_mapping.assert_called_with(
            self.mapping.id, ignore_missing=False
        )
        self.assertIsNone(result)


class TestMappingList(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.mapping = sdk_fakes.generate_fake_resource(
            _mapping.Mapping, rules=MAPPING_RULES, schema_version='1.0'
        )

        self.extra_mapping = sdk_fakes.generate_fake_resource(
            _mapping.Mapping, rules=MAPPING_RULES_2, schema_version='2.0'
        )

        self.identity_sdk_client.mappings.return_value = [
            self.mapping,
            self.extra_mapping,
        ]

        # Get the command object to test
        self.cmd = mapping.ListMapping(self.app, None)

    def test_mapping_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.mappings.assert_called_with()

        collist = ('ID', 'schema_version')
        self.assertEqual(collist, columns)

        datalist = [
            (self.mapping.id, '1.0'),
            (self.extra_mapping.id, '2.0'),
        ]
        self.assertEqual(datalist, data)


class TestMappingSet(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.mapping = sdk_fakes.generate_fake_resource(
            _mapping.Mapping, rules=MAPPING_RULES, schema_version='1.0'
        )
        self.mapping_2 = sdk_fakes.generate_fake_resource(
            _mapping.Mapping, rules=MAPPING_RULES_2, schema_version='2.0'
        )
        self.identity_sdk_client.get_mapping.return_value = self.mapping
        self.identity_sdk_client.update_mapping.return_value = self.mapping_2

        # Get the command object to test
        self.cmd = mapping.SetMapping(self.app, None)

    def test_set_new_rules(self):
        arglist = [
            '--rules',
            MAPPING_RULES_FILE_PATH,
            self.mapping.id,
        ]
        verifylist = [
            ('mapping', self.mapping.id),
            ('rules', MAPPING_RULES_FILE_PATH),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = MAPPING_RULES_2
        with mock.patch(
            "openstackclient.identity.v3.mapping.SetMapping._read_rules",
            mocker,
        ):
            result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.update_mapping.assert_called_with(
            mapping=self.mapping.id,
            rules=MAPPING_RULES_2,
            schema_version=None,
        )

        self.assertIsNone(result)

    def test_set_rules_wrong_file_path(self):
        arglist = [
            '--rules',
            MAPPING_RULES_FILE_PATH,
            self.mapping.id,
        ]
        verifylist = [
            ('mapping', self.mapping.id),
            ('rules', MAPPING_RULES_FILE_PATH),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestMappingShow(identity_fakes.TestFederatedIdentity):
    def setUp(self):
        super().setUp()

        self.mapping = sdk_fakes.generate_fake_resource(
            _mapping.Mapping, rules=MAPPING_RULES, schema_version=None
        )
        self.identity_sdk_client.get_mapping.return_value = self.mapping

        self.cmd = mapping.ShowMapping(self.app, None)

    def test_mapping_show(self):
        arglist = [self.mapping.id]
        verifylist = [('mapping', self.mapping.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.get_mapping.assert_called_with(
            self.mapping.id
        )

        collist = ('id', 'rules', 'schema_version')
        self.assertEqual(collist, columns)

        datalist = (self.mapping.id, MAPPING_RULES, None)
        self.assertEqual(datalist, data)
