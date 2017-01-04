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

"""Image v1 API Library"""

from openstackclient.api import api


class APIv1(api.BaseAPI):
    """Image v1 API"""

    _endpoint_suffix = '/v1'

    def __init__(self, endpoint=None, **kwargs):
        super(APIv1, self).__init__(endpoint=endpoint, **kwargs)

        self.endpoint = self.endpoint.rstrip('/')
        self._munge_url()

    def _munge_url(self):
        # Hack this until discovery is up
        if not self.endpoint.endswith(self._endpoint_suffix):
            self.endpoint = self.endpoint + self._endpoint_suffix

    def image_list(
        self,
        detailed=False,
        public=False,
        private=False,
        **filter
    ):
        """Get available images

        :param detailed:
            Retrieve detailed response from server if True
        :param public:
            Return public images if True
        :param private:
            Return private images if True

        If public and private are both True or both False then all images are
        returned.  Both arguments False is equivalent to no filter and all
        images are returned.  Both arguments True is a filter that includes
        both public and private images which is the same set as all images.

        http://docs.openstack.org/api/openstack-image-service/1.1/content/requesting-a-list-of-public-vm-images.html
        http://docs.openstack.org/api/openstack-image-service/1.1/content/requesting-detailed-metadata-on-public-vm-images.html
        http://docs.openstack.org/api/openstack-image-service/1.1/content/filtering-images-returned-via-get-images-and-get-imagesdetail.html
        """

        url = "/images"
        if detailed or public or private:
            # Because we can't all use /details
            url += "/detail"

        image_list = self.list(url, **filter)['images']

        if public != private:
            # One is True and one is False, so public represents the filter
            # state in either case
            image_list = [i for i in image_list if i['is_public'] == public]

        return image_list
