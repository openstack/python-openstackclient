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

import json
import logging
import os
import shlex
import subprocess

from tempest.lib.cli import output_parser
from tempest.lib import exceptions
import testtools

ADMIN_CLOUD = os.environ.get('OS_ADMIN_CLOUD', 'devstack-admin')
LOG = logging.getLogger(__name__)


def execute(cmd, *, fail_ok=False):
    """Executes specified command for the given action."""
    LOG.debug('Executing: %s', cmd)
    cmdlist = shlex.split(cmd)
    stdout = subprocess.PIPE
    stderr = subprocess.PIPE
    env = {
        k: v for k, v in os.environ.copy().items() if not k.startswith('OS_')
    }

    proc = subprocess.Popen(cmdlist, stdout=stdout, stderr=stderr, env=env)

    result_out_b, result_err = proc.communicate()
    result_out = result_out_b.decode('utf-8')
    LOG.debug('stdout: %s', result_out)
    LOG.debug('stderr: %s', result_err)

    if not fail_ok and proc.returncode != 0:
        raise exceptions.CommandFailed(
            proc.returncode,
            cmd,
            result_out,
            result_err,
        )

    return result_out


class TestCase(testtools.TestCase):
    @classmethod
    def openstack(
        cls,
        cmd,
        *,
        cloud=ADMIN_CLOUD,
        fail_ok=False,
        parse_output=False,
    ):
        """Executes openstackclient command for the given action

        :param cmd: A string representation of the command to execute.
        :param cloud: The cloud to execute against. This can be a string, empty
            string, or None. A string results in '--os-auth-type $cloud', an
            empty string results in the '--os-auth-type' option being
            omitted, and None results in '--os-auth-type none' for legacy
            reasons.
        :param fail_ok: If failure is permitted. If False (default), a command
            failure will result in `~tempest.lib.exceptions.CommandFailed`
            being raised.
        :param parse_output: If true, pass the '-f json' parameter and decode
            the output.
        :returns: The output from the command.
        :raises: `~tempest.lib.exceptions.CommandFailed` if the command failed
            and ``fail_ok`` was ``False``.
        """
        auth_args = []
        if cloud is None:
            # Execute command with no auth
            auth_args.append('--os-auth-type none')
        elif cloud != '':
            # Execute command with an explicit cloud specified
            auth_args.append(f'--os-cloud {cloud}')

        format_args = []
        if parse_output:
            format_args.append('-f json')

        output = execute(
            ' '.join(['openstack'] + auth_args + [cmd] + format_args),
            fail_ok=fail_ok,
        )

        if parse_output:
            return json.loads(output)
        else:
            return output

    @classmethod
    def is_service_enabled(cls, service, version=None):
        """Ask client cloud if service is available

        :param service: The service name or type. This should be either an
            exact match to what is in the catalog or a known official value or
            alias from service-types-authority
        :param version: Optional version. This should be a major version, e.g.
            '2.0'
        :returns: True if the service is enabled and optionally provides the
            specified API version, else False
        """
        ret = cls.openstack(
            f'versions show --service {service} -f value -c Version'
        ).splitlines()
        if version:
            return version in ret

        return bool(ret)

    @classmethod
    def is_extension_enabled(cls, alias, *, service='network'):
        """Ask client cloud if extension is enabled"""
        extensions = cls.openstack(
            f'extension list --{service}',
            parse_output=True,
        )
        return alias in [x['Alias'] for x in extensions]

    @classmethod
    def get_openstack_configuration_value(cls, configuration):
        opts = cls.get_opts([configuration])
        return cls.openstack('configuration show ' + opts)

    @classmethod
    def get_opts(cls, fields, output_format='value'):
        return ' -f {} {}'.format(
            output_format, ' '.join(['-c ' + it for it in fields])
        )

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
