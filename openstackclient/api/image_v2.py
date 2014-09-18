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

    def __init__(self, endpoint=None, **kwargs):
        super(APIv2, self).__init__(endpoint=endpoint, **kwargs)

        # Hack this until discovery is up, and ignore parent endpoint setting
        self.endpoint = '/'.join([endpoint.rstrip('/'), 'v2'])

    def image_list(
        self,
        detailed=False,
        public=False,
        private=False,
        **filter
    ):
        """Get available images

        can add limit/marker

        :param detailed:
            For v1 compatibility only, ignored as v2 is always 'detailed'
        :param public:
            Return public images if True
        :param private:
            Return private images if True

        If public and private are both True or both False then all images are
        returned.  Both arguments False is equivalent to no filter and all
        images are returned.  Both arguments True is a filter that includes
        both public and private images which is the same set as all images.

        http://docs.openstack.org/api/openstack-image-service/2.0/content/list-images.html

        TODO(dtroyer): Implement filtering
        """

        if public == private:
            # No filtering for both False and both True cases
            filter.pop('visibility', None)
        elif public:
            filter['visibility'] = 'public'
        elif private:
            filter['visibility'] = 'private'

        url = "/images"
        if detailed:
            # Because we can't all use /details
            url += "/detail"

        return self.list(url, **filter)['images']
