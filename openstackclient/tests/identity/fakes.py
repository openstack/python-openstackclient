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


class FakeIdentityv2Client(object):
    def __init__(self, **kwargs):
        self.tenants = mock.Mock()
        self.tenants.resource_class = fakes.FakeResource(None, {})
        self.users = mock.Mock()
        self.users.resource_class = fakes.FakeResource(None, {})
        self.ec2 = mock.Mock()
        self.ec2.resource_class = fakes.FakeResource(None, {})
        self.auth_tenant_id = 'fake-tenant'
        self.auth_user_id = 'fake-user'


class FakeIdentityv3Client(object):
    def __init__(self, **kwargs):
        self.domains = mock.Mock()
        self.domains.resource_class = fakes.FakeResource(None, {})
        self.projects = mock.Mock()
        self.projects.resource_class = fakes.FakeResource(None, {})
        self.users = mock.Mock()
        self.users.resource_class = fakes.FakeResource(None, {})
