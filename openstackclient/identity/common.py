#   Copyright 2012-2013 OpenStack Foundation
#
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

"""Common identity code"""

from keystoneclient import exceptions as identity_exc
from openstackclient.common import exceptions
from openstackclient.common import utils


def find_service(identity_client, name_type_or_id):
    """Find a service by id, name or type."""

    try:
        # search for the usual ID or name
        return utils.find_resource(identity_client.services, name_type_or_id)
    except exceptions.CommandError:
        try:
            # search for service type
            return identity_client.services.find(type=name_type_or_id)
        # FIXME(dtroyer): This exception should eventually come from
        #                 common client exceptions
        except identity_exc.NotFound:
            msg = ("No service with a type, name or ID of '%s' exists."
                   % name_type_or_id)
            raise exceptions.CommandError(msg)
