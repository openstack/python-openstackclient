#   Copyright 2011-2013 OpenStack, LLC.
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

"""Keyring backend for OpenStack, to store encrypted password in a file."""

from Crypto.Cipher import AES

import keyring
import os


KEYRING_FILE = os.path.join(os.path.expanduser('~'), '.openstack-keyring.cfg')


class OpenStackKeyring(keyring.backends.file.BaseKeyring):
    """OpenStack Keyring to store encrypted password."""
    filename = KEYRING_FILE

    def supported(self):
        """Applicable for all platforms, but not recommend."""
        pass

    def _init_crypter(self):
        """Initialize the crypter using the class name."""
        block_size = 32
        padding = '0'

        # init the cipher with the class name, up to block_size
        password = __name__[block_size:]
        password = password + (block_size - len(password) %
                               block_size) * padding
        return AES.new(password, AES.MODE_CFB)

    def encrypt(self, password):
        """Encrypt the given password."""
        crypter = self._init_crypter()
        return crypter.encrypt(password)

    def decrypt(self, password_encrypted):
        """Decrypt the given password."""
        crypter = self._init_crypter()
        return crypter.decrypt(password_encrypted)


def os_keyring():
    """Initialize the openstack keyring."""
    ring = 'openstackclient.common.openstackkeyring.OpenStackKeyring'
    return keyring.core.load_keyring(None, ring)
