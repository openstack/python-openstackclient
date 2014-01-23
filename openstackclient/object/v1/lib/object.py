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

import six

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def list_objects(
    api,
    url,
    container,
    marker=None,
    limit=None,
    end_marker=None,
    delimiter=None,
    prefix=None,
    path=None,
    full_listing=False,
):
    """Get objects in a container

    :param api: a restapi object
    :param url: endpoint
    :param container: container name to get a listing for
    :param marker: marker query
    :param limit: limit query
    :param end_marker: marker query
    :param delimiter: string to delimit the queries on
    :param prefix: prefix query
    :param path: path query (equivalent: "delimiter=/" and "prefix=path/")
    :param full_listing: if True, return a full listing, else returns a max
                         of 10000 listings
    :returns: a tuple of (response headers, a list of objects) The response
              headers will be a dict and all header names will be lowercase.
    """

    if full_listing:
        data = listing = list_objects(
            api,
            url,
            container,
            marker,
            limit,
            end_marker,
            delimiter,
            prefix,
            path,
        )
        while listing:
            if delimiter:
                marker = listing[-1].get('name', listing[-1].get('subdir'))
            else:
                marker = listing[-1]['name']
            listing = list_objects(
                api,
                url,
                container,
                marker,
                limit,
                end_marker,
                delimiter,
                prefix,
                path,
            )
            if listing:
                data.extend(listing)
        return data

    object_url = url
    params = {
        'format': 'json',
    }
    if marker:
        params['marker'] = marker
    if limit:
        params['limit'] = limit
    if end_marker:
        params['end_marker'] = end_marker
    if delimiter:
        params['delimiter'] = delimiter
    if prefix:
        params['prefix'] = prefix
    if path:
        params['path'] = path
    url = "%s/%s" % (object_url, container)
    return api.list(url, params=params)


def show_object(
    api,
    url,
    container,
    obj,
):
    """Get object details

    :param api: a restapi object
    :param url: endpoint
    :param container: container name to get a listing for
    :returns: dict of object properties
    """

    response = api.head("%s/%s/%s" % (url, container, obj))
    url_parts = urlparse(url)
    data = {
        'account': url_parts.path.split('/')[-1],
        'container': container,
        'object': obj,
    }
    data['content-type'] = response.headers.get('content-type', None)
    if 'content-length' in response.headers:
        data['content-length'] = response.headers.get('content-length', None)
    if 'last-modified' in response.headers:
        data['last-modified'] = response.headers.get('last-modified', None)
    if 'etag' in response.headers:
        data['etag'] = response.headers.get('etag', None)
    if 'x-object-manifest' in response.headers:
        data['x-object-manifest'] = response.headers.get(
            'x-object-manifest', None)
    for key, value in six.iteritems(response.headers):
        if key.startswith('x-object-meta-'):
            data[key[len('x-object-meta-'):].title()] = value
        elif key not in (
                'content-type', 'content-length', 'last-modified',
                'etag', 'date', 'x-object-manifest'):
            data[key.title()] = value

    return data
