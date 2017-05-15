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

from openstackclient.identity.v3 import catalog
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils


class TestCatalog(utils.TestCommand):

    fake_service = {
        'id': 'qwertyuiop',
        'type': 'compute',
        'name': 'supernova',
        'endpoints': [
            {
                'region': 'onlyone',
                'url': 'https://public.example.com',
                'interface': 'public',
            },
            {
                'region_id': 'onlyone',
                'url': 'https://admin.example.com',
                'interface': 'admin',
            },
            {
                'url': 'https://internal.example.com',
                'interface': 'internal',
            },
            {
                'region': None,
                'url': 'https://none.example.com',
                'interface': 'none',
            },
        ],
    }

    def setUp(self):
        super(TestCatalog, self).setUp()

        self.sc_mock = mock.Mock()
        self.sc_mock.service_catalog.catalog.return_value = [
            self.fake_service,
        ]

        self.auth_mock = mock.Mock()
        self.app.client_manager.session = self.auth_mock

        self.auth_mock.auth.get_auth_ref.return_value = self.sc_mock


class TestCatalogList(TestCatalog):

    def setUp(self):
        super(TestCatalogList, self).setUp()

        # Get the command object to test
        self.cmd = catalog.ListCatalog(self.app, None)

    def test_catalog_list(self):
        auth_ref = identity_fakes.fake_auth_ref(
            identity_fakes.TOKEN_WITH_PROJECT_ID,
            fake_service=self.fake_service,
        )
        self.ar_mock = mock.PropertyMock(return_value=auth_ref)
        type(self.app.client_manager).auth_ref = self.ar_mock

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Name', 'Type', 'Endpoints')
        self.assertEqual(collist, columns)
        datalist = ((
            'supernova',
            'compute',
            catalog.EndpointsColumn(self.fake_service['endpoints']),
        ), )
        self.assertListItemEqual(datalist, tuple(data))


class TestCatalogShow(TestCatalog):

    def setUp(self):
        super(TestCatalogShow, self).setUp()

        # Get the command object to test
        self.cmd = catalog.ShowCatalog(self.app, None)

    def test_catalog_show(self):
        auth_ref = identity_fakes.fake_auth_ref(
            identity_fakes.TOKEN_WITH_PROJECT_ID,
            fake_service=self.fake_service,
        )
        self.ar_mock = mock.PropertyMock(return_value=auth_ref)
        type(self.app.client_manager).auth_ref = self.ar_mock

        arglist = [
            'compute',
        ]
        verifylist = [
            ('service', 'compute'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('endpoints', 'id', 'name', 'type')
        self.assertEqual(collist, columns)
        datalist = (
            catalog.EndpointsColumn(self.fake_service['endpoints']),
            'qwertyuiop',
            'supernova',
            'compute',
        )
        self.assertItemEqual(datalist, data)


class TestFormatColumns(TestCatalog):
    def test_endpoints_column_human_readabale(self):
        col = catalog.EndpointsColumn(self.fake_service['endpoints'])
        self.assertEqual(
            'onlyone\n  public: https://public.example.com\n'
            'onlyone\n  admin: https://admin.example.com\n'
            '<none>\n  internal: https://internal.example.com\n'
            '<none>\n  none: https://none.example.com\n',
            col.human_readable())
