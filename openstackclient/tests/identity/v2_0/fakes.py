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


class FakeIdentityv2Client(object):
    def __init__(self, **kwargs):
        self.roles = mock.Mock()
        self.roles.resource_class = fakes.FakeResource(None, {})
        self.service_catalog = mock.Mock()
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.tenants = mock.Mock()
        self.tenants.resource_class = fakes.FakeResource(None, {})
        self.users = mock.Mock()
        self.users.resource_class = fakes.FakeResource(None, {})
        self.ec2 = mock.Mock()
        self.ec2.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestIdentityv2(utils.TestCommand):
    def setUp(self):
        super(TestIdentityv2, self).setUp()

        self.app.client_manager.identity = FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
