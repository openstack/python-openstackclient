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
import ddt
from manilaclient import api_versions
from openstackclient.share.v2 import security_services
from osc_lib import exceptions
from osc_lib import utils as oscutils

from openstackclient.tests.unit.share.v2 import fakes as share_fakes
from openstackclient.tests.unit import utils as test_utils


class TestShareSecurityService(share_fakes.TestShare):
    def setUp(self):
        super().setUp()

        self.security_services_mock = self.share_client.security_services
        self.security_services_mock.reset_mock()

        self.share_networks_mock = self.share_client.share_networks
        self.share_networks_mock.reset_mock()

        self.set_share_api_version(api_versions.MAX_VERSION)


@ddt.ddt
class TestShareSecurityServiceCreate(TestShareSecurityService):
    def setUp(self):
        super().setUp()

        self.security_service = (
            share_fakes.FakeShareSecurityService.create_fake_security_service()
        )
        self.security_services_mock.create.return_value = self.security_service
        self.cmd = security_services.CreateShareSecurityService(self.app, None)

        self.data = self.security_service._info.values()
        self.columns = self.security_service._info.keys()

    def test_share_security_service_create_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_security_service_create(self):
        arglist = [
            self.security_service.type,
            '--dns-ip',
            self.security_service.dns_ip,
            '--ou',
            self.security_service.ou,
            '--server',
            self.security_service.server,
            '--domain',
            self.security_service.domain,
            '--user',
            self.security_service.user,
            '--password',
            self.security_service.password,
            '--name',
            self.security_service.name,
            '--description',
            self.security_service.description,
            '--default-ad-site',
            self.security_service.default_ad_site,
        ]
        verifylist = [
            ('type', self.security_service.type),
            ('dns_ip', self.security_service.dns_ip),
            ('ou', self.security_service.ou),
            ('server', self.security_service.server),
            ('domain', self.security_service.domain),
            ('user', self.security_service.user),
            ('password', self.security_service.password),
            ('name', self.security_service.name),
            ('description', self.security_service.description),
            ('default_ad_site', self.security_service.default_ad_site),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.security_services_mock.create.assert_called_with(
            self.security_service.type,
            dns_ip=self.security_service.dns_ip,
            server=self.security_service.server,
            domain=self.security_service.domain,
            user=self.security_service.user,
            password=self.security_service.password,
            name=self.security_service.name,
            description=self.security_service.description,
            ou=self.security_service.ou,
            default_ad_site=self.security_service.default_ad_site,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    @ddt.data('2.43', '2.75')
    def test_share_security_service_create_api_version_exception(
        self, version
    ):
        self.set_share_api_version(version)

        arglist = [
            self.security_service.type,
        ]
        verifylist = [
            ('type', self.security_service.type),
        ]

        if api_versions.APIVersion(version) <= api_versions.APIVersion("2.43"):
            arglist.extend(['--ou', self.security_service.ou])
            verifylist.append(('ou', self.security_service.ou))

        if api_versions.APIVersion(version) <= api_versions.APIVersion("2.75"):
            arglist.extend(
                ['--default-ad-site', self.security_service.default_ad_site]
            )
            verifylist.append(
                ('default_ad_site', self.security_service.default_ad_site)
            )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareSecurityServiceDelete(TestShareSecurityService):
    def setUp(self):
        super().setUp()

        self.security_service = (
            share_fakes.FakeShareSecurityService.create_fake_security_service()
        )
        self.security_services_mock.get.return_value = self.security_service

        self.security_services = share_fakes.FakeShareSecurityService.create_fake_security_services()

        self.cmd = security_services.DeleteShareSecurityService(self.app, None)

    def test_share_security_service_delete_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_security_service_delete(self):
        arglist = [
            self.security_services[0].id,
            self.security_services[1].id,
        ]
        verifylist = [
            (
                'security_service',
                [self.security_services[0].id, self.security_services[1].id],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertEqual(
            self.security_services_mock.delete.call_count,
            len(self.security_services),
        )
        self.assertIsNone(result)

    def test_share_security_service_delete_exception(self):
        arglist = [
            self.security_services[0].id,
        ]
        verifylist = [
            ('security_service', [self.security_services[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.security_services_mock.delete.side_effect = (
            exceptions.CommandError()
        )
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareSecurityServiceShow(TestShareSecurityService):
    def setUp(self):
        super().setUp()

        self.security_service = (
            share_fakes.FakeShareSecurityService.create_fake_security_service()
        )
        self.security_services_mock.get.return_value = self.security_service

        self.cmd = security_services.ShowShareSecurityService(self.app, None)

        self.data = self.security_service._info.values()
        self.columns = self.security_service._info.keys()

    def test_share_security_service_show_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_security_service_show(self):
        arglist = [self.security_service.id]
        verifylist = [('security_service', self.security_service.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.security_services_mock.get.assert_called_with(
            self.security_service.id
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


@ddt.ddt
class TestShareSecurityServiceSet(TestShareSecurityService):
    def setUp(self):
        super().setUp()

        self.security_service = (
            share_fakes.FakeShareSecurityService.create_fake_security_service(
                methods={'update': None}
            )
        )
        self.security_services_mock.get.return_value = self.security_service
        self.cmd = security_services.SetShareSecurityService(self.app, None)

    def test_share_security_service_set_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_security_service_set(self):
        arglist = [
            self.security_service.id,
            '--dns-ip',
            self.security_service.dns_ip,
            '--ou',
            self.security_service.ou,
            '--server',
            self.security_service.server,
            '--domain',
            self.security_service.domain,
            '--user',
            self.security_service.user,
            '--password',
            self.security_service.password,
            '--name',
            self.security_service.name,
            '--description',
            self.security_service.description,
            '--default-ad-site',
            self.security_service.default_ad_site,
        ]
        verifylist = [
            ('security_service', self.security_service.id),
            ('dns_ip', self.security_service.dns_ip),
            ('ou', self.security_service.ou),
            ('server', self.security_service.server),
            ('domain', self.security_service.domain),
            ('user', self.security_service.user),
            ('password', self.security_service.password),
            ('name', self.security_service.name),
            ('description', self.security_service.description),
            ('default_ad_site', self.security_service.default_ad_site),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.security_service.update.assert_called_with(
            dns_ip=self.security_service.dns_ip,
            server=self.security_service.server,
            domain=self.security_service.domain,
            user=self.security_service.user,
            password=self.security_service.password,
            name=self.security_service.name,
            description=self.security_service.description,
            ou=self.security_service.ou,
            default_ad_site=self.security_service.default_ad_site,
        )
        self.assertIsNone(result)

    def test_share_security_service_set_exception(self):
        arglist = [
            self.security_service.id,
            '--name',
            self.security_service.name,
        ]
        verifylist = [
            ('security_service', self.security_service.id),
            ('name', self.security_service.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.security_service.update.side_effect = exceptions.CommandError()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    @ddt.data('2.43', '2.75')
    def test_share_security_service_set_api_version_exception(self, version):
        self.set_share_api_version(version)

        arglist = [
            self.security_service.id,
        ]
        verifylist = [
            ('security_service', self.security_service.id),
        ]

        if api_versions.APIVersion(version) <= api_versions.APIVersion("2.43"):
            arglist.extend(['--ou', self.security_service.ou])
            verifylist.append(('ou', self.security_service.ou))

        if api_versions.APIVersion(version) <= api_versions.APIVersion("2.75"):
            arglist.extend(
                ['--default-ad-site', self.security_service.default_ad_site]
            )
            verifylist.append(
                ('default_ad_site', self.security_service.default_ad_site)
            )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


@ddt.ddt
class TestShareSecurityServiceUnset(TestShareSecurityService):
    def setUp(self):
        super().setUp()

        self.security_service = (
            share_fakes.FakeShareSecurityService.create_fake_security_service(
                methods={'update': None}
            )
        )
        self.security_services_mock.get.return_value = self.security_service
        self.cmd = security_services.UnsetShareSecurityService(self.app, None)

    def test_share_security_service_unset_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_security_service_unset(self):
        arglist = [
            self.security_service.id,
            '--dns-ip',
            '--ou',
            '--server',
            '--domain',
            '--user',
            '--password',
            '--name',
            '--description',
            '--default-ad-site',
        ]
        verifylist = [
            ('security_service', self.security_service.id),
            ('dns_ip', True),
            ('ou', True),
            ('server', True),
            ('domain', True),
            ('user', True),
            ('password', True),
            ('name', True),
            ('description', True),
            ('default_ad_site', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.security_service.update.assert_called_with(
            dns_ip='',
            server='',
            domain='',
            user='',
            password='',
            name='',
            description='',
            ou='',
            default_ad_site='',
        )
        self.assertIsNone(result)

    def test_share_security_service_unset_exception(self):
        arglist = [
            self.security_service.id,
            '--name',
        ]
        verifylist = [
            ('security_service', self.security_service.id),
            ('name', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.security_service.update.side_effect = exceptions.CommandError()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    @ddt.data('2.43', '2.75')
    def test_share_security_service_unset_api_version_exception(self, version):
        self.set_share_api_version(version)

        arglist = [
            self.security_service.id,
        ]
        verifylist = [
            ('security_service', self.security_service.id),
        ]

        if api_versions.APIVersion(version) <= api_versions.APIVersion("2.43"):
            arglist.extend(['--ou'])
            verifylist.append(('ou', True))

        if api_versions.APIVersion(version) <= api_versions.APIVersion("2.75"):
            (arglist.extend(['--default-ad-site']),)
            verifylist.append(('default_ad_site', True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareSecurityServiceList(TestShareSecurityService):
    columns = [
        'ID',
        'Name',
        'Status',
        'Type',
    ]

    def setUp(self):
        super().setUp()

        self.share_network = (
            share_fakes.FakeShareNetwork.create_one_share_network()
        )
        self.share_networks_mock.get.return_value = self.share_network
        self.services_list = share_fakes.FakeShareSecurityService.create_fake_security_services()
        self.security_services_mock.list.return_value = self.services_list
        self.values = (
            oscutils.get_dict_properties(i._info, self.columns)
            for i in self.services_list
        )

        self.cmd = security_services.ListShareSecurityService(self.app, None)

    def test_share_security_service_list_no_args(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.security_services_mock.list.assert_called_with(
            search_opts={
                'all_tenants': False,
                'status': None,
                'name': None,
                'type': None,
                'user': None,
                'dns_ip': None,
                'server': None,
                'domain': None,
                'offset': None,
                'limit': None,
            },
            detailed=False,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_security_service_list(self):
        arglist = [
            '--share-network',
            self.share_network.id,
            '--status',
            self.services_list[0].status,
            '--name',
            self.services_list[0].name,
            '--type',
            self.services_list[0].type,
            '--user',
            self.services_list[0].user,
            '--dns-ip',
            self.services_list[0].dns_ip,
            '--ou',
            self.services_list[0].ou,
            '--server',
            self.services_list[0].server,
            '--domain',
            self.services_list[0].domain,
            '--default-ad-site',
            self.services_list[0].default_ad_site,
            '--limit',
            '1',
        ]
        verifylist = [
            ('share_network', self.share_network.id),
            ('status', self.services_list[0].status),
            ('name', self.services_list[0].name),
            ('type', self.services_list[0].type),
            ('user', self.services_list[0].user),
            ('dns_ip', self.services_list[0].dns_ip),
            ('ou', self.services_list[0].ou),
            ('server', self.services_list[0].server),
            ('domain', self.services_list[0].domain),
            ('default_ad_site', self.services_list[0].default_ad_site),
            ('limit', 1),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.security_services_mock.list.assert_called_with(
            search_opts={
                'all_tenants': False,
                'status': self.services_list[0].status,
                'name': self.services_list[0].name,
                'type': self.services_list[0].type,
                'user': self.services_list[0].user,
                'dns_ip': self.services_list[0].dns_ip,
                'server': self.services_list[0].server,
                'domain': self.services_list[0].domain,
                'default_ad_site': self.services_list[0].default_ad_site,
                'offset': None,
                'limit': 1,
                'ou': self.services_list[0].ou,
                'share_network_id': self.share_network.id,
            },
            detailed=False,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_security_service_list_ou_api_version_exception(self):
        self.set_share_api_version('2.43')

        arglist = [
            '--ou',
            self.services_list[0].ou,
        ]
        verifylist = [
            ('ou', self.services_list[0].ou),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_share_security_service_list_ad_site_api_version_exception(self):
        self.set_share_api_version('2.75')

        arglist = [
            '--default-ad-site',
            self.services_list[0].default_ad_site,
        ]
        verifylist = [
            ('default_ad_site', self.services_list[0].default_ad_site),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_share_security_service_list_detail_all_projects(self):
        arglist = ['--all-projects', '--detail']
        verifylist = [
            ('all_projects', True),
            ('detail', True),
        ]
        columns_detail = self.columns.copy()
        columns_detail.append('Project ID')
        columns_detail.append('Share Networks')

        values_detail = (
            oscutils.get_dict_properties(i._info, columns_detail)
            for i in self.services_list
        )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.security_services_mock.list.assert_called_with(
            search_opts={
                'all_tenants': True,
                'status': None,
                'name': None,
                'type': None,
                'user': None,
                'dns_ip': None,
                'server': None,
                'domain': None,
                'offset': None,
                'limit': None,
            },
            detailed=True,
        )
        self.assertEqual(columns_detail, columns)
        self.assertEqual(list(values_detail), list(data))
