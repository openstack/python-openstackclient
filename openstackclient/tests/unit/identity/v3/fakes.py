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

import copy
import datetime
from unittest import mock
import uuid

from keystoneauth1 import access
from keystoneauth1 import fixture
from openstack.identity.v3 import _proxy
from osc_lib.cli import format_columns

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils

base_url = 'http://identity:5000/v3/'

domain_id = 'd1'
domain_name = 'oftheking'
domain_description = 'domain description'

DOMAIN = {
    'id': domain_id,
    'name': domain_name,
    'description': domain_description,
    'enabled': True,
    'tags': [],
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
        "local": [{"group": {"id": EMPLOYEE_GROUP_ID}}],
        "remote": [
            {"type": "orgPersonType", "not_any_of": ["Contractor", "Guest"]}
        ],
    }
]

MAPPING_RULES_2 = [
    {
        "local": [{"group": {"id": DEVELOPER_GROUP_ID}}],
        "remote": [{"type": "orgPersonType", "any_one_of": ["Contractor"]}],
    }
]


MAPPING_RESPONSE = {"id": mapping_id, "rules": MAPPING_RULES}

MAPPING_RESPONSE_2 = {"id": mapping_id, "rules": MAPPING_RULES_2}

mfa_opt1 = 'password,totp'
mfa_opt2 = 'password'

project_id = '8-9-64'
project_name = 'beatles'
project_description = 'Fab Four'

PROJECT = {
    'id': project_id,
    'name': project_name,
    'description': project_description,
    'enabled': True,
    'domain_id': domain_id,
    'tags': [],
    'links': base_url + 'projects/' + project_id,
}

PROJECT_2 = {
    'id': project_id + '-2222',
    'name': project_name + ' reprise',
    'description': project_description + 'plus four more',
    'enabled': True,
    'domain_id': domain_id,
    'tags': [],
    'links': base_url + 'projects/' + project_id,
}

region_id = 'region_one'
region_parent_region_id = 'region_two'
region_description = 'region one'

REGION = {
    'id': region_id,
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
    'tags': [],
    'links': base_url + 'projects/' + (project_id + '-with-parent'),
}

