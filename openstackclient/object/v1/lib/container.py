#   Copyright 2010-2012 OpenStack Foundation
#   Copyright 2013 Nebula Inc.
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

"""Object v1 API library"""

try:
    from urllib.parse import urlparse  # noqa
except ImportError:
    from urlparse import urlparse  # noqa

from openstackclient.object.v1.lib import object as object_lib


def create_container(
    session,
    url,
    container,
):
    """Create a container

    :param session: an authenticated keystoneclient.session.Session object
    :param url: endpoint
    :param container: name of container to create
    :returns: dict of returned headers
    """

    response = session.put("%s/%s" % (url, container))
    url_parts = urlparse(url)
    data = {
        'account': url_parts.path.split('/')[-1],
        'container': container,
        'x-trans-id': response.headers.get('x-trans-id', None),
    }

    return data


def delete_container(
    session,
    url,
    container,
):
    """Delete a container

    :param session: an authenticated keystoneclient.session.Session object
    :param url: endpoint
    :param container: name of container to delete
    """

    session.delete("%s/%s" % (url, container))


def list_containers(
    session,
    url,
    marker=None,
    limit=None,
    end_marker=None,
    prefix=None,
    full_listing=False,
):
    """Get containers in an account

    :param session: an authenticated keystoneclient.session.Session object
    :param url: endpoint
    :param marker: marker query
    :param limit: limit query
    :param end_marker: end_marker query
    :param prefix: prefix query
    :param full_listing: if True, return a full listing, else returns a max
                         of 10000 listings
    :returns: list of containers
    """

    if full_listing:
        data = listing = list_containers(
            session,
            url,
            marker,
            limit,
            end_marker,
            prefix,
        )
        while listing:
            marker = listing[-1]['name']
            listing = list_containers(
                session,
                url,
                marker,
                limit,
                end_marker,
                prefix,
            )
            if listing:
                data.extend(listing)
        return data

    params = {
        'format': 'json',
    }
    if marker:
        params['marker'] = marker
    if limit:
        params['limit'] = limit
    if end_marker:
        params['end_marker'] = end_marker
    if prefix:
        params['prefix'] = prefix
    return session.get(url, params=params).json()


def save_container(
    session,
    url,
    container
):
    """Save all the content from a container

    :param session: an authenticated keystoneclient.session.Session object
    :param url: endpoint
    :param container: name of container to save
    """

    objects = object_lib.list_objects(session, url, container)
    for object in objects:
        object_lib.save_object(session, url, container, object['name'])


def show_container(
    session,
    url,
    container,
):
    """Get container details

    :param session: an authenticated keystoneclient.session.Session object
    :param url: endpoint
    :param container: name of container to show
    :returns: dict of returned headers
    """

    response = session.head("%s/%s" % (url, container))
    data = {
        'account': response.headers.get('x-container-meta-owner', None),
        'container': container,
        'object_count': response.headers.get(
            'x-container-object-count',
            None,
        ),
        'bytes_used': response.headers.get('x-container-bytes-used', None),
        'read_acl': response.headers.get('x-container-read', None),
        'write_acl': response.headers.get('x-container-write', None),
        'sync_to': response.headers.get('x-container-sync-to', None),
        'sync_key': response.headers.get('x-container-sync-key', None),
    }

    return data
