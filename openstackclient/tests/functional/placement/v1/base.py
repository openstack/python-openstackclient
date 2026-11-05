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

from tempest.lib import exceptions

from openstackclient.tests.functional import base


RP_PREFIX = 'osc-placement-functional-tests-'

ARGUMENTS_MISSING = 'the following arguments are required'
ARGUMENTS_REQUIRED = 'the following arguments are required: %s'


class BaseTestCase(base.TestCase):
    VERSION = '1.0'
    error: str

    @classmethod
    def openstack(
        cls,
        cmd,
        *,
        cloud=base.ADMIN_CLOUD,
        fail_ok=False,
        parse_output=False,
        may_print_to_stderr=False,
    ):
        if cls.VERSION is not None:
            cmd = f'--os-placement-api-version {cls.VERSION} ' + cmd
        output = super().openstack(
            cmd, cloud=cloud, fail_ok=fail_ok, parse_output=parse_output
        )
        if may_print_to_stderr:
            return output, cls.error
        return output

    @classmethod
    def execute(cls, cmd, *, fail_ok=False):
        output, cls.error = base.execute_with_stderr(cmd, fail_ok=fail_ok)
        return output

    def _cleanup(self, cmd):
        try:
            self.openstack(cmd)
        except exceptions.CommandFailed as exc:
            # Ignore only resources already deleted by the test.
            message = str(exc).lower()
            if (
                'not found' not in message
                and '404' not in message
                and 'no resource provider' not in message
            ):
                raise

    def resource_class_list(self):
        return self.openstack('resource class list', parse_output=True)

    def resource_class_show(self, name):
        return self.openstack('resource class show ' + name, parse_output=True)

    def resource_class_create(self, name):
        if name.startswith('CUSTOM_OSC_'):
            self.addCleanup(self._cleanup, 'resource class delete ' + name)
        return self.openstack('resource class create ' + name)

    def resource_class_set(self, name):
        self.addCleanup(self._cleanup, 'resource class delete ' + name)
        return self.openstack('resource class set ' + name)

    def resource_class_delete(self, name):
        return self.openstack('resource class delete ' + name)
