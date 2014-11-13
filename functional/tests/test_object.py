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
import uuid

from functional.common import test

BASIC_LIST_HEADERS = ['Name']
CONTAINER_FIELDS = ['account', 'container', 'x-trans-id']
OBJECT_FIELDS = ['object', 'container', 'etag']


class ObjectV1Tests(test.TestCase):
    """Functional tests for Object V1 commands. """

    CONTAINER_NAME = uuid.uuid4().hex
    OBJECT_NAME = uuid.uuid4().hex

    def setUp(self):
        super(ObjectV1Tests, self).setUp()
        self.addCleanup(os.remove, self.OBJECT_NAME)
        with open(self.OBJECT_NAME, 'w') as f:
            f.write('test content')

    def test_container_create(self):
        raw_output = self.openstack('container create ' + self.CONTAINER_NAME)
        items = self.parse_listing(raw_output)
        self.assert_show_fields(items, CONTAINER_FIELDS)

    def test_container_delete(self):
        container_tmp = uuid.uuid4().hex
        self.openstack('container create ' + container_tmp)
        raw_output = self.openstack('container delete ' + container_tmp)
        self.assertEqual(0, len(raw_output))

    def test_container_list(self):
        raw_output = self.openstack('container list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_LIST_HEADERS)

    def test_container_show(self):
        self.openstack('container show ' + self.CONTAINER_NAME)
        # TODO(stevemar): Assert returned fields

    def test_container_save(self):
        self.openstack('container save ' + self.CONTAINER_NAME)
        # TODO(stevemar): Assert returned fields

    def test_object_create(self):
        raw_output = self.openstack('object create ' + self.CONTAINER_NAME
                                    + ' ' + self.OBJECT_NAME)
        items = self.parse_listing(raw_output)
        self.assert_show_fields(items, OBJECT_FIELDS)

    def test_object_delete(self):
        raw_output = self.openstack('object delete ' + self.CONTAINER_NAME
                                    + ' ' + self.OBJECT_NAME)
        self.assertEqual(0, len(raw_output))

    def test_object_list(self):
        raw_output = self.openstack('object list ' + self.CONTAINER_NAME)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_LIST_HEADERS)

    def test_object_save(self):
        self.openstack('object create ' + self.CONTAINER_NAME
                       + ' ' + self.OBJECT_NAME)
        self.openstack('object save ' + self.CONTAINER_NAME
                       + ' ' + self.OBJECT_NAME)
        # TODO(stevemar): Assert returned fields

    def test_object_save_with_filename(self):
        self.openstack('object create ' + self.CONTAINER_NAME
                       + ' ' + self.OBJECT_NAME)
        self.openstack('object save ' + self.CONTAINER_NAME
                       + ' ' + self.OBJECT_NAME + ' --file tmp.txt')
        # TODO(stevemar): Assert returned fields

    def test_object_show(self):
        self.openstack('object create ' + self.CONTAINER_NAME
                       + ' ' + self.OBJECT_NAME)
        self.openstack('object show ' + self.CONTAINER_NAME
                       + ' ' + self.OBJECT_NAME)
        # TODO(stevemar): Assert returned fields
