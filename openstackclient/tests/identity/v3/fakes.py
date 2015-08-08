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

import mock

from openstackclient.tests import fakes
from openstackclient.tests import utils

base_url = 'http://identity:5000/v3/'

domain_id = 'd1'
domain_name = 'oftheking'
domain_description = 'domain description'

DOMAIN = {
    'id': domain_id,
    'name': domain_name,
    'description': domain_description,
    'enabled': True,
    'links': base_url + 'domains/' + domain_id,
}

group_id = 'gr-010'
group_name = 'spencer davis'

GROUP = {
    'id': group_id,
    'name': group_name,
    'links': base_url + 'groups/' + group_id,
}

mapping_id = 'test_mapping'
mapping_rules_file_path = '/tmp/path/to/file'
# Copied from
# (https://github.com/openstack/keystone/blob\
# master/keystone/tests/mapping_fixtures.py
EMPLOYEE_GROUP_ID = "0cd5e9"
DEVELOPER_GROUP_ID = "xyz"
MAPPING_RULES = [
    {
        "local": [
            {
                "group": {
                    "id": EMPLOYEE_GROUP_ID
                }
            }
        ],
        "remote": [
            {
                "type": "orgPersonType",
                "not_any_of": [
                    "Contractor",
                    "Guest"
                ]
            }
        ]
    }
]

MAPPING_RULES_2 = [
    {
        "local": [
            {
                "group": {
                    "id": DEVELOPER_GROUP_ID
                }
            }
        ],
        "remote": [
            {
                "type": "orgPersonType",
                "any_one_of": [
                    "Contractor"
                ]
            }
        ]
    }
]


MAPPING_RESPONSE = {
    "id": mapping_id,
    "rules": MAPPING_RULES
}

MAPPING_RESPONSE_2 = {
    "id": mapping_id,
    "rules": MAPPING_RULES_2
}

project_id = '8-9-64'
project_name = 'beatles'
project_description = 'Fab Four'

PROJECT = {
    'id': project_id,
    'name': project_name,
    'description': project_description,
    'enabled': True,
    'domain_id': domain_id,
    'links': base_url + 'projects/' + project_id,
}

PROJECT_2 = {
    'id': project_id + '-2222',
    'name': project_name + ' reprise',
    'description': project_description + 'plus four more',
    'enabled': True,
    'domain_id': domain_id,
    'links': base_url + 'projects/' + project_id,
}

region_id = 'region_one'
region_url = 'http://localhost:1111'
region_parent_region_id = 'region_two'
region_description = 'region one'

REGION = {
    'id': region_id,
    'url': region_url,
    'description': region_description,
    'parent_region_id': region_parent_region_id,
    'links': base_url + 'regions/' + region_id,
}

PROJECT_WITH_PARENT = {
    'id': project_id + '-with-parent',
    'name': project_name + ' and their parents',
    'description': project_description + ' plus another four',
    'enabled': True,
    'domain_id': domain_id,
    'parent_id': project_id,
    'links': base_url + 'projects/' + (project_id + '-with-parent'),
}

PROJECT_WITH_GRANDPARENT = {
    'id': project_id + '-with-grandparent',
    'name': project_name + ', granny and grandpa',
    'description': project_description + ' plus another eight?',
    'enabled': True,
    'domain_id': domain_id,
    'parent_id': PROJECT_WITH_PARENT['id'],
    'links': base_url + 'projects/' + (project_id + '-with-grandparent'),
}

parents = [{'project': PROJECT}]
grandparents = [{'project': PROJECT}, {'project': PROJECT_WITH_PARENT}]
ids_for_parents = [PROJECT['id']]
ids_for_parents_and_grandparents = [PROJECT['id'], PROJECT_WITH_PARENT['id']]

children = [{'project': PROJECT_WITH_GRANDPARENT}]
ids_for_children = [PROJECT_WITH_GRANDPARENT['id']]


role_id = 'r1'
role_name = 'roller'

ROLE = {
    'id': role_id,
    'name': role_name,
    'links': base_url + 'roles/' + role_id,
}

service_id = 's-123'
service_name = 'Texaco'
service_type = 'gas'
service_description = 'oil brand'

SERVICE = {
    'id': service_id,
    'name': service_name,
    'type': service_type,
    'description': service_description,
    'enabled': True,
    'links': base_url + 'services/' + service_id,
}

