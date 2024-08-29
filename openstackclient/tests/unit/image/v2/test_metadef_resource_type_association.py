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

from openstackclient.image.v2 import metadef_resource_type_association
from openstackclient.tests.unit.image.v2 import fakes as resource_type_fakes


class TestMetadefResourceTypeAssociationCreate(
    resource_type_fakes.TestImagev2
):
    resource_type_association = (
        resource_type_fakes.create_one_resource_type_association()
    )

    columns = (
        'created_at',
        'id',
        'name',
        'prefix',
        'properties_target',
        'updated_at',
    )

    data = (
        resource_type_association.created_at,
        resource_type_association.id,
        resource_type_association.name,
        resource_type_association.prefix,
        resource_type_association.properties_target,
        resource_type_association.updated_at,
    )

    def setUp(self):
        super().setUp()

        self.image_client.create_metadef_resource_type_association.return_value = self.resource_type_association
        self.cmd = metadef_resource_type_association.CreateMetadefResourceTypeAssociation(
            self.app, None
        )

    def test_resource_type_association_create(self):
        arglist = [
            self.resource_type_association.namespace_name,
            self.resource_type_association.name,
        ]

        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestMetadefResourceTypeAssociationDelete(
    resource_type_fakes.TestImagev2
):
    resource_type_association = (
        resource_type_fakes.create_one_resource_type_association()
    )

    def setUp(self):
        super().setUp()

        self.image_client.delete_metadef_resource_type_association.return_value = self.resource_type_association
        self.cmd = metadef_resource_type_association.DeleteMetadefResourceTypeAssociation(
            self.app, None
        )

    def test_resource_type_association_delete(self):
        arglist = [
            self.resource_type_association.namespace_name,
            self.resource_type_association.name,
        ]

        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)


class TestMetadefResourceTypeAssociationList(resource_type_fakes.TestImagev2):
    resource_type_associations = (
        resource_type_fakes.create_resource_type_associations()
    )

    columns = ['Name']

    datalist = [
        (resource_type_association.name,)
        for resource_type_association in resource_type_associations
    ]

    def setUp(self):
        super().setUp()

        self.image_client.metadef_resource_type_associations.side_effect = [
            self.resource_type_associations,
            [],
        ]

        self.cmd = metadef_resource_type_association.ListMetadefResourceTypeAssociations(
            self.app, None
        )

    def test_resource_type_association_list(self):
        arglist = [
            self.resource_type_associations[0].namespace_name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)
