#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import shlex
import subprocess

from tempest.lib.cli import output_parser
from tempest.lib import exceptions
import testtools


COMMON_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONAL_DIR = os.path.normpath(os.path.join(COMMON_DIR, '..'))
ROOT_DIR = os.path.normpath(os.path.join(FUNCTIONAL_DIR, '..'))
EXAMPLE_DIR = os.path.join(ROOT_DIR, 'examples')
ADMIN_CLOUD = os.environ.get('OS_ADMIN_CLOUD', 'devstack-admin')


def execute(cmd, fail_ok=False, merge_stderr=False):
    """Executes specified command for the given action."""
    cmdlist = shlex.split(cmd)
    stdout = subprocess.PIPE
    stderr = subprocess.STDOUT if merge_stderr else subprocess.PIPE
    proc = subprocess.Popen(cmdlist, stdout=stdout, stderr=stderr)
    result, result_err = proc.communicate()
    result = result.decode('utf-8')
    if not fail_ok and proc.returncode != 0:
        raise exceptions.CommandFailed(proc.returncode, cmd, result,
                                       result_err)
    return result


class TestCase(testtools.TestCase):

    @classmethod
    def openstack(cls, cmd, cloud=ADMIN_CLOUD, fail_ok=False):
        """Executes openstackclient command for the given action

        NOTE(dtroyer): There is a subtle distinction between pasing
        cloud=None and cloud='': for compatibility reasons passing
        cloud=None continues to include the option '--os-auth-type none'
        in the command while passing cloud='' omits the '--os-auth-type'
         option completely to let the default handlers be invoked.
        """
        if cloud is None:
            # Execute command with no auth
            return execute(
                'openstack --os-auth-type none ' + cmd,
                fail_ok=fail_ok
            )
        elif cloud == '':
            # Execute command with no auth options at all
            return execute(
                'openstack ' + cmd,
                fail_ok=fail_ok
            )
        else:
            # Execure command with an explicit cloud specified
            return execute(
                'openstack --os-cloud=' + cloud + ' ' + cmd,
                fail_ok=fail_ok
            )

    @classmethod
    def is_service_enabled(cls, service):
        """Ask client cloud if service is available"""
        cmd = ('service show -f value -c enabled {service}'
               .format(service=service))
        try:
            return "True" in cls.openstack(cmd)
        except exceptions.CommandFailed as e:
            if "No service with a type, name or ID of" in str(e):
                return False
            else:
                raise  # Unable to determine if service is enabled

    @classmethod
    def is_extension_enabled(cls, alias):
        """Ask client cloud if extension is enabled"""
        return alias in cls.openstack('extension list -f value -c Alias')

    @classmethod
    def get_openstack_configuration_value(cls, configuration):
        opts = cls.get_opts([configuration])
        return cls.openstack('configuration show ' + opts)

    @classmethod
    def get_opts(cls, fields, output_format='value'):
        return ' -f {0} {1}'.format(output_format,
                                    ' '.join(['-c ' + it for it in fields]))

    @classmethod
    def assertOutput(cls, expected, actual):
        if expected != actual:
            raise Exception(expected + ' != ' + actual)

    @classmethod
    def assertInOutput(cls, expected, actual):
        if expected not in actual:
            raise Exception(expected + ' not in ' + actual)

    @classmethod
    def assertsOutputNotNone(cls, observed):
        if observed is None:
            raise Exception('No output observed')

    def assert_table_structure(self, items, field_names):
        """Verify that all items have keys listed in field_names."""
        for item in items:
            for field in field_names:
                self.assertIn(field, item)

    def assert_show_fields(self, show_output, field_names):
        """Verify that all items have keys listed in field_names."""

        # field_names = ['name', 'description']
        # show_output = [{'name': 'fc2b98d8faed4126b9e371eda045ade2'},
        #          {'description': 'description-821397086'}]
        # this next line creates a flattened list of all 'keys' (like 'name',
        # and 'description' out of the output
        all_headers = [item for sublist in show_output for item in sublist]
        for field_name in field_names:
            self.assertIn(field_name, all_headers)

    def parse_show_as_object(self, raw_output):
        """Return a dict with values parsed from cli output."""
        items = self.parse_show(raw_output)
        o = {}
        for item in items:
            o.update(item)
        return o

    def parse_show(self, raw_output):
        """Return list of dicts with item values parsed from cli output."""

        items = []
        table_ = output_parser.table(raw_output)
        for row in table_['values']:
            item = {}
            item[row[0]] = row[1]
            items.append(item)
        return items

    def parse_listing(self, raw_output):
        """Return list of dicts with basic item parsed from cli output."""
        return output_parser.listing(raw_output)