PROJECT_WITH_GRANDPARENT = {
    'id': project_id + '-with-grandparent',
    'name': project_name + ', granny and grandpa',
    'description': project_description + ' plus another eight?',
    'enabled': True,
    'domain_id': domain_id,
    'parent_id': PROJECT_WITH_PARENT['id'],
    'tags': [],
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
role_description = 'role description'

ROLE = {
    'id': role_id,
    'name': role_name,
    'domain': None,
    'links': base_url + 'roles/' + role_id,
}

ROLE_2 = {
    'id': 'r2',
    'name': 'Rolls Royce',
    'domain': domain_id,
    'links': base_url + 'roles/' + 'r2',
}

ROLES = [ROLE, ROLE_2]

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

endpoint_group_id = 'eg-123'
endpoint_group_description = 'eg 123 description'
endpoint_group_filters = {
    'service_id': service_id,
    'region_id': endpoint_region,
}
endpoint_group_filters_2 = {
    'region_id': endpoint_region,
}
endpoint_group_file_path = '/tmp/path/to/file'

ENDPOINT_GROUP = {
    'id': endpoint_group_id,
    'filters': endpoint_group_filters,
    'description': endpoint_group_description,
    'links': base_url + 'endpoint_groups/' + endpoint_group_id,
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
trust_roles = ({"id": role_id, "name": role_name},)

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

token_expires = '2016-09-05T18:04:52+0000'
token_id = 'tttttttt-tttt-tttt-tttt-tttttttttttt'

UNSCOPED_TOKEN = {
    'expires': token_expires,
    'id': token_id,
    'user_id': user_id,
}

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
formatted_idp_remote_ids = format_columns.ListColumn(idp_remote_ids)

IDENTITY_PROVIDER = {
    'id': idp_id,
    'remote_ids': idp_remote_ids,
    'enabled': True,
    'description': idp_description,
    'domain_id': domain_id,
}

protocol_id = 'protocol'

mapping_id = 'test_mapping'
mapping_id_updated = 'prod_mapping'

sp_id = 'BETA'
sp_description = 'Service Provider to burst into'
service_provider_url = 'https://beta.example.com/Shibboleth.sso/POST/SAML'
sp_auth_url = (
    'https://beta.example.com/v3/OS-FEDERATION/identity_providers/'
    'idp/protocol/saml2/auth'
)

SERVICE_PROVIDER = {
    'id': sp_id,
    'enabled': True,
    'description': sp_description,
    'sp_url': service_provider_url,
    'auth_url': sp_auth_url,
}

PROTOCOL_ID_MAPPING = {'id': protocol_id, 'mapping': mapping_id}

PROTOCOL_OUTPUT = {
    'id': protocol_id,
    'mapping_id': mapping_id,
    'identity_provider': idp_id,
}

PROTOCOL_OUTPUT_UPDATED = {
    'id': protocol_id,
    'mapping_id': mapping_id_updated,
    'identity_provider': idp_id,
}

# Assignments

ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID = {
    'scope': {'project': {'id': project_id}},
    'user': {'id': user_id},
    'role': {'id': role_id},
}

ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID_INCLUDE_NAMES = {
    'scope': {
        'project': {
            'domain': {'id': domain_id, 'name': domain_name},
            'id': project_id,
            'name': project_name,
        }
    },
    'user': {
        'domain': {'id': domain_id, 'name': domain_name},
        'id': user_id,
        'name': user_name,
    },
    'role': {'id': role_id, 'name': role_name},
}

ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID_INHERITED = {
    'scope': {
        'project': {'id': project_id},
        'OS-INHERIT:inherited_to': 'projects',
    },
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

ASSIGNMENT_WITH_DOMAIN_ROLE = {
    'scope': {'domain': {'id': domain_id}},
    'user': {'id': user_id},
    'role': {'id': ROLE_2['id']},
}

ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID_INCLUDE_NAMES = {
    'scope': {'domain': {'id': domain_id, 'name': domain_name}},
    'user': {
        'domain': {'id': domain_id, 'name': domain_name},
        'id': user_id,
        'name': user_name,
    },
    'role': {'id': role_id, 'name': role_name},
}

ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID_INHERITED = {
    'scope': {
        'domain': {'id': domain_id},
        'OS-INHERIT:inherited_to': 'projects',
    },
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
    'description': consumer_description,
}

access_token_id = 'test access token id'
access_token_secret = 'test access token secret'
access_token_expires = '2014-05-18T03:13:18.152071Z'

OAUTH_ACCESS_TOKEN = {
    'id': access_token_id,
    'expires': access_token_expires,
    'key': access_token_id,
    'secret': access_token_secret,
}

request_token_id = 'test request token id'
request_token_secret = 'test request token secret'
request_token_expires = '2014-05-17T11:10:51.511336Z'

OAUTH_REQUEST_TOKEN = {
    'id': request_token_id,
    'expires': request_token_expires,
    'key': request_token_id,
    'secret': request_token_secret,
}

oauth_verifier_pin = '6d74XaDS'
OAUTH_VERIFIER = {'oauth_verifier': oauth_verifier_pin}

app_cred_id = 'app-cred-id'
app_cred_name = 'testing_app_cred'
app_cred_role = ({"id": role_id, "name": role_name, "domain": None},)
app_cred_description = 'app credential for testing'
app_cred_expires = datetime.datetime(2022, 1, 1, 0, 0)
app_cred_expires_str = app_cred_expires.strftime('%Y-%m-%dT%H:%M:%S%z')
app_cred_secret = 'moresecuresecret'
app_cred_access_rules = (
    '[{"path": "/v2.1/servers", "method": "GET", "service": "compute"}]'
)
app_cred_access_rules_path = '/tmp/access_rules.json'
access_rule_id = 'access-rule-id'
access_rule_service = 'compute'
access_rule_path = '/v2.1/servers'
access_rule_method = 'GET'
APP_CRED_BASIC = {
    'id': app_cred_id,
    'name': app_cred_name,
    'project_id': project_id,
    'roles': app_cred_role,
    'description': None,
    'expires_at': None,
    'unrestricted': False,
    'secret': app_cred_secret,
    'access_rules': None,
}
APP_CRED_OPTIONS = {
    'id': app_cred_id,
    'name': app_cred_name,
    'project_id': project_id,
    'roles': app_cred_role,
    'description': app_cred_description,
    'expires_at': app_cred_expires_str,
    'unrestricted': False,
    'secret': app_cred_secret,
    'access_rules': None,
}
ACCESS_RULE = {
    'id': access_rule_id,
    'service': access_rule_service,
    'path': access_rule_path,
    'method': access_rule_method,
}
APP_CRED_ACCESS_RULES = {
    'id': app_cred_id,
    'name': app_cred_name,
    'project_id': project_id,
    'roles': app_cred_role,
    'description': None,
    'expires_at': None,
    'unrestricted': False,
    'secret': app_cred_secret,
    'access_rules': app_cred_access_rules,
}

registered_limit_id = 'registered-limit-id'
registered_limit_default_limit = 10
registered_limit_description = 'default limit of foobars'
registered_limit_resource_name = 'foobars'
REGISTERED_LIMIT = {
    'id': registered_limit_id,
    'default_limit': registered_limit_default_limit,
    'resource_name': registered_limit_resource_name,
    'service_id': service_id,
    'description': None,
    'region_id': None,
}
REGISTERED_LIMIT_OPTIONS = {
    'id': registered_limit_id,
    'default_limit': registered_limit_default_limit,
    'resource_name': registered_limit_resource_name,
    'service_id': service_id,
    'description': registered_limit_description,
    'region_id': region_id,
}

limit_id = 'limit-id'
limit_resource_limit = 15
limit_description = 'limit of foobars'
limit_resource_name = 'foobars'
LIMIT = {
    'id': limit_id,
    'project_id': project_id,
    'resource_limit': limit_resource_limit,
    'resource_name': limit_resource_name,
    'service_id': service_id,
    'description': None,
    'region_id': None,
}
LIMIT_OPTIONS = {
    'id': limit_id,
    'project_id': project_id,
    'resource_limit': limit_resource_limit,
    'resource_name': limit_resource_name,
    'service_id': service_id,
    'description': limit_description,
    'region_id': region_id,
}


def fake_auth_ref(fake_token, fake_service=None):
    """Create an auth_ref using keystoneauth's fixtures"""
    token_copy = copy.deepcopy(fake_token)
    token_id = token_copy.pop('id')
    token = fixture.V3Token(**token_copy)
    # An auth_ref is actually an access info object
    auth_ref = access.create(
        body=token,
        auth_token=token_id,
    )

    # Create a service catalog
    if fake_service:
        service = token.add_service(
            fake_service['type'],
            fake_service['name'],
        )
        # TODO(dtroyer): Add an 'id' element to KSA's _Service fixure
        service['id'] = fake_service['id']
        for e in fake_service['endpoints']:
            region = e.get('region_id') or e.get('region', '<none>')
            service.add_endpoint(
                e['interface'],
                e['url'],
                region=region,
            )

    return auth_ref


class FakeAuth:
    def __init__(self, auth_method_class=None):
        self._auth_method_class = auth_method_class

    def get_token(self, *args, **kwargs):
        return token_id


class FakeSession:
    def __init__(self, **kwargs):
        self.auth = FakeAuth()


class FakeIdentityv3Client:
    def __init__(self, **kwargs):
        self.domains = mock.Mock()
        self.domains.resource_class = fakes.FakeResource(None, {})
        self.credentials = mock.Mock()
        self.credentials.resource_class = fakes.FakeResource(None, {})
        self.endpoints = mock.Mock()
        self.endpoints.resource_class = fakes.FakeResource(None, {})
        self.endpoint_filter = mock.Mock()
        self.endpoint_filter.resource_class = fakes.FakeResource(None, {})
        self.endpoint_groups = mock.Mock()
        self.endpoint_groups.resource_class = fakes.FakeResource(None, {})
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
        self.session.auth.auth_ref.service_catalog.resource_class = (
            fakes.FakeResource(None, {})
        )
        self.tokens = mock.Mock()
        self.tokens.resource_class = fakes.FakeResource(None, {})
        self.trusts = mock.Mock()
        self.trusts.resource_class = fakes.FakeResource(None, {})
        self.users = mock.Mock()
        self.users.resource_class = fakes.FakeResource(None, {})
        self.role_assignments = mock.Mock()
        self.role_assignments.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']
        self.auth = FakeAuth()
        self.auth.client = mock.Mock()
        self.auth.client.resource_class = fakes.FakeResource(None, {})
        self.application_credentials = mock.Mock()
        self.application_credentials.resource_class = fakes.FakeResource(
            None, {}
        )
        self.access_rules = mock.Mock()
        self.access_rules.resource_class = fakes.FakeResource(None, {})
        self.inference_rules = mock.Mock()
        self.inference_rules.resource_class = fakes.FakeResource(None, {})
        self.registered_limits = mock.Mock()
        self.registered_limits.resource_class = fakes.FakeResource(None, {})
        self.limits = mock.Mock()
        self.limits.resource_class = fakes.FakeResource(None, {})


class FakeFederationManager:
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
        super().__init__(**kwargs)
        self.federation = FakeFederationManager()


class FakeOAuth1Client(FakeIdentityv3Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.access_tokens = mock.Mock()
        self.access_tokens.resource_class = fakes.FakeResource(None, {})
        self.consumers = mock.Mock()
        self.consumers.resource_class = fakes.FakeResource(None, {})
        self.request_tokens = mock.Mock()
        self.request_tokens.resource_class = fakes.FakeResource(None, {})


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.identity = FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.identity_client = self.app.client_manager.identity

        # TODO(stephenfin): Rename to 'identity_client' once all commands are
        # migrated to SDK
        self.app.client_manager.sdk_connection.identity = mock.Mock(
            _proxy.Proxy
        )
        self.identity_sdk_client = (
            self.app.client_manager.sdk_connection.identity
        )


class TestIdentityv3(
    FakeClientMixin,
    utils.TestCommand,
): ...


# We don't use FakeClientMixin since we want a different fake legacy client
class TestFederatedIdentity(utils.TestCommand):
    def setUp(self):
        super().setUp()

        self.app.client_manager.identity = FakeFederatedClient(
            endpoint=fakes.AUTH_URL, token=fakes.AUTH_TOKEN
        )
        self.identity_client = self.app.client_manager.identity

        # TODO(stephenfin): Rename to 'identity_client' once all commands are
        # migrated to SDK
        self.app.client_manager.sdk_connection.identity = mock.Mock(
            _proxy.Proxy
        )
        self.identity_sdk_client = (
            self.app.client_manager.sdk_connection.identity
        )


# We don't use FakeClientMixin since we want a different fake legacy client
class TestOAuth1(utils.TestCommand):
    def setUp(self):
        super().setUp()

        self.app.client_manager.identity = FakeOAuth1Client(
            endpoint=fakes.AUTH_URL, token=fakes.AUTH_TOKEN
        )
        self.identity_client = self.app.client_manager.identity

        # TODO(stephenfin): Rename to 'identity_client' once all commands are
        # migrated to SDK
        self.app.client_manager.sdk_connection.identity = mock.Mock(
            _proxy.Proxy
        )
        self.identity_sdk_client = (
            self.app.client_manager.sdk_connection.identity
        )


class FakeProject:
    """Fake one or more project."""

    @staticmethod
    def create_one_project(attrs=None):
        """Create a fake project.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        project_info = {
            'id': 'project-id-' + uuid.uuid4().hex,
            'name': 'project-name-' + uuid.uuid4().hex,
            'description': 'project-description-' + uuid.uuid4().hex,
            'enabled': True,
            'is_domain': False,
            'domain_id': 'domain-id-' + uuid.uuid4().hex,
            'parent_id': 'parent-id-' + uuid.uuid4().hex,
            'tags': [],
            'links': 'links-' + uuid.uuid4().hex,
        }
        project_info.update(attrs)

        project = fakes.FakeResource(
            info=copy.deepcopy(project_info), loaded=True
        )
        return project

    @staticmethod
    def create_projects(attrs=None, count=2):
        """Create multiple fake projects.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of projects to fake
        :return:
            A list of FakeResource objects faking the projects
        """

        projects = []
        for i in range(0, count):
            projects.append(FakeProject.create_one_project(attrs))
        return projects


class FakeDomain:
    """Fake one or more domain."""

    @staticmethod
    def create_one_domain(attrs=None):
        """Create a fake domain.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        domain_info = {
            'id': 'domain-id-' + uuid.uuid4().hex,
            'name': 'domain-name-' + uuid.uuid4().hex,
            'description': 'domain-description-' + uuid.uuid4().hex,
            'enabled': True,
            'tags': [],
            'links': 'links-' + uuid.uuid4().hex,
        }
        domain_info.update(attrs)

        domain = fakes.FakeResource(
            info=copy.deepcopy(domain_info), loaded=True
        )
        return domain


class FakeCredential:
    """Fake one or more credential."""

    @staticmethod
    def create_one_credential(attrs=None):
        """Create a fake credential.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, type, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        credential_info = {
            'id': 'credential-id-' + uuid.uuid4().hex,
            'type': 'cert',
            'user_id': 'user-id-' + uuid.uuid4().hex,
            'blob': 'credential-data-' + uuid.uuid4().hex,
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'links': 'links-' + uuid.uuid4().hex,
        }
        credential_info.update(attrs)

        credential = fakes.FakeResource(
            info=copy.deepcopy(credential_info), loaded=True
        )
        return credential

    @staticmethod
    def create_credentials(attrs=None, count=2):
        """Create multiple fake credentials.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of credentials to fake
        :return:
            A list of FakeResource objects faking the credentials
        """
        credentials = []
        for i in range(0, count):
            credential = FakeCredential.create_one_credential(attrs)
            credentials.append(credential)

        return credentials

    @staticmethod
    def get_credentials(credentials=None, count=2):
        """Get an iterable MagicMock object with a list of faked credentials.

        If credentials list is provided, then initialize the Mock object with
        the list. Otherwise create one.

        :param List credentials:
            A list of FakeResource objects faking credentials
        :param Integer count:
            The number of credentials to be faked
        :return:
            An iterable Mock object with side_effect set to a list of faked
            credentials
        """
        if credentials is None:
            credentials = FakeCredential.create_credentials(count)

        return mock.Mock(side_effect=credentials)


class FakeUser:
    """Fake one or more user."""

    @staticmethod
    def create_one_user(attrs=None):
        """Create a fake user.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        user_info = {
            'id': 'user-id-' + uuid.uuid4().hex,
            'name': 'user-name-' + uuid.uuid4().hex,
            'default_project_id': 'project-' + uuid.uuid4().hex,
            'email': 'user-email-' + uuid.uuid4().hex,
            'enabled': True,
            'domain_id': 'domain-id-' + uuid.uuid4().hex,
            'links': 'links-' + uuid.uuid4().hex,
        }
        user_info.update(attrs)

        user = fakes.FakeResource(info=copy.deepcopy(user_info), loaded=True)
        return user

    @staticmethod
    def create_users(attrs=None, count=2):
        """Create multiple fake users.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of users to fake
        :return:
            A list of FakeResource objects faking the users
        """
        users = []
        for i in range(0, count):
            user = FakeUser.create_one_user(attrs)
            users.append(user)

        return users

    @staticmethod
    def get_users(users=None, count=2):
        """Get an iterable MagicMock object with a list of faked users.

        If users list is provided, then initialize the Mock object with
        the list. Otherwise create one.

        :param List users:
            A list of FakeResource objects faking users
        :param Integer count:
            The number of users to be faked
        :return
            An iterable Mock object with side_effect set to a list of faked
            users
        """
        if users is None:
            users = FakeUser.create_users(count)

        return mock.Mock(side_effect=users)


class FakeGroup:
    """Fake one or more group."""

    @staticmethod
    def create_one_group(attrs=None):
        """Create a fake group.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        group_info = {
            'id': 'group-id-' + uuid.uuid4().hex,
            'name': 'group-name-' + uuid.uuid4().hex,
            'links': 'links-' + uuid.uuid4().hex,
            'domain_id': 'domain-id-' + uuid.uuid4().hex,
            'description': 'group-description-' + uuid.uuid4().hex,
        }
        group_info.update(attrs)

        group = fakes.FakeResource(info=copy.deepcopy(group_info), loaded=True)
        return group

    @staticmethod
    def create_groups(attrs=None, count=2):
        """Create multiple fake groups.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of groups to fake
        :return:
            A list of FakeResource objects faking the groups
        """
        groups = []
        for i in range(0, count):
            group = FakeGroup.create_one_group(attrs)
            groups.append(group)

        return groups

    @staticmethod
    def get_groups(groups=None, count=2):
        """Get an iterable MagicMock object with a list of faked groups.

        If groups list is provided, then initialize the Mock object with
        the list. Otherwise create one.

        :param List groups:
            A list of FakeResource objects faking groups
        :param Integer count:
            The number of groups to be faked
        :return:
            An iterable Mock object with side_effect set to a list of faked
            groups
        """
        if groups is None:
            groups = FakeGroup.create_groups(count)

        return mock.Mock(side_effect=groups)


class FakeEndpoint:
    """Fake one or more endpoint."""

    @staticmethod
    def create_one_endpoint(attrs=None):
        """Create a fake endpoint.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, url, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        endpoint_info = {
            'id': 'endpoint-id-' + uuid.uuid4().hex,
            'url': 'url-' + uuid.uuid4().hex,
            'region': 'endpoint-region-' + uuid.uuid4().hex,
            'interface': 'admin',
            'service_id': 'service-id-' + uuid.uuid4().hex,
            'enabled': True,
            'links': 'links-' + uuid.uuid4().hex,
        }
        endpoint_info.update(attrs)

        endpoint = fakes.FakeResource(
            info=copy.deepcopy(endpoint_info), loaded=True
        )
        return endpoint

    @staticmethod
    def create_one_endpoint_filter(attrs=None):
        """Create a fake endpoint project relationship.

        :param Dictionary attrs:
            A dictionary with all attributes of endpoint filter
        :return:
            A FakeResource object with project, endpoint and so on
        """
        attrs = attrs or {}

        # Set default attribute
        endpoint_filter_info = {
            'project': 'project-id-' + uuid.uuid4().hex,
            'endpoint': 'endpoint-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes if there are some attributes set
        endpoint_filter_info.update(attrs)

        endpoint_filter = fakes.FakeModel(copy.deepcopy(endpoint_filter_info))

        return endpoint_filter


class FakeEndpointGroup:
    """Fake one or more endpoint group."""

    @staticmethod
    def create_one_endpointgroup(attrs=None):
        """Create a fake endpoint group.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, url, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        endpointgroup_info = {
            'id': 'endpoint-group-id-' + uuid.uuid4().hex,
            'name': 'endpoint-group-name-' + uuid.uuid4().hex,
            'filters': {
                'region': 'region-' + uuid.uuid4().hex,
                'service_id': 'service-id-' + uuid.uuid4().hex,
            },
            'description': 'endpoint-group-description-' + uuid.uuid4().hex,
            'links': 'links-' + uuid.uuid4().hex,
        }
        endpointgroup_info.update(attrs)

        endpoint = fakes.FakeResource(
            info=copy.deepcopy(endpointgroup_info), loaded=True
        )
        return endpoint

    @staticmethod
    def create_one_endpointgroup_filter(attrs=None):
        """Create a fake endpoint project relationship.

        :param Dictionary attrs:
            A dictionary with all attributes of endpointgroup filter
        :return:
            A FakeResource object with project, endpointgroup and so on
        """
        attrs = attrs or {}

        # Set default attribute
        endpointgroup_filter_info = {
            'project': 'project-id-' + uuid.uuid4().hex,
            'endpointgroup': 'endpointgroup-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes if there are some attributes set
        endpointgroup_filter_info.update(attrs)

        endpointgroup_filter = fakes.FakeModel(
            copy.deepcopy(endpointgroup_filter_info)
        )

        return endpointgroup_filter


class FakeService:
    """Fake one or more service."""

    @staticmethod
    def create_one_service(attrs=None):
        """Create a fake service.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        service_info = {
            'id': 'service-id-' + uuid.uuid4().hex,
            'name': 'service-name-' + uuid.uuid4().hex,
            'type': 'service-type-' + uuid.uuid4().hex,
            'description': 'service-description-' + uuid.uuid4().hex,
            'enabled': True,
            'links': 'links-' + uuid.uuid4().hex,
        }
        service_info.update(attrs)

        service = fakes.FakeResource(
            info=copy.deepcopy(service_info), loaded=True
        )
        return service


class FakeRoleAssignment:
    """Fake one or more role assignment."""

    @staticmethod
    def create_one_role_assignment(attrs=None):
        """Create a fake role assignment.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with scope, user, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        role_assignment_info = {
            'scope': {'project': {'id': 'project-id-' + uuid.uuid4().hex}},
            'user': {'id': 'user-id-' + uuid.uuid4().hex},
            'role': {'id': 'role-id-' + uuid.uuid4().hex},
        }
        role_assignment_info.update(attrs)

        role_assignment = fakes.FakeResource(
            info=copy.deepcopy(role_assignment_info), loaded=True
        )

        return role_assignment


class FakeImpliedRoleResponse:
    """Fake one or more role assignment."""

    def __init__(self, prior_role, implied_roles):
        self.prior_role = prior_role
        self.implies = [role for role in implied_roles]

    @staticmethod
    def create_list():
        """Create a fake implied role list response.

        :return:
            A list of FakeImpliedRoleResponse objects
        """

        # set default attributes.
        implied_roles = [FakeImpliedRoleResponse(ROLES[0], [ROLES[1]])]

        return implied_roles
