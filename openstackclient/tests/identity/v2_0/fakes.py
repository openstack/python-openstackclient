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

token_expires = '2014-01-01T00:00:00Z'
token_id = 'tttttttt-tttt-tttt-tttt-tttttttttttt'

TOKEN = {
    'expires': token_expires,
    'id': token_id,
    'tenant_id': project_id,
    'user_id': user_id,
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

extension_name = 'OpenStack Keystone User CRUD'
extension_namespace = 'http://docs.openstack.org/identity/'\
    'api/ext/OS-KSCRUD/v1.0'
extension_description = 'OpenStack extensions to Keystone v2.0 API'\
    ' enabling User Operations.'
extension_updated = '2013-07-07T12:00:0-00:00'
extension_alias = 'OS-KSCRUD'
extension_links = '[{"href":'\
    '"https://github.com/openstack/identity-api", "type":'\
    ' "text/html", "rel": "describedby"}]'

EXTENSION = {
    'name': extension_name,
    'namespace': extension_namespace,
    'description': extension_description,
    'updated': extension_updated,
    'alias': extension_alias,
    'links': extension_links,
}


class FakeIdentityv2Client(object):
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


class TestIdentityv2(utils.TestCommand):
    def setUp(self):
        super(TestIdentityv2, self).setUp()

        self.app.client_manager.identity = FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
