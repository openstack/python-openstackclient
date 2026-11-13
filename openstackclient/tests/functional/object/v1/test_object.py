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

import hashlib
import os
import shlex
import uuid

import fixtures
from tempest.lib import exceptions

from openstackclient.tests.functional.object.v1 import common


class ObjectTests(common.ObjectStoreTests):
    """Functional tests for Object Store object commands."""

    def test_object(self):
        content = b'test content\n'
        etag = hashlib.md5(content, usedforsecurity=False).hexdigest()
        directory = self.useFixture(fixtures.TempDir()).path
        container = uuid.uuid4().hex
        # Registered after TempDir so remote cleanup runs before local cleanup.
        self.addCleanup(
            self.openstack,
            f'container delete --recursive {container}',
            fail_ok=True,
        )
        self.openstack(f'container create {container}')

        # Absolute names keep default downloads inside our temporary directory.
        downloads = os.path.join(directory, 'downloads')
        os.mkdir(downloads)
        names = [
            os.path.join(downloads, name)
            for name in ('prefix-a', 'prefix-b', 'prefix-c')
        ]
        for name in names:
            with open(name, 'wb') as f:
                f.write(content)
        arguments = ' '.join(shlex.quote(name) for name in names)
        data = self.openstack(
            f'object create {container} {arguments}', parse_output=True
        )
        self.assertEqual(names, [item['object'] for item in data])
        for item in data:
            self.assertEqual(container, item['container'])
            self.assertEqual(etag, item['etag'].strip('"'))

        # Reuse the first file to exercise uploading with a different name.
        name = 'object with spaces'
        quoted = shlex.quote(name)
        data = self.openstack(
            f'object create {container} {shlex.quote(names[0])} --name {quoted}',
            parse_output=True,
        )
        self.assertEqual(name, data[0]['object'])
        self.assertEqual(container, data[0]['container'])
        self.assertEqual(etag, data[0]['etag'].strip('"'))
        command = f'object show {container} {quoted}'
        data = self.openstack(command, parse_output=True)
        self.assertEqual(name, data['object'])
        self.assertEqual(container, data['container'])
        self.assertTrue(data['account'])
        self.assertEqual(len(content), int(data['content-length']))
        self.assertTrue(data['content-type'])
        self.assertTrue(data['last-modified'])
        self.assertEqual(etag, data['etag'].strip('"'))

        # List the original objects, filtering out the renamed upload.
        prefix = shlex.quote(os.path.join(downloads, 'prefix-'))
        listing = f'object list {container} --prefix {prefix}'
        data = self.openstack(listing + ' --long', parse_output=True)
        self.assertEqual(names, [item['Name'] for item in data])
        for item in data:
            self.assertEqual(len(content), int(item['Bytes']))
            self.assertEqual(etag, item['Hash'])
            self.assertTrue(item['Content Type'])
            self.assertTrue(item['Last Modified'])
        for options, expected in (
            ('--limit 1', names[:1]),
            (f'--marker {shlex.quote(names[0])}', names[1:]),
            (f'--end-marker {shlex.quote(names[2])}', names[:2]),
            ('--all --limit 1', names),
        ):
            data = self.openstack(f'{listing} {options}', parse_output=True)
            self.assertEqual(expected, [item['Name'] for item in data])

        data = self.openstack(f'{listing} --delimiter /', parse_output=True)
        self.assertEqual(names, [item['Name'] for item in data])
        # Swift rolls up the downloads directory into one subdir entry.
        data = self.openstack(
            f'object list {container} --delimiter / '
            f'--prefix {shlex.quote(directory + "/")}',
            parse_output=True,
        )
        self.assertEqual(1, len(data))

        self.assertEqual(
            '',
            self.openstack(
                f'object set {container} {quoted} '
                '--property first=one --property second=two'
            ),
        )
        data = self.openstack(command, parse_output=True)
        self.assertEqual(
            {'first': 'one', 'second': 'two'}, self.get_properties(data)
        )
        # Swift object POST replaces metadata, unlike account/container POST.
        self.openstack(
            f'object set {container} {quoted} '
            '--property first=updated --property second=two'
        )
        data = self.openstack(command, parse_output=True)
        self.assertEqual(
            {'first': 'updated', 'second': 'two'}, self.get_properties(data)
        )
        self.assertEqual(
            '',
            self.openstack(
                f'object unset {container} {quoted} '
                '--property first --property second'
            ),
        )
        data = self.openstack(command, parse_output=True)
        self.assertFalse(self.get_properties(data))

        # Download to an explicit file and stdout without uploading again.
        destination = os.path.join(directory, 'new directory', 'download')
        self.assertEqual(
            '',
            self.openstack(
                f'object save {container} {quoted} '
                f'--file {shlex.quote(destination)}'
            ),
        )
        with open(destination, 'rb') as f:
            self.assertEqual(content, f.read())
        self.assertEqual(
            content.decode(),
            self.openstack(f'object save {container} {quoted} --file -'),
        )
        self.assertEqual(
            '', self.openstack(f'object delete {container} {quoted}')
        )
        with self.assertRaises(exceptions.CommandFailed):
            self.openstack(command)

        # Download using the default name, then save the whole container.
        os.remove(names[0])
        self.assertEqual(
            '',
            self.openstack(f'object save {container} {shlex.quote(names[0])}'),
        )
        with open(names[0], 'rb') as f:
            self.assertEqual(content, f.read())
        for name in names:
            os.remove(name)
        os.rmdir(downloads)
        self.assertEqual('', self.openstack(f'container save {container}'))
        for name in names:
            with open(name, 'rb') as f:
                self.assertEqual(content, f.read())

        # Batch-delete two objects, leaving one to test recursive deletion.
        arguments = ' '.join(shlex.quote(name) for name in names[:2])
        self.assertEqual(
            '', self.openstack(f'object delete {container} {arguments}')
        )
        data = self.openstack(f'object list {container}', parse_output=True)
        self.assertEqual(names[2:], [item['Name'] for item in data])
        with self.assertRaises(exceptions.CommandFailed):
            self.openstack(f'container delete {container}')
        self.assertEqual(
            '', self.openstack(f'container delete --recursive {container}')
        )
        with self.assertRaises(exceptions.CommandFailed):
            self.openstack(f'container show {container}')