SERVICE_WITHOUT_NAME = {
    'id': service_id,
    'type': service_type,
    'description': service_description,
    'enabled': True,
    'links': base_url + 'services/' + service_id,
}

endpoint_id = 'e-123'
endpoint_url = 'http://127.0.0.1:35357'
endpoint_region = 'RegionOne'
endpoint_interface = 'admin'

ENDPOINT = {
    'id': endpoint_id,
    'url': endpoint_url,
    'region': endpoint_region,
    'interface': endpoint_interface,
    'service_id': service_id,
    'enabled': True,
    'links': base_url + 'endpoints/' + endpoint_id,
}

user_id = 'bbbbbbb-aaaa-aaaa-aaaa-bbbbbbbaaaa'
user_name = 'paul'
user_description = 'Sir Paul'
user_email = 'paul@applecorps.com'

USER = {
    'id': user_id,
    'name': user_name,
    'default_project_id': project_id,
    'email': user_email,
    'enabled': True,
    'domain_id': domain_id,
    'links': base_url + 'users/' + user_id,
}

trust_id = 't-456'
trust_expires = None
trust_impersonation = False
trust_roles = {"id": role_id, "name": role_name},

TRUST = {
    'expires_at': trust_expires,
    'id': trust_id,
    'impersonation': trust_impersonation,
    'links': base_url + 'trusts/' + trust_id,
    'project_id': project_id,
    'roles': trust_roles,
    'trustee_user_id': user_id,
    'trustor_user_id': user_id,
}

token_expires = '2014-01-01T00:00:00Z'
token_id = 'tttttttt-tttt-tttt-tttt-tttttttttttt'

TOKEN_WITH_PROJECT_ID = {
    'expires': token_expires,
    'id': token_id,
    'project_id': project_id,
    'user_id': user_id,
}

TOKEN_WITH_DOMAIN_ID = {
    'expires': token_expires,
    'id': token_id,
    'domain_id': domain_id,
    'user_id': user_id,
}

idp_id = 'test_idp'
idp_description = 'super exciting IdP description'
idp_remote_ids = ['entity1', 'entity2']

IDENTITY_PROVIDER = {
    'id': idp_id,
    'remote_ids': idp_remote_ids,
    'enabled': True,
    'description': idp_description
}

protocol_id = 'protocol'

mapping_id = 'test_mapping'
mapping_id_updated = 'prod_mapping'

sp_id = 'BETA'
sp_description = 'Service Provider to burst into'
service_provider_url = 'https://beta.example.com/Shibboleth.sso/POST/SAML'
sp_auth_url = ('https://beta.example.com/v3/OS-FEDERATION/identity_providers/'
               'idp/protocol/saml2/auth')

SERVICE_PROVIDER = {
    'id': sp_id,
    'enabled': True,
    'description': sp_description,
    'sp_url': service_provider_url,
    'auth_url': sp_auth_url
}

PROTOCOL_ID_MAPPING = {
    'id': protocol_id,
    'mapping': mapping_id
}

PROTOCOL_OUTPUT = {
    'id': protocol_id,
    'mapping_id': mapping_id,
    'identity_provider': idp_id
}

PROTOCOL_OUTPUT_UPDATED = {
    'id': protocol_id,
    'mapping_id': mapping_id_updated,
    'identity_provider': idp_id
}

# Assignments

ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID = {
    'scope': {'project': {'id': project_id}},
    'user': {'id': user_id},
    'role': {'id': role_id},
}

ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID_INHERITED = {
    'scope': {'project': {'id': project_id},
              'OS-INHERIT:inherited_to': 'projects'},
    'user': {'id': user_id},
    'role': {'id': role_id},
}

ASSIGNMENT_WITH_PROJECT_ID_AND_GROUP_ID = {
    'scope': {'project': {'id': project_id}},
    'group': {'id': group_id},
    'role': {'id': role_id},
}

ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID = {
    'scope': {'domain': {'id': domain_id}},
    'user': {'id': user_id},
    'role': {'id': role_id},
}

ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID_INHERITED = {
    'scope': {'domain': {'id': domain_id},
              'OS-INHERIT:inherited_to': 'projects'},
    'user': {'id': user_id},
    'role': {'id': role_id},
}

ASSIGNMENT_WITH_DOMAIN_ID_AND_GROUP_ID = {
    'scope': {'domain': {'id': domain_id}},
    'group': {'id': group_id},
    'role': {'id': role_id},
}

