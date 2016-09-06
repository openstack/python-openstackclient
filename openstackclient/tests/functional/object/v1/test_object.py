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

import os
import tempfile
import uuid

from openstackclient.tests.functional import base

BASIC_LIST_HEADERS = ['Name']
CONTAINER_FIELDS = ['account', 'container', 'x-trans-id']
OBJECT_FIELDS = ['object', 'container', 'etag']


class ObjectTests(base.TestCase):
    """Functional tests for Object commands. """

    CONTAINER_NAME = uuid.uuid4().hex

    def test_object(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write('test content')
            f.flush()
            self._test_object(f.name)

    def _test_object(self, object_file):
        raw_output = self.openstack('container create ' + self.CONTAINER_NAME)
        items = self.parse_listing(raw_output)
        self.assert_show_fields(items, CONTAINER_FIELDS)

        raw_output = self.openstack('container list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_LIST_HEADERS)

        self.openstack('container show ' + self.CONTAINER_NAME)
        # TODO(stevemar): Assert returned fields

        self.openstack('container save ' + self.CONTAINER_NAME)
        # TODO(stevemar): Assert returned fields

        raw_output = self.openstack('object create ' + self.CONTAINER_NAME
                                    + ' ' + object_file)
        items = self.parse_listing(raw_output)
        self.assert_show_fields(items, OBJECT_FIELDS)

        raw_output = self.openstack('object list ' + self.CONTAINER_NAME)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_LIST_HEADERS)

        self.openstack('object save ' + self.CONTAINER_NAME
                       + ' ' + object_file)
        # TODO(stevemar): Assert returned fields

        tmp_file = 'tmp.txt'
        self.addCleanup(os.remove, tmp_file)
        self.openstack('object save ' + self.CONTAINER_NAME
                       + ' ' + object_file + ' --file ' + tmp_file)
        # TODO(stevemar): Assert returned fields

        self.openstack('object show ' + self.CONTAINER_NAME
                       + ' ' + object_file)
        # TODO(stevemar): Assert returned fields

        raw_output = self.openstack('object delete ' + self.CONTAINER_NAME
                                    + ' ' + object_file)
        self.assertEqual(0, len(raw_output))

        self.openstack('object create ' + self.CONTAINER_NAME
                       + ' ' + object_file)
        raw_output = self.openstack('container delete -r ' +
                                    self.CONTAINER_NAME)
        self.assertEqual(0, len(raw_output))
