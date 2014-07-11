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

import mock

extension_name = 'Matrix'
extension_namespace = 'http://docs.openstack.org/network/'
extension_description = 'Simulated reality'
extension_updated = '2013-07-09T12:00:0-00:00'
extension_alias = 'Dystopian'
extension_links = '[{"href":''"https://github.com/os/network", "type"}]'

NETEXT = {
    'name': extension_name,
    'namespace': extension_namespace,
    'description': extension_description,
    'updated': extension_updated,
    'alias': extension_alias,
    'links': extension_links,
}


class FakeNetworkV2Client(object):
    def __init__(self, **kwargs):
        self.list_extensions = mock.Mock(return_value={'extensions': [NETEXT]})
