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


def find(client, resource, resources, name_or_id, name_attr='name'):
    """Find a network resource

    :param client: network client
    :param resource: name of the resource
    :param resources: plural name of resource
    :param name_or_id: name or id of resource user is looking for
    :param name_attr: key to the name attribute for the resource

    For example:
        n = find(netclient, 'network', 'networks', 'matrix')
    """
    list_method = getattr(client, "find_%s" % resource)
    data = list_method(name_or_id, ignore_missing=False)
    return data.id
