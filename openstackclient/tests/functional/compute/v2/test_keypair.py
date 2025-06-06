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

import tempfile

from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions

from openstackclient.tests.functional import base


class KeypairBase(base.TestCase):
    """Methods for functional tests."""

    def keypair_create(self, name=data_utils.rand_uuid(), user=None):
        """Create keypair and add cleanup."""
        cmd = 'keypair create ' + name
        if user is not None:
            cmd += ' --user ' + user
        raw_output = self.openstack(cmd)
        self.addCleanup(
            self.keypair_delete, name, ignore_exceptions=True, user=user
        )
        if not raw_output:
            self.fail('Keypair has not been created!')
        return name

    def keypair_list(self, params=''):
        """Return dictionary with list of keypairs."""
        raw_output = self.openstack('keypair list')
        keypairs = self.parse_show_as_object(raw_output)
        return keypairs

    def keypair_delete(self, name, ignore_exceptions=False, user=None):
        """Try to delete keypair by name."""
        try:
            cmd = 'keypair delete ' + name
            if user is not None:
                cmd += ' --user ' + user
            self.openstack(cmd)
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise


class KeypairTests(KeypairBase):
    """Functional tests for compute keypairs."""

    PUBLIC_KEY = (
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDWNGczJxNaFUrJJVhta4dWsZY6bU'
        '5HUMPbyfSMu713ca3mYtG848W4dfDCB98KmSQx2Bl0D6Q2nrOszOXEQWAXNdfMadnW'
        'c4mNwhZcPBVohIFoC1KZJC8kcBTvFZcoz3mdIijxJtywZNpGNh34VRJlZeHyYjg8/D'
        'esHzdoBVd5c/4R36emQSIV9ukY6PHeZ3scAH4B3K9PxItJBwiFtouSRphQG0bJgOv/'
        'gjAjMElAvg5oku98cb4QiHZ8T8WY68id804raHR6pJxpVVJN4TYJmlUs+NOVM+pPKb'
        'KJttqrIBTkawGK9pLHNfn7z6v1syvUo/4enc1l0Q/Qn2kWiz67 fake@openstack'
    )

    def setUp(self):
        """Create keypair with randomized name for tests."""
        super().setUp()
        self.KPName = data_utils.rand_name('TestKeyPair')
        self.keypair = self.keypair_create(self.KPName)

    def test_keypair_create_duplicate(self):
        """Try to create duplicate name keypair.

        Test steps:
        1) Create keypair in setUp
        2) Try to create duplicate keypair with the same name
        """
        self.assertRaises(
            exceptions.CommandFailed,
            self.openstack,
            'keypair create ' + self.KPName,
        )

    def test_keypair_create_noname(self):
        """Try to create keypair without name.

        Test steps:
        1) Try to create keypair without a name
        """
        self.assertRaises(
            exceptions.CommandFailed, self.openstack, 'keypair create'
        )

    def test_keypair_create_public_key(self):
        """Test for create keypair with --public-key option.

        Test steps:
        1) Create keypair with given public key
        2) Delete keypair
        """
        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write(self.PUBLIC_KEY)
            f.flush()

            raw_output = self.openstack(
                f'keypair create --public-key {f.name} tmpkey',
            )
            self.addCleanup(
                self.openstack,
                'keypair delete tmpkey',
            )
            self.assertIn('tmpkey', raw_output)

    def test_keypair_create_private_key(self):
        """Test for create keypair with --private-key option.

        Test steps:
        1) Create keypair with private key file
        2) Delete keypair
        """
        with tempfile.NamedTemporaryFile(mode='w+') as f:
            cmd_output = self.openstack(
                f'keypair create --private-key {f.name} tmpkey',
                parse_output=True,
            )
            self.addCleanup(self.openstack, 'keypair delete tmpkey')
            self.assertEqual('tmpkey', cmd_output.get('name'))
            self.assertIsNotNone(cmd_output.get('user_id'))
            self.assertIsNotNone(cmd_output.get('fingerprint'))
            pk_content = f.read()
            self.assertInOutput(
                '-----BEGIN OPENSSH PRIVATE KEY-----',
                pk_content,
            )
            self.assertRegex(pk_content, "[0-9A-Za-z+/]+[=]{0,3}\n")
            self.assertInOutput(
                '-----END OPENSSH PRIVATE KEY-----',
                pk_content,
            )

    def test_keypair_create(self):
        """Test keypair create command.

        Test steps:
        1) Create keypair in setUp
        2) Check Ed25519 private key in output
        3) Check for new keypair in keypairs list
        """
        NewName = data_utils.rand_name('TestKeyPairCreated')
        raw_output = self.openstack('keypair create ' + NewName)
        self.addCleanup(self.openstack, 'keypair delete ' + NewName)
        self.assertInOutput('-----BEGIN OPENSSH PRIVATE KEY-----', raw_output)
        self.assertRegex(raw_output, "[0-9A-Za-z+/]+[=]{0,3}\n")
        self.assertInOutput('-----END OPENSSH PRIVATE KEY-----', raw_output)
        self.assertIn(NewName, self.keypair_list())

    def test_keypair_delete_not_existing(self):
        """Try to delete keypair with not existing name.

        Test steps:
        1) Create keypair in setUp
        2) Try to delete not existing keypair
        """
        self.assertRaises(
            exceptions.CommandFailed,
            self.openstack,
            'keypair delete not_existing',
        )

    def test_keypair_delete(self):
        """Test keypair delete command.

        Test steps:
        1) Create keypair in setUp
        2) Delete keypair
        3) Check that keypair not in keypairs list
        """
        self.openstack('keypair delete ' + self.KPName)
        self.assertNotIn(self.KPName, self.keypair_list())

    def test_keypair_list(self):
        """Test keypair list command.

        Test steps:
        1) Create keypair in setUp
        2) List keypairs
        3) Check output table structure
        4) Check keypair name in output
        """
        HEADERS = ['Name', 'Fingerprint']
        raw_output = self.openstack('keypair list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, HEADERS)
        self.assertIn(self.KPName, raw_output)

    def test_keypair_show(self):
        """Test keypair show command.

        Test steps:
        1) Create keypair in setUp
        2) Show keypair
        3) Check output table structure
        4) Check keypair name in output
        """
        HEADERS = ['Field', 'Value']
        raw_output = self.openstack('keypair show ' + self.KPName)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, HEADERS)
        self.assertInOutput(self.KPName, raw_output)

    def test_keypair_list_by_project(self):
        """Test keypair list by project.

        Test steps:
        1) Create keypair for admin project in setUp
        2) Create a new project
        3) Create a new user
        4) Associate the new user with the new project
        5) Create keypair for the new user
        6) List keypairs by the new project
        7) Check that only the keypair from step 5 is returned
        """
        project_name = data_utils.rand_name('TestProject')
        self.openstack(f'project create {project_name}')
        self.addCleanup(self.openstack, f'project delete {project_name}')
        user_name = data_utils.rand_name('TestUser')
        self.openstack(f'user create {user_name}')
        self.addCleanup(self.openstack, f'user delete {user_name}')
        self.openstack(
            f'role add --user {user_name} --project {project_name} member'
        )
        keypair_name = self.keypair_create(user=user_name)
        raw_output = self.openstack(f'keypair list --project {project_name}')
        items = self.parse_listing(raw_output)
        self.assertEqual(1, len(items))
        self.assertEqual(keypair_name, items[0]['Name'])
