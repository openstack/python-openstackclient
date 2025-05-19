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

"""Volume v3 API Library

A collection of wrappers for deprecated Block Storage v3 APIs that are not
intentionally supported by SDK.
"""

import http

from openstack import exceptions as sdk_exceptions
from osc_lib import exceptions


# consistency groups


def find_consistency_group(compute_client, name_or_id):
    """Find the consistency group for a given name or ID

    https://docs.openstack.org/api-ref/block-storage/v3/#show-a-consistency-group-s-details

    :param volume_client: A volume client
    :param name_or_id: The name or ID of the consistency group to look up
    :returns: A consistency group object
    :raises exception.NotFound: If a matching consistency group could not be
        found or more than one match was found
    """
    response = compute_client.get(f'/consistencygroups/{name_or_id}')
    if response.status_code != http.HTTPStatus.NOT_FOUND:
        # there might be other, non-404 errors
        sdk_exceptions.raise_from_response(response)
        return response.json()['consistencygroup']

    response = compute_client.get('/consistencygroups')
    sdk_exceptions.raise_from_response(response)
    found = None
    consistency_groups = response.json()['consistencygroups']
    for consistency_group in consistency_groups:
        if consistency_group['name'] == name_or_id:
            if found:
                raise exceptions.NotFound(
                    f'multiple matches found for {name_or_id}'
                )
            found = consistency_group

    if not found:
        raise exceptions.NotFound(f'{name_or_id} not found')

    return found
