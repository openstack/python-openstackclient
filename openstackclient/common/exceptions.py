#   Copyright 2012-2013 OpenStack, LLC.
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

"""Exception definitions."""


class CommandError(Exception):
    pass


class AuthorizationFailure(Exception):
    pass


class NoTokenLookupException(Exception):
    """This does not support looking up endpoints from an existing token."""
    pass


class EndpointNotFound(Exception):
    """Could not find Service or Region in Service Catalog."""
    pass


class UnsupportedVersion(Exception):
    """The user is trying to use an unsupported version of the API"""
    pass


class ClientException(Exception):
    """The base exception class for all exceptions this library raises."""
    def __init__(self, code, message=None, details=None):
        self.code = code
        self.message = message or self.__class__.message
        self.details = details

    def __str__(self):
        return "%s (HTTP %s)" % (self.message, self.code)


class BadRequest(ClientException):
    """HTTP 400 - Bad request: you sent some malformed data."""
    http_status = 400
    message = "Bad request"


class Unauthorized(ClientException):
    """HTTP 401 - Unauthorized: bad credentials."""
    http_status = 401
    message = "Unauthorized"


class Forbidden(ClientException):
    """HTTP 403 - Forbidden: not authorized to access to this resource."""
    http_status = 403
    message = "Forbidden"


class NotFound(ClientException):
    """HTTP 404 - Not found"""
    http_status = 404
    message = "Not found"


class Conflict(ClientException):
    """HTTP 409 - Conflict"""
    http_status = 409
    message = "Conflict"


class OverLimit(ClientException):
    """HTTP 413 - Over limit: reached the API limits for this time period."""
    http_status = 413
    message = "Over limit"


# NotImplemented is a python keyword.
class HTTPNotImplemented(ClientException):
    """HTTP 501 - Not Implemented: server does not support this operation."""
    http_status = 501
    message = "Not Implemented"


# In Python 2.4 Exception is old-style and thus doesn't have a __subclasses__()
# so we can do this:
#     _code_map = dict((c.http_status, c)
#                      for c in ClientException.__subclasses__())
#
# Instead, we have to hardcode it:
_code_map = dict((c.http_status, c) for c in [
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    OverLimit,
    HTTPNotImplemented
])


def from_response(response, body):
    """Return an instance of a ClientException based on an httplib2 response.

    Usage::

        resp, body = http.request(...)
        if resp.status != 200:
            raise exception_from_response(resp, body)
    """
    cls = _code_map.get(response.status, ClientException)
    if body:
        if hasattr(body, 'keys'):
            error = body[body.keys()[0]]
            message = error.get('message', None)
            details = error.get('details', None)
        else:
            # If we didn't get back a properly formed error message we
            # probably couldn't communicate with Keystone at all.
            message = "Unable to communicate with image service: %s." % body
            details = None
        return cls(code=response.status, message=message, details=details)
    else:
        return cls(code=response.status)
