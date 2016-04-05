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
import uuid

from functional.common import test


PUBLIC_KEY = (
    'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDWNGczJxNaFUrJJVhta4dWsZY6bU'
    '5HUMPbyfSMu713ca3mYtG848W4dfDCB98KmSQx2Bl0D6Q2nrOszOXEQWAXNdfMadnW'
    'c4mNwhZcPBVohIFoC1KZJC8kcBTvFZcoz3mdIijxJtywZNpGNh34VRJlZeHyYjg8/D'
    'esHzdoBVd5c/4R36emQSIV9ukY6PHeZ3scAH4B3K9PxItJBwiFtouSRphQG0bJgOv/'
    'gjAjMElAvg5oku98cb4QiHZ8T8WY68id804raHR6pJxpVVJN4TYJmlUs+NOVM+pPKb'
    'KJttqrIBTkawGK9pLHNfn7z6v1syvUo/4enc1l0Q/Qn2kWiz67 fake@openstack'
)


class KeypairTests(test.TestCase):
    """Functional tests for compute keypairs. """
    NAME = uuid.uuid4().hex
    HEADERS = ['Name']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        private_key = cls.openstack('keypair create ' + cls.NAME)
        cls.assertInOutput('-----BEGIN RSA PRIVATE KEY-----', private_key)
        cls.assertInOutput('-----END RSA PRIVATE KEY-----', private_key)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('keypair delete ' + cls.NAME)
        cls.assertOutput('', raw_output)

    def test_keypair_create(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(PUBLIC_KEY)
            f.flush()

            raw_output = self.openstack(
                'keypair create --public-key %s tmpkey' % f.name,
            )
            self.addCleanup(
                self.openstack,
                'keypair delete tmpkey',
            )
            self.assertIn('tmpkey', raw_output)

    def test_keypair_list(self):
        opts = self.get_list_opts(self.HEADERS)
        raw_output = self.openstack('keypair list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_keypair_show(self):
        opts = self.get_show_opts(self.FIELDS)
        raw_output = self.openstack('keypair show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)
