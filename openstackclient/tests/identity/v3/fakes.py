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


domain_id = 'd1'
domain_name = 'oftheking'

DOMAIN = {
    'id': domain_id,
    'name': domain_name,
}

group_id = 'gr-010'
group_name = 'spencer davis'

GROUP = {
    'id': group_id,
    'name': group_name,
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
}

PROJECT_2 = {
    'id': project_id + '-2222',
    'name': project_name + ' reprise',
    'description': project_description + 'plus four more',
    'enabled': True,
    'domain_id': domain_id,
}

role_id = 'r1'
role_name = 'roller'

ROLE = {
    'id': role_id,
    'name': role_name,
}

service_id = 's-123'
service_name = 'Texaco'
service_type = 'gas'

SERVICE = {
    'id': service_id,
    'name': service_name,
    'type': service_type,
    'enabled': True,
}

user_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
user_name = 'paul'
user_description = 'Sir Paul'
user_email = 'paul@applecorps.com'

USER = {
    'id': user_id,
    'name': user_name,
    'project_id': project_id,
    'email': user_email,
    'enabled': True,
    'domain_id': domain_id,
}

token_expires = '2014-01-01T00:00:00Z'
token_id = 'tttttttt-tttt-tttt-tttt-tttttttttttt'

TOKEN_WITH_TENANT_ID = {
    'expires': token_expires,
    'id': token_id,
    'tenant_id': project_id,
    'user_id': user_id,
}

TOKEN_WITH_DOMAIN_ID = {
    'expires': token_expires,
    'id': token_id,
    'domain_id': domain_id,
    'user_id': user_id,
}


class FakeIdentityv3Client(object):
    def __init__(self, **kwargs):
        self.domains = mock.Mock()
        self.domains.resource_class = fakes.FakeResource(None, {})
        self.groups = mock.Mock()
        self.groups.resource_class = fakes.FakeResource(None, {})
        self.projects = mock.Mock()
        self.projects.resource_class = fakes.FakeResource(None, {})
        self.roles = mock.Mock()
        self.roles.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.service_catalog = mock.Mock()
        self.users = mock.Mock()
        self.users.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestIdentityv3(utils.TestCommand):
    def setUp(self):
        super(TestIdentityv3, self).setUp()

        self.app.client_manager.identity = FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
