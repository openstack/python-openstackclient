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

import ast
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
                f"O401: client_manager.{service} mocks are already provided "
                f"by the {service} service's FakeClientMixin class",
            )


@core.flake8ext
def assert_use_of_client_aliases(logical_line):
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
        r'(self\.app\.client_manager\.(compute|network|image)+\.[a-z_]+) = mock.Mock',  # noqa: E501
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


class SDKProxyFindChecker(ast.NodeVisitor):
    """NodeVisitor to find ``*_client.find_*`` statements."""

    def __init__(self):
        self.error = False

    def visit_Call(self, node):
        # No need to keep visiting the AST if we already found something.
        if self.error:
            return

        self.generic_visit(node)

        if not (
            isinstance(node.func, ast.Attribute)
            and node.func.attr.startswith('find_')  # and
            # isinstance(node.func.value, ast.Attribute) and
            # node.func.value.attr.endswith('_client')
        ):
            # print(f'skipping: got {node.func}')
            return

        if not (
            (
                # handle calls like 'identity_client.find_project'
                isinstance(node.func.value, ast.Name)
                and node.func.value.id.endswith('client')
            )
            or (
                # handle calls like 'self.app.client_manager.image.find_image'
                isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr
                in ('identity', 'network', 'image', 'compute')
            )
        ):
            return

        if not any(kw.arg == 'ignore_missing' for kw in node.keywords):
            self.error = True


@core.flake8ext
def assert_find_ignore_missing_kwargs(logical_line, filename):
    """Ensure ignore_missing is always used for ``find_*`` SDK proxy calls.

    Okay: self.compute_client.find_server(foo, ignore_missing=True)
    Okay: self.image_client.find_server(foo, ignore_missing=False)
    Okay: self.volume_client.volumes.find(name='foo')
    O403: self.network_client.find_network(parsed_args.network)
    O403: self.compute_client.find_flavor(flavor_id, get_extra_specs=True)
    """
    if 'tests' in filename:
        return

    checker = SDKProxyFindChecker()
    try:
        parsed_logical_line = ast.parse(logical_line)
    except SyntaxError:
        # let flake8 catch this itself
        # https://github.com/PyCQA/flake8/issues/1948
        return
    checker.visit(parsed_logical_line)
    if checker.error:
        yield (
            0,
            'O403: Calls to find_* proxy methods must explicitly set '
            'ignore_missing',
        )
