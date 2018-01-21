#    Copyright 2018 SUSE Linux GmbH
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional.identity.v3 import common


class ApplicationCredentialTests(common.IdentityTests):

    APPLICATION_CREDENTIAL_FIELDS = ['id', 'name', 'project_id',
                                     'description', 'roles', 'expires_at',
                                     'unrestricted']
    APPLICATION_CREDENTIAL_LIST_HEADERS = ['ID', 'Name', 'Project ID',
                                           'Description', 'Expires At']

    def test_application_credential_create(self):
        name = data_utils.rand_name('name')
        raw_output = self.openstack('application credential create %(name)s'
                                    % {'name': name})
        self.addCleanup(
            self.openstack,
            'application credential delete %(name)s' % {'name': name})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.APPLICATION_CREDENTIAL_FIELDS)

    def _create_role_assignments(self):
        try:
            user = self.openstack('configuration show -f value'
                                  ' -c auth.username')
        except Exception:
            user = self.openstack('configuration show -f value'
                                  ' -c auth.user_id')
        try:
            user_domain = self.openstack('configuration show -f value'
                                         ' -c auth.user_domain_name')
        except Exception:
            user_domain = self.openstack('configuration show -f value'
                                         ' -c auth.user_domain_id')
        try:
            project = self.openstack('configuration show -f value'
                                     ' -c auth.project_name')
        except Exception:
            project = self.openstack('configuration show -f value'
                                     ' -c auth.project_id')
        try:
            project_domain = self.openstack('configuration show -f value'
                                            ' -c auth.project_domain_name')
        except Exception:
            project_domain = self.openstack('configuration show -f value'
                                            ' -c auth.project_domain_id')
        role1 = self._create_dummy_role()
        role2 = self._create_dummy_role()
        for role in role1, role2:
            self.openstack('role add'
                           ' --user %(user)s'
                           ' --user-domain %(user_domain)s'
                           ' --project %(project)s'
                           ' --project-domain %(project_domain)s'
                           ' %(role)s'
                           % {'user': user,
                              'user_domain': user_domain,
                              'project': project,
                              'project_domain': project_domain,
                              'role': role})
            self.addCleanup(self.openstack,
                            'role remove'
                            ' --user %(user)s'
                            ' --user-domain %(user_domain)s'
                            ' --project %(project)s'
                            ' --project-domain %(project_domain)s'
                            ' %(role)s'
                            % {'user': user,
                               'user_domain': user_domain,
                               'project': project,
                               'project_domain': project_domain,
                               'role': role})
        return role1, role2

    def test_application_credential_create_with_options(self):
        name = data_utils.rand_name('name')
        secret = data_utils.rand_name('secret')
        description = data_utils.rand_name('description')
        tomorrow = (datetime.datetime.utcnow() +
                    datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S%z')
        role1, role2 = self._create_role_assignments()
        raw_output = self.openstack('application credential create %(name)s'
                                    ' --secret %(secret)s'
                                    ' --description %(description)s'
                                    ' --expiration %(tomorrow)s'
                                    ' --role %(role1)s'
                                    ' --role %(role2)s'
                                    ' --unrestricted'
                                    % {'name': name,
                                       'secret': secret,
                                       'description': description,
                                       'tomorrow': tomorrow,
                                       'role1': role1,
                                       'role2': role2})
        self.addCleanup(
            self.openstack,
            'application credential delete %(name)s' % {'name': name})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.APPLICATION_CREDENTIAL_FIELDS)

    def test_application_credential_delete(self):
        name = data_utils.rand_name('name')
        self.openstack('application credential create %(name)s'
                       % {'name': name})
        raw_output = self.openstack('application credential delete '
                                    '%(name)s' % {'name': name})
        self.assertEqual(0, len(raw_output))

    def test_application_credential_list(self):
        raw_output = self.openstack('application credential list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(
            items, self.APPLICATION_CREDENTIAL_LIST_HEADERS)

    def test_application_credential_show(self):
        name = data_utils.rand_name('name')
        raw_output = self.openstack('application credential create %(name)s'
                                    % {'name': name})
        self.addCleanup(
            self.openstack,
            'application credential delete %(name)s' % {'name': name})
        raw_output = self.openstack('application credential show '
                                    '%(name)s' % {'name': name})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.APPLICATION_CREDENTIAL_FIELDS)
