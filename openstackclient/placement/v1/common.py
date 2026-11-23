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

from typing import Any
from urllib import parse as urlparse


def url_with_filters(url: str, filters: dict[str, Any] | None = None) -> str:
    """Add a percent-encoded string of filters (a dict) to a base url."""

    def encode(value: str | bytes) -> bytes:
        return value.encode('utf-8') if isinstance(value, str) else value

    if filters:
        qs = urlparse.urlencode(
            [(encode(k), encode(v)) for k, v in filters.items()]
        )
        url = urlparse.urljoin(url, '?' + qs)

    return url


def get_required_query_param_from_args(
    required_traits: list[str], forbidden_traits: list[str]
) -> list[str]:
    # Iterate the required params and collect OR groups and simple
    # AND traits separately. Each OR group needs a separate query param
    # while the AND traits and forbidden traits can be collated to a single
    # query param
    required_query_params = []
    and_traits = []
    for required in required_traits:
        if ',' in required:
            required_query_params.append('in:' + required)
        else:
            and_traits.append(required)
    # We need an extra required query param for the and_traits and the
    # forbidden traits
    and_query = ','.join(and_traits + forbidden_traits)
    if and_query:
        required_query_params.append(and_query)
    return required_query_params