consumer_id = 'test consumer id'
consumer_description = 'someone we trust'
consumer_secret = 'test consumer secret'

OAUTH_CONSUMER = {
    'id': consumer_id,
    'secret': consumer_secret,
    'description': consumer_description
}

access_token_id = 'test access token id'
access_token_secret = 'test access token secret'
access_token_expires = '2014-05-18T03:13:18.152071Z'

OAUTH_ACCESS_TOKEN = {
    'id': access_token_id,
    'expires': access_token_expires,
    'key': access_token_id,
    'secret': access_token_secret
}

request_token_id = 'test request token id'
request_token_secret = 'test request token secret'
request_token_expires = '2014-05-17T11:10:51.511336Z'

OAUTH_REQUEST_TOKEN = {
    'id': request_token_id,
    'expires': request_token_expires,
    'key': request_token_id,
    'secret': request_token_secret
}

oauth_verifier_pin = '6d74XaDS'
OAUTH_VERIFIER = {
    'oauth_verifier': oauth_verifier_pin
}


class FakeAuth(object):
    def __init__(self, auth_method_class=None):
        self._auth_method_class = auth_method_class

    def get_token(self, *args, **kwargs):
        return token_id


class FakeSession(object):
    def __init__(self, **kwargs):
        self.auth = FakeAuth()


class FakeIdentityv3Client(object):
    def __init__(self, **kwargs):
        self.domains = mock.Mock()
        self.domains.resource_class = fakes.FakeResource(None, {})
        self.endpoints = mock.Mock()
        self.endpoints.resource_class = fakes.FakeResource(None, {})
        self.groups = mock.Mock()
        self.groups.resource_class = fakes.FakeResource(None, {})
        self.oauth1 = mock.Mock()
        self.oauth1.resource_class = fakes.FakeResource(None, {})
        self.projects = mock.Mock()
        self.projects.resource_class = fakes.FakeResource(None, {})
        self.regions = mock.Mock()
        self.regions.resource_class = fakes.FakeResource(None, {})
        self.roles = mock.Mock()
        self.roles.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.session = mock.Mock()
        self.session.auth.auth_ref.service_catalog.resource_class = \
            fakes.FakeResource(None, {})
        self.trusts = mock.Mock()
        self.trusts.resource_class = fakes.FakeResource(None, {})
        self.users = mock.Mock()
        self.users.resource_class = fakes.FakeResource(None, {})
        self.role_assignments = mock.Mock()
        self.role_assignments.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class FakeFederationManager(object):
    def __init__(self, **kwargs):
        self.identity_providers = mock.Mock()
        self.identity_providers.resource_class = fakes.FakeResource(None, {})
        self.mappings = mock.Mock()
        self.mappings.resource_class = fakes.FakeResource(None, {})
        self.protocols = mock.Mock()
        self.protocols.resource_class = fakes.FakeResource(None, {})
        self.projects = mock.Mock()
        self.projects.resource_class = fakes.FakeResource(None, {})
        self.domains = mock.Mock()
        self.domains.resource_class = fakes.FakeResource(None, {})
        self.service_providers = mock.Mock()
        self.service_providers.resource_class = fakes.FakeResource(None, {})


class FakeFederatedClient(FakeIdentityv3Client):
    def __init__(self, **kwargs):
        super(FakeFederatedClient, self).__init__(**kwargs)
        self.federation = FakeFederationManager()


class FakeOAuth1Client(FakeIdentityv3Client):
    def __init__(self, **kwargs):
        super(FakeOAuth1Client, self).__init__(**kwargs)

        self.access_tokens = mock.Mock()
        self.access_tokens.resource_class = fakes.FakeResource(None, {})
        self.consumers = mock.Mock()
        self.consumers.resource_class = fakes.FakeResource(None, {})
        self.request_tokens = mock.Mock()
        self.request_tokens.resource_class = fakes.FakeResource(None, {})


class TestIdentityv3(utils.TestCommand):
    def setUp(self):
        super(TestIdentityv3, self).setUp()

        self.app.client_manager.identity = FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


class TestFederatedIdentity(utils.TestCommand):
    def setUp(self):
        super(TestFederatedIdentity, self).setUp()

        self.app.client_manager.identity = FakeFederatedClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )


class TestOAuth1(utils.TestCommand):
    def setUp(self):
        super(TestOAuth1, self).setUp()

        self.app.client_manager.identity = FakeOAuth1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )
