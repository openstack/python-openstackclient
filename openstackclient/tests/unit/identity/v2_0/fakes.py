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
from unittest import mock
import uuid

from keystoneauth1 import access
from keystoneauth1 import fixture
from openstack.identity.v2 import _proxy

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils


project_id = '8-9-64'
project_name = 'beatles'
project_description = 'Fab Four'

PROJECT = {
    'id': project_id,
    'name': project_name,
    'description': project_description,
    'enabled': True,
}

PROJECT_2 = {
    'id': project_id + '-2222',
    'name': project_name + ' reprise',
    'description': project_description + 'plus four more',
    'enabled': True,
}

role_id = '1'
role_name = 'boss'

ROLE = {
    'id': role_id,
    'name': role_name,
}

ROLE_2 = {
    'id': '2',
    'name': 'bigboss',
}

service_id = '1925-10-11'
service_name = 'elmore'
service_description = 'Leonard, Elmore, rip'
service_type = 'author'

SERVICE = {
    'id': service_id,
    'name': service_name,
    'description': service_description,
    'type': service_type,
}

user_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
user_name = 'paul'
user_description = 'Sir Paul'
user_email = 'paul@applecorps.com'

USER = {
    'id': user_id,
    'name': user_name,
    'tenantId': project_id,
    'email': user_email,
    'enabled': True,
}

token_expires = '2016-09-05T18:04:52+0000'
token_id = 'token-id-' + uuid.uuid4().hex

TOKEN = {
    'expires': token_expires,
    'id': token_id,
    'tenant_id': 'project-id',
    'user_id': 'user-id',
}

UNSCOPED_TOKEN = {
    'expires': token_expires,
    'id': token_id,
    'user_id': 'user-id',
}

endpoint_name = service_name
endpoint_adminurl = 'https://admin.example.com/v2/UUID'
endpoint_region = 'RegionOne'
endpoint_internalurl = 'https://internal.example.com/v2/UUID'
endpoint_type = service_type
endpoint_id = '11b41ee1b00841128b7333d4bf1a6140'
endpoint_publicurl = 'https://public.example.com/v2/UUID'
endpoint_service_id = service_id

ENDPOINT = {
    'service_name': endpoint_name,
    'adminurl': endpoint_adminurl,
    'region': endpoint_region,
    'internalurl': endpoint_internalurl,
    'service_type': endpoint_type,
    'id': endpoint_id,
    'publicurl': endpoint_publicurl,
    'service_id': endpoint_service_id,
}


def fake_auth_ref(fake_token, fake_service=None):
    """Create an auth_ref using keystoneauth's fixtures"""
    token_copy = copy.deepcopy(fake_token)
    token_copy['token_id'] = token_copy.pop('id')
    token = fixture.V2Token(**token_copy)
    # An auth_ref is actually an access info object
    auth_ref = access.create(body=token)

    # Create a service catalog
    if fake_service:
        service = token.add_service(
            fake_service.type,
            fake_service.name,
        )
        # TODO(dtroyer): Add an 'id' element to KSA's _Service fixure
        service['id'] = fake_service.id
        for e in fake_service.endpoints:
            # KSA's _Service fixture copies publicURL to internalURL and
            # adminURL if they do not exist.  Soooo helpful...
            internal = e.get('internalURL', None)
            admin = e.get('adminURL', None)
            region = e.get('region_id') or e.get('region', '<none>')
            endpoint = service.add_endpoint(
                public=e['publicURL'],
                internal=internal,
                admin=admin,
                region=region,
            )
            # ...so undo that helpfulness
            if not internal:
                endpoint['internalURL'] = None
            if not admin:
                endpoint['adminURL'] = None

    return auth_ref


class FakeIdentityv2Client:
    def __init__(self, **kwargs):
        self.roles = mock.Mock()
        self.roles.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.tenants = mock.Mock()
        self.tenants.resource_class = fakes.FakeResource(None, {})
        self.tokens = mock.Mock()
        self.tokens.resource_class = fakes.FakeResource(None, {})
        self.users = mock.Mock()
        self.users.resource_class = fakes.FakeResource(None, {})
        self.ec2 = mock.Mock()
        self.ec2.resource_class = fakes.FakeResource(None, {})
        self.endpoints = mock.Mock()
        self.endpoints.resource_class = fakes.FakeResource(None, {})
        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']

    def __getattr__(self, name):
        # Map v3 'projects' back to v2 'tenants'
        if name == "projects":
            return self.tenants
        else:
            raise AttributeError(name)


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.identity = FakeIdentityv2Client(
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


class TestIdentityv2(
    FakeClientMixin,
    utils.TestCommand,
): ...


class FakeExtension:
    """Fake one or more extension."""

    @staticmethod
    def create_one_extension(attrs=None):
        """Create a fake extension.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, namespace, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        extension_info = {
            'name': 'name-' + uuid.uuid4().hex,
            'namespace': (
                'http://docs.openstack.org/identity/api/ext/OS-KSCRUD/v1.0'
            ),
            'description': 'description-' + uuid.uuid4().hex,
            'updated': '2013-07-07T12:00:0-00:00',
            'alias': 'OS-KSCRUD',
            'links': (
                '[{"href":'
                '"https://github.com/openstack/identity-api", "type":'
                ' "text/html", "rel": "describedby"}]'
            ),
        }

        # Overwrite default attributes.
        extension_info.update(attrs)

        extension = fakes.FakeResource(
            info=copy.deepcopy(extension_info), loaded=True
        )
        return extension


class FakeCatalog:
    """Fake one or more catalog."""

    @staticmethod
    def create_catalog(attrs=None):
        """Create a fake catalog.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with id, name, type and so on.
        """
        attrs = attrs or {}

        # Set default attributes.
        catalog_info = {
            'id': 'service-id-' + uuid.uuid4().hex,
            'type': 'compute',
            'name': 'supernova',
            'endpoints': [
                {
                    'region': 'one',
                    'publicURL': 'https://public.one.example.com',
                    'internalURL': 'https://internal.one.example.com',
                    'adminURL': 'https://admin.one.example.com',
                },
                {
                    'region': 'two',
                    'publicURL': 'https://public.two.example.com',
                    'internalURL': 'https://internal.two.example.com',
                    'adminURL': 'https://admin.two.example.com',
                },
                {
                    'region': None,
                    'publicURL': 'https://public.none.example.com',
                    'internalURL': 'https://internal.none.example.com',
                    'adminURL': 'https://admin.none.example.com',
                },
            ],
        }
        # Overwrite default attributes.
        catalog_info.update(attrs)

        catalog = fakes.FakeResource(
            info=copy.deepcopy(catalog_info), loaded=True
        )

        return catalog


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
            'description': 'project_description',
            'enabled': True,
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


class FakeEndpoint:
    """Fake one or more endpoint."""

    @staticmethod
    def create_one_endpoint(attrs=None):
        """Create a fake agent.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, region, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        endpoint_info = {
            'service_name': 'service-name-' + uuid.uuid4().hex,
            'adminurl': 'http://endpoint_adminurl',
            'region': 'endpoint_region',
            'internalurl': 'http://endpoint_internalurl',
            'service_type': 'service_type',
            'id': 'endpoint-id-' + uuid.uuid4().hex,
            'publicurl': 'http://endpoint_publicurl',
            'service_id': 'service-name-' + uuid.uuid4().hex,
        }
        endpoint_info.update(attrs)

        endpoint = fakes.FakeResource(
            info=copy.deepcopy(endpoint_info), loaded=True
        )
        return endpoint

    @staticmethod
    def create_endpoints(attrs=None, count=2):
        """Create multiple fake endpoints.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of endpoints to fake
        :return:
            A list of FakeResource objects faking the endpoints
        """
        endpoints = []
        for i in range(0, count):
            endpoints.append(FakeEndpoint.create_one_endpoint(attrs))

        return endpoints


class FakeService:
    """Fake one or more service."""

    @staticmethod
    def create_one_service(attrs=None):
        """Create a fake service.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, type, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        service_info = {
            'id': 'service-id-' + uuid.uuid4().hex,
            'name': 'service-name-' + uuid.uuid4().hex,
            'description': 'service_description',
            'type': 'service_type',
        }
        service_info.update(attrs)

        service = fakes.FakeResource(
            info=copy.deepcopy(service_info), loaded=True
        )
        return service

    @staticmethod
    def create_services(attrs=None, count=2):
        """Create multiple fake services.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of services to fake
        :return:
            A list of FakeResource objects faking the services
        """
        services = []
        for i in range(0, count):
            services.append(FakeService.create_one_service(attrs))

        return services


class FakeRole:
    """Fake one or more role."""

    @staticmethod
    def create_one_role(attrs=None):
        """Create a fake role.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        role_info = {
            'id': 'role-id' + uuid.uuid4().hex,
            'name': 'role-name' + uuid.uuid4().hex,
        }
        role_info.update(attrs)

        role = fakes.FakeResource(info=copy.deepcopy(role_info), loaded=True)
        return role

    @staticmethod
    def create_roles(attrs=None, count=2):
        """Create multiple fake roles.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of roles to fake
        :return:
            A list of FakeResource objects faking the roles
        """
        roles = []
        for i in range(0, count):
            roles.append(FakeRole.create_one_role(attrs))

        return roles


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
            'tenantId': 'project-id-' + uuid.uuid4().hex,
            'email': 'admin@openstack.org',
            'enabled': True,
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
            users.append(FakeUser.create_one_user(attrs))

        return users
