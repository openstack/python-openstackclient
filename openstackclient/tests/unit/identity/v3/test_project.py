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

from unittest import mock

from openstack import exceptions as sdk_exc
from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import user as _user
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.identity.v3 import project
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestProjectCreate(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    columns = (
        'description',
        'domain_id',
        'enabled',
        'id',
        'is_domain',
        'name',
        'options',
        'parent_id',
        'tags',
    )

    project_kwargs_no_options = {
        'description': None,
        'domain_id': None,
        'enabled': True,
        'is_domain': False,
        'parent_id': None,
        'tags': [],
    }

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_domain.return_value = self.domain

        # Get the command object to test
        self.cmd = project.CreateProject(self.app, None)

    def test_project_create_no_options(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project, **self.project_kwargs_no_options
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            project.name,
        ]
        verifylist = [
            ('parent', None),
            ('enabled', True),
            ('name', project.name),
            ('tags', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': project.name,
            'is_enabled': True,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)

        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_description(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, description='new desc'),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--description',
            'new desc',
            project.name,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': project.name,
            'description': 'new desc',
            'is_enabled': True,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            'new desc',
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_domain(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, domain_id=self.domain.id),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--domain',
            project.domain_id,
            project.name,
        ]
        verifylist = [
            ('domain', project.domain_id),
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'domain_id': project.domain_id,
            'is_enabled': True,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            self.domain.id,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_domain_no_perms(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, domain_id=self.domain.id),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--domain',
            project.domain_id,
            project.name,
        ]
        verifylist = [
            ('domain', project.domain_id),
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.identity_sdk_client.find_domain.side_effect = (
            sdk_exc.ForbiddenException
        )
        self.identity_sdk_client.find_domain.return_value = None

        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'domain_id': project.domain_id,
            'is_enabled': True,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            self.domain.id,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_enable(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, enabled=True),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--enable',
            project.name,
        ]
        verifylist = [
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'is_enabled': True,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_disable(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, enabled=False),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--disable',
            project.name,
        ]
        verifylist = [
            ('enabled', False),
            ('name', project.name),
            ('parent', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'is_enabled': False,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            False,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_property(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, fee='fi', fo='fum'),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--property',
            'fee=fi',
            '--property',
            'fo=fum',
            project.name,
        ]
        verifylist = [
            ('name', project.name),
            ('properties', {'fee': 'fi', 'fo': 'fum'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'is_enabled': True,
            'fee': 'fi',
            'fo': 'fum',
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(
            (
                'description',
                'domain_id',
                'enabled',
                'fee',
                'fo',
                'id',
                'is_domain',
                'name',
                'options',
                'parent_id',
                'tags',
            ),
            columns,
        )
        datalist = (
            None,
            None,
            True,
            'fi',
            'fum',
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_is_domain_false_property(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, is_domain=False),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--property',
            'is_domain=false',
            project.name,
        ]
        verifylist = [
            ('parent', None),
            ('enabled', True),
            ('name', project.name),
            ('tags', []),
            ('properties', {'is_domain': 'false'}),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'is_enabled': True,
            'is_domain': False,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_is_domain_true_property(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, is_domain=True),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--property',
            'is_domain=true',
            project.name,
        ]
        verifylist = [
            ('parent', None),
            ('enabled', True),
            ('name', project.name),
            ('tags', []),
            ('properties', {'is_domain': 'true'}),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'is_enabled': True,
            'is_domain': True,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            True,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_is_domain_none_property(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, is_domain=None),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--property',
            'is_domain=none',
            project.name,
        ]
        verifylist = [
            ('parent', None),
            ('enabled', True),
            ('name', project.name),
            ('tags', []),
            ('properties', {'is_domain': 'none'}),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'is_enabled': True,
            'is_domain': None,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            None,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_parent(self):
        parent = sdk_fakes.generate_fake_resource(_project.Project)
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(
                self.project_kwargs_no_options,
                domain_id=self.domain.id,
                parent_id=parent.id,
            ),
        )
        self.identity_sdk_client.find_project.return_value = parent
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--domain',
            project.domain_id,
            '--parent',
            parent.name,
            project.name,
        ]
        verifylist = [
            ('domain', project.domain_id),
            ('parent', parent.name),
            ('enabled', True),
            ('name', project.name),
            ('tags', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': project.name,
            'domain_id': project.domain_id,
            'parent_id': parent.id,
            'is_enabled': True,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            self.domain.id,
            True,
            project.id,
            False,
            project.name,
            {},
            parent.id,
            [],
        )
        self.assertEqual(data, datalist)

    def test_project_create_invalid_parent(self):
        self.identity_sdk_client.find_project.side_effect = (
            sdk_exc.ResourceNotFound
        )
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(
                self.project_kwargs_no_options,
                domain_id=self.domain.id,
                parent_id='invalid',
            ),
        )

        arglist = [
            '--domain',
            project.domain_id,
            '--parent',
            'invalid',
            project.name,
        ]
        verifylist = [
            ('domain', project.domain_id),
            ('parent', 'invalid'),
            ('enabled', True),
            ('name', project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_project_create_with_tags(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(
                self.project_kwargs_no_options,
                domain_id=self.domain.id,
                tags=['foo'],
            ),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--domain',
            project.domain_id,
            '--tag',
            'foo',
            project.name,
        ]
        verifylist = [
            ('domain', project.domain_id),
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', ['foo']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'domain_id': project.domain_id,
            'is_enabled': True,
            'tags': ['foo'],
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            self.domain.id,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            ['foo'],
        )
        self.assertEqual(datalist, data)

    def test_project_create_with_immutable_option(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(
                self.project_kwargs_no_options, options={'immutable': True}
            ),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--immutable',
            project.name,
        ]
        verifylist = [
            ('immutable', True),
            ('description', None),
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'is_enabled': True,
            'options': {'immutable': True},
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {'immutable': True},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_with_no_immutable_option(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(
                self.project_kwargs_no_options, options={'immutable': False}
            ),
        )
        self.identity_sdk_client.create_project.return_value = project

        arglist = [
            '--no-immutable',
            project.name,
        ]
        verifylist = [
            ('immutable', False),
            ('description', None),
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': project.name,
            'is_enabled': True,
            'options': {'immutable': False},
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {'immutable': False},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_conflict_with_or_show(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project, **self.project_kwargs_no_options
        )
        self.identity_sdk_client.create_project.side_effect = (
            sdk_exc.ConflictException
        )
        self.identity_sdk_client.find_project.return_value = project

        arglist = [
            '--or-show',
            project.name,
        ]
        verifylist = [
            ('or_show', True),
            ('description', None),
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', []),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': project.name,
            'is_enabled': True,
        }
        self.identity_sdk_client.create_project.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_create_conflict_without_or_show(self):
        self.identity_sdk_client.create_project.side_effect = (
            sdk_exc.ConflictException
        )
        project = sdk_fakes.generate_fake_resource(
            _project.Project, **self.project_kwargs_no_options
        )

        arglist = [
            project.name,
        ]
        verifylist = [
            ('or_show', False),
            ('description', None),
            ('enabled', True),
            ('name', project.name),
            ('parent', None),
            ('tags', []),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            sdk_exc.ConflictException,
            self.cmd.take_action,
            parsed_args,
        )


class TestProjectDelete(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.project_with_domain = sdk_fakes.generate_fake_resource(
            _project.Project,
            name=self.project.name,
            domain_id=self.domain.id,
        )
        self.identity_sdk_client.delete_project.return_value = None

        # Get the command object to test
        self.cmd = project.DeleteProject(self.app, None)

    def test_project_delete_no_options(self):
        self.identity_sdk_client.find_project.return_value = self.project

        arglist = [
            self.project.id,
        ]
        verifylist = [
            ('projects', [self.project.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_project.assert_called_with(
            self.project.id,
        )
        self.assertIsNone(result)

    def test_project_multi_delete(self):
        self.identity_sdk_client.find_project.side_effect = [
            self.project,
            self.project_with_domain,
        ]
        arglist = [self.project.id, self.project_with_domain.id]
        verifylist = [
            ('projects', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_project.assert_has_calls(
            [
                mock.call(self.project.id),
                mock.call(self.project_with_domain.id),
            ]
        )
        self.assertIsNone(result)

    def test_project_delete_with_forbidden_domain(self):
        self.identity_sdk_client.find_domain.side_effect = [
            sdk_exc.ForbiddenException
        ]
        self.identity_sdk_client.find_project.return_value = (
            self.project_with_domain
        )

        arglist = [
            '--domain',
            self.project_with_domain.domain_id,
            self.project_with_domain.name,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('projects', [self.project_with_domain.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_project.assert_called_with(
            name_or_id=self.project_with_domain.name,
            ignore_missing=False,
            domain_id=self.domain.id,
        )
        self.identity_sdk_client.delete_project.assert_called_once_with(
            self.project_with_domain.id
        )
        self.assertIsNone(result)

    def test_delete_multi_projects_with_exception(self):
        self.identity_sdk_client.find_project.side_effect = [
            self.project,
            self.project_with_domain,
            sdk_exc.NotFoundException,
        ]

        arglist = [
            self.project.id,
            self.project_with_domain.id,
            'unexist_project',
        ]
        verifylist = [
            ('projects', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 3 projects failed to delete.', str(e))

        self.identity_sdk_client.find_project.assert_has_calls(
            [
                mock.call(name_or_id=self.project.id, ignore_missing=False),
                mock.call(
                    name_or_id=self.project_with_domain.id,
                    ignore_missing=False,
                ),
                mock.call(name_or_id='unexist_project', ignore_missing=False),
            ]
        )

        self.assertEqual(3, self.identity_sdk_client.find_project.call_count)
        self.identity_sdk_client.delete_project.assert_has_calls(
            [
                mock.call(self.project.id),
                mock.call(self.project_with_domain.id),
            ]
        )


class TestProjectList(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)
    project = sdk_fakes.generate_fake_resource(
        _project.Project, domain_id=domain.id
    )
    projects = list(
        sdk_fakes.generate_fake_resources(_project.Project, count=2)
    )

    columns = (
        'ID',
        'Name',
    )
    datalist = (
        (
            project.id,
            project.name,
        ),
    )
    datalists = (
        (
            projects[0].description,
            True,
            projects[0].id,
            projects[0].name,
        ),
        (
            projects[1].description,
            True,
            projects[1].id,
            projects[1].name,
        ),
    )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = project.ListProject(self.app, None)

    def test_project_list_no_options(self):
        self.identity_sdk_client.projects.return_value = [self.project]

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.projects.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_project_list_long(self):
        self.identity_sdk_client.projects.return_value = [self.project]

        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.projects.assert_called_with()

        collist = ('ID', 'Name', 'Domain ID', 'Description', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.project.id,
                self.project.name,
                self.project.domain_id,
                self.project.description,
                True,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_project_list_domain(self):
        self.identity_sdk_client.projects.return_value = [self.project]

        arglist = [
            '--domain',
            self.project.domain_id,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
        ]

        self.identity_sdk_client.find_domain.return_value = self.domain

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.projects.assert_called_with(
            domain_id=self.project.domain_id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_project_list_domain_no_perms(self):
        self.identity_sdk_client.projects.return_value = [self.project]

        arglist = [
            '--domain',
            self.project.domain_id,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.identity_sdk_client.find_project.side_effect = (
            sdk_exc.ResourceNotFound
        )
        self.identity_sdk_client.find_domain.return_value = self.domain

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.projects.assert_called_with(
            domain_id=self.project.domain_id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_project_list_parent(self):
        self.parent = sdk_fakes.generate_fake_resource(_project.Project)
        self.project = sdk_fakes.generate_fake_resource(
            _project.Project,
            id=self.project.id,
            name=self.project.name,
            domain_id=self.domain.id,
            parent_id=self.parent.id,
        )
        self.identity_sdk_client.projects.return_value = [self.project]

        arglist = [
            '--parent',
            self.parent.id,
        ]
        verifylist = [
            ('parent', self.parent.id),
        ]

        self.identity_sdk_client.find_project.return_value = self.parent

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.projects.assert_called_with(
            parent_id=self.parent.id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_project_list_user(self):
        self.user = sdk_fakes.generate_fake_resource(_user.User)
        self.project = sdk_fakes.generate_fake_resource(
            _project.UserProject,
            id=self.project.id,
            name=self.project.name,
            user_id=self.user.id,
        )
        self.identity_sdk_client.user_projects.return_value = [self.project]

        arglist = [
            '--user',
            self.user.id,
        ]
        verifylist = [
            ('user', self.user.id),
        ]

        self.identity_sdk_client.find_user.return_value = self.user

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.user_projects.assert_called_with(self.user.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_project_list_sort(self):
        self.identity_sdk_client.projects.return_value = self.projects

        arglist = [
            '--sort',
            'name:asc',
        ]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        (columns, data) = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.projects.assert_called_with()

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)

        if self.projects[0].name > self.projects[1].name:
            datalists = (
                (self.projects[1].id, self.projects[1].name),
                (self.projects[0].id, self.projects[0].name),
            )
        else:
            datalists = (
                (self.projects[0].id, self.projects[0].name),
                (self.projects[1].id, self.projects[1].name),
            )

        self.assertEqual(datalists, tuple(data))

    def test_project_list_my_projects(self):
        self.identity_sdk_client.user_projects.return_value = [self.project]

        auth_ref = identity_fakes.fake_auth_ref(
            identity_fakes.TOKEN_WITH_PROJECT_ID,
        )
        self.app.client_manager.auth_ref = auth_ref

        arglist = [
            '--my-projects',
        ]
        verifylist = [
            ('my_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.user_projects.assert_called_with(
            self.app.client_manager.auth_ref.user_id
        )

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.project.id,
                self.project.name,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_project_list_with_option_enabled(self):
        self.identity_sdk_client.projects.return_value = [self.project]

        arglist = ['--enabled']
        verifylist = [('is_enabled', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'is_enabled': True}
        self.identity_sdk_client.projects.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestProjectSet(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    project_kwargs_no_options = {
        'domain_id': domain.id,
        'tags': ['tag1', 'tag2', 'tag3'],
    }
    project = sdk_fakes.generate_fake_resource(
        _project.Project, **project_kwargs_no_options
    )

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.find_project.return_value = self.project

        # Get the command object to test
        self.cmd = project.SetProject(self.app, None)

    def test_project_set_no_options(self):
        arglist = [
            self.project.name,
        ]
        verifylist = [
            ('project', self.project.name),
            ('enabled', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_project_set_name(self):
        arglist = [
            '--name',
            'qwerty',
            '--domain',
            self.project.domain_id,
            self.project.name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('domain', self.project.domain_id),
            ('enabled', None),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'qwerty',
        }

        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_description(self):
        arglist = [
            '--domain',
            self.project.domain_id,
            '--description',
            'new desc',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('description', 'new desc'),
            ('enabled', None),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'new desc',
        }
        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_enable(self):
        arglist = [
            '--domain',
            self.project.domain_id,
            '--enable',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('enabled', True),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_disable(self):
        arglist = [
            '--domain',
            self.project.domain_id,
            '--disable',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('enabled', False),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_property(self):
        arglist = [
            '--domain',
            self.project.domain_id,
            '--property',
            'fee=fi',
            '--property',
            'fo=fum',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('properties', {'fee': 'fi', 'fo': 'fum'}),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'fee': 'fi',
            'fo': 'fum',
        }
        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_tags(self):
        arglist = [
            '--name',
            'qwerty',
            '--domain',
            self.project.domain_id,
            '--tag',
            'foo',
            self.project.name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('domain', self.domain.id),
            ('enabled', None),
            ('project', self.project.name),
            ('tags', ['foo']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values. new tag is added to original tags for update.
        kwargs = {
            'name': 'qwerty',
            'tags': sorted({'tag1', 'tag2', 'tag3', 'foo'}),
        }
        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_remove_tags(self):
        arglist = [
            '--remove-tag',
            'tag1',
            '--remove-tag',
            'tag2',
            self.project.name,
        ]
        verifylist = [
            ('enabled', None),
            ('project', self.project.name),
            ('remove_tags', ['tag1', 'tag2']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {'tags': list({'tag3'})}
        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_with_immutable_option(self):
        arglist = [
            '--domain',
            self.project.domain_id,
            '--immutable',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('immutable', True),
            ('enabled', None),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'options': {'immutable': True},
        }
        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_with_no_immutable_option(self):
        arglist = [
            '--domain',
            self.project.domain_id,
            '--no-immutable',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('immutable', False),
            ('enabled', None),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'options': {'immutable': False},
        }
        self.identity_sdk_client.update_project.assert_called_with(
            self.project.id, **kwargs
        )
        self.assertIsNone(result)


class TestProjectShow(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    columns = (
        'description',
        'domain_id',
        'enabled',
        'id',
        'is_domain',
        'name',
        'options',
        'parent_id',
        'tags',
    )

    project_kwargs_no_options = {
        'description': None,
        'domain_id': None,
        'enabled': True,
        'is_domain': False,
        'parent_id': None,
        'tags': [],
    }

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = project.ShowProject(self.app, None)

    def test_project_show(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project, **self.project_kwargs_no_options
        )
        self.identity_sdk_client.find_project.return_value = project

        arglist = [
            project.id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_project.assert_called_with(
            project.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_show_parents(self):
        parent = sdk_fakes.generate_fake_resource(
            _project.Project, parent_id='default'
        )
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(
                self.project_kwargs_no_options,
                parent_id=parent.id,
                parents={parent.id: {parent.parent_id: None}},
            ),
        )
        self.identity_sdk_client.find_project.return_value = project

        arglist = [
            project.id,
            '--parents',
        ]
        verifylist = [
            ('project', project.id),
            ('parents', True),
            ('children', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_project.assert_called_with(
            project.id, parents_as_ids=True, ignore_missing=False
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'options',
            'parent_id',
            'parents',
            'tags',
        )
        self.assertEqual(collist, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            parent.id,
            {parent.id: {'default': None}},
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_show_subtree(self):
        child = sdk_fakes.generate_fake_resource(
            _project.Project, subtree=None
        )
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, subtree={child.id: None}),
        )
        self.identity_sdk_client.find_project.return_value = project

        arglist = [
            project.id,
            '--children',
        ]
        verifylist = [
            ('project', project.id),
            ('parents', False),
            ('children', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_project.assert_called_with(
            project.id, subtree_as_ids=True, ignore_missing=False
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'options',
            'parent_id',
            'subtree',
            'tags',
        )
        self.assertEqual(collist, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            {child.id: None},
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_show_parents_and_children(self):
        parent = sdk_fakes.generate_fake_resource(
            _project.Project, parent_id='default'
        )
        child = sdk_fakes.generate_fake_resource(
            _project.Project, subtree=None
        )
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(
                self.project_kwargs_no_options,
                parent_id=parent.id,
                parents={parent.id: {parent.parent_id: None}},
                subtree={child.id: None},
            ),
        )
        self.identity_sdk_client.find_project.return_value = project

        arglist = [
            project.id,
            '--parents',
            '--children',
        ]
        verifylist = [
            ('project', project.id),
            ('parents', True),
            ('children', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_project.assert_called_with(
            project.id,
            parents_as_ids=True,
            subtree_as_ids=True,
            ignore_missing=False,
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'options',
            'parent_id',
            'parents',
            'subtree',
            'tags',
        )
        self.assertEqual(collist, columns)
        datalist = (
            None,
            None,
            True,
            project.id,
            False,
            project.name,
            {},
            parent.id,
            {parent.id: {'default': None}},
            {child.id: None},
            [],
        )
        self.assertEqual(datalist, data)

    def test_project_show_with_domain(self):
        project = sdk_fakes.generate_fake_resource(
            _project.Project,
            **dict(self.project_kwargs_no_options, domain_id=self.domain.id),
        )
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.find_project.return_value = project

        arglist = [
            "--domain",
            self.domain.id,
            project.name,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('project', project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_project.assert_called_with(
            project.id, domain_id=self.domain.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            None,
            self.domain.id,
            True,
            project.id,
            False,
            project.name,
            {},
            None,
            [],
        )
        self.assertEqual(datalist, data)
