# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections.abc import Generator
import contextlib
import json
import logging
from typing import Any

import keystoneauth1.exceptions.http as ks_exceptions
from keystoneauth1 import session as ks_session
import osc_lib.exceptions as exceptions
import requests

_http_error_to_exc = {
    cls.http_status: cls for cls in exceptions.ClientException.__subclasses__()
}

LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def _wrap_http_exceptions() -> Generator[None, None, None]:
    """Reraise osc-lib exceptions with detailed messages."""
    try:
        yield
    except ks_exceptions.HttpError as exc:
        if 400 <= exc.http_status < 500:
            if exc.response is not None:
                detail = json.loads(exc.response.content)['errors'][0][
                    'detail'
                ]
                msg = detail.split('\n')[-1].strip()
            else:
                msg = '<unknown>'
            exc_class = _http_error_to_exc.get(
                exc.http_status, exceptions.CommandError
            )
            raise exc_class(exc.http_status, msg) from exc
        else:
            raise


class SessionClient:
    def __init__(
        self,
        session: ks_session.Session,
        ks_filter: dict[str, Any],
        api_version: str = '1.0',
    ) -> None:
        self.session = session
        self.ks_filter = ks_filter
        self.negotiate_api_version(api_version)

    def request(
        self, method: str, url: str, **kwargs: Any
    ) -> requests.Response:
        request_version = kwargs.pop('version', None)
        api_version = (
            self.ks_filter['service_type']
            + ' '
            + (request_version or self.api_version)
        )
        headers = kwargs.pop('headers', {})
        headers.setdefault('OpenStack-API-Version', api_version)
        headers.setdefault('Accept', 'application/json')

        with _wrap_http_exceptions():
            return self.session.request(
                url,
                method,
                headers=headers,
                endpoint_filter=self.ks_filter,
                **kwargs,
            )

    def negotiate_api_version(self, api_version: str) -> None:
        """Set api_version to self.

        If negotiate version (only majorversion) is given, talk to server to
        pick up max microversion supported both by client and by server.
        """
        if api_version not in {'1'}:
            self.api_version = api_version
            return
        client_ver = '1.39'
        self.api_version = client_ver
        resp = self.request('GET', '/', raise_exc=False)
        if resp.status_code == 406:
            server_ver = resp.json()['errors'][0]['max_version']
            self.api_version = server_ver
            LOG.debug(
                'Microversion %s not supported in server. '
                'Falling back to microversion %s',
                client_ver,
                server_ver,
            )
