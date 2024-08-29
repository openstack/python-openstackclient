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

"""Image v2 API Library"""

from openstackclient.api import image_v1


class APIv2(image_v1.APIv1):
    """Image v2 API"""

    _endpoint_suffix = '/v2'

    def _munge_url(self):
        # Hack this until discovery is up, and ignore parent endpoint setting
        if not self.endpoint.endswith(self._endpoint_suffix):
            self.endpoint = self.endpoint + self._endpoint_suffix

    def image_list(
        self,
        detailed=False,
        public=False,
        private=False,
        community=False,
        shared=False,
        **filter,
    ):
        """Get available images

        can add limit/marker

        :param detailed:
            For v1 compatibility only, ignored as v2 is always 'detailed'
        :param public:
            Return public images if True
        :param private:
            Return private images if True
        :param community:
            Return commuity images if True
        :param shared:
            Return shared images if True

        If public, private, community and shared are all True or all False
        then all images are returned.  All arguments False is equivalent to no
        filter and all images are returned.  All arguments True is a filter
        that includes all public, private, community and shared images which
        is the same set as all images.

        http://docs.openstack.org/api/openstack-image-service/2.0/content/list-images.html
        """

        if not public and not private and not community and not shared:
            # No filtering for all False
            filter.pop('visibility', None)
        elif public:
            filter['visibility'] = 'public'
        elif private:
            filter['visibility'] = 'private'
        elif community:
            filter['visibility'] = 'community'
        elif shared:
            filter['visibility'] = 'shared'

        url = "/images"
        if detailed:
            # Because we can't all use /details
            url += "/detail"

        return self.list(url, **filter)['images']
