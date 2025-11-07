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

import os
import re

from hacking import core

"""
Guidelines for writing new hacking checks

 - Use only for python-openstackclient specific tests. OpenStack general tests
   should be submitted to the common 'hacking' module.
 - Pick numbers in the range O4xx. Find the current test with the highest
   allocated number and then pick the next value.
"""


@core.flake8ext
def assert_no_oslo(logical_line):
    """Check for use of oslo libraries.

    O400
    """
    if re.match(r'(from|import) oslo_.*', logical_line):
        yield (0, "0400: oslo libraries should not be used in SDK projects")


@core.flake8ext
def assert_no_duplicated_setup(logical_line, filename):
    """Check for use of various unnecessary test duplications.

    O401
    """
    if os.path.join('openstackclient', 'tests', 'unit') not in filename:
        return

    if re.match(r'self.app = .*\(self.app, self.namespace\)', logical_line):
        yield (
            0,
            'O401: It is not necessary to create dummy Namespace objects',
        )

    if os.path.basename(filename) != 'fakes.py':
        if re.match(
            r'self.[a-z_]+_client = self.app.client_manager.*', logical_line
        ):
            yield (
                0,
                "O401: Aliases for mocks of the service client are already "
                "provided by the respective service's FakeClientMixin class",
            )

        if match := re.match(
            r'self.app.client_manager.([a-z_]+) = mock.Mock', logical_line
        ):
            service = match.group(1)
            if service == 'auth_ref':
                return
            yield (
                0,
                f"O401: client_manager.{service} mocks are already provided by "
                f"the {service} service's FakeClientMixin class",
            )


@core.flake8ext
def assert_use_of_client_aliases(logical_line, filename):
    """Ensure we use $service_client instead of $sdk_connection.service.

    O402
    """
    # we should expand the list of services as we drop legacy clients
    if match := re.match(
        r'self\.app\.client_manager\.sdk_connnection\.(compute|network|image)',
        logical_line,
    ):
        service = match.group(1)
        yield (0, f"0402: prefer {service}_client to sdk_connection.{service}")

    if match := re.match(
        r'(self\.app\.client_manager\.(compute|network|image)+\.[a-z_]+) = mock.Mock',
        logical_line,
    ):
        yield (
            0,
            f"O402: {match.group(1)} is already a mock: there's no need to "
            f"assign a new mock.Mock instance.",
        )

    if match := re.match(
        r'(self\.(compute|network|image)_client\.[a-z_]+) = mock.Mock',
        logical_line,
    ):
        yield (
            0,
            f"O402: {match.group(1)} is already a mock: there's no need to "
            f"assign a new mock.Mock instance.",
        )
