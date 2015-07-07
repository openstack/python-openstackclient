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
import re
import shlex
import subprocess
import testtools

import six

from functional.common import exceptions

COMMON_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONAL_DIR = os.path.normpath(os.path.join(COMMON_DIR, '..'))
ROOT_DIR = os.path.normpath(os.path.join(FUNCTIONAL_DIR, '..'))
EXAMPLE_DIR = os.path.join(ROOT_DIR, 'examples')


def execute(cmd, fail_ok=False, merge_stderr=False):
    """Executes specified command for the given action."""
    cmdlist = shlex.split(cmd.encode('utf-8'))
    result = ''
    result_err = ''
    stdout = subprocess.PIPE
    stderr = subprocess.STDOUT if merge_stderr else subprocess.PIPE
    proc = subprocess.Popen(cmdlist, stdout=stdout, stderr=stderr)
    result, result_err = proc.communicate()
    if not fail_ok and proc.returncode != 0:
        raise exceptions.CommandFailed(proc.returncode, cmd, result,
                                       result_err)
    return result


class TestCase(testtools.TestCase):

    delimiter_line = re.compile('^\+\-[\+\-]+\-\+$')

    @classmethod
    def openstack(cls, cmd, fail_ok=False):
        """Executes openstackclient command for the given action."""
        return execute('openstack ' + cmd, fail_ok=fail_ok)

    @classmethod
    def get_show_opts(cls, fields=[]):
        return ' -f value ' + ' '.join(['-c ' + it for it in fields])

    @classmethod
    def get_list_opts(cls, headers=[]):
        opts = ' -f csv '
        opts = opts + ' '.join(['-c ' + it for it in headers])
        return opts

    @classmethod
    def assertOutput(cls, expected, actual):
        if expected != actual:
            raise Exception(expected + ' != ' + actual)

    @classmethod
    def assertInOutput(cls, expected, actual):
        if expected not in actual:
            raise Exception(expected + ' not in ' + actual)

    @classmethod
    def cleanup_tmpfile(cls, filename):
        try:
            os.remove(filename)
        except OSError:
            pass

    def assert_table_structure(self, items, field_names):
        """Verify that all items have keys listed in field_names."""
        for item in items:
            for field in field_names:
                self.assertIn(field, item)

    def assert_show_fields(self, items, field_names):
        """Verify that all items have keys listed in field_names."""
        for item in items:
            for key in six.iterkeys(item):
                self.assertIn(key, field_names)

    def assert_show_structure(self, items, field_names):
        """Verify that all field_names listed in keys of all items."""
        if isinstance(items, list):
            o = {}
            for d in items:
                o.update(d)
        else:
            o = items
        item_keys = o.keys()
        for field in field_names:
            self.assertIn(field, item_keys)

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
        table_ = self.table(raw_output)
        for row in table_['values']:
            item = {}
            item[row[0]] = row[1]
            items.append(item)
        return items

    def parse_listing(self, raw_output):
        """Return list of dicts with basic item parsed from cli output."""

        items = []
        table_ = self.table(raw_output)
        for row in table_['values']:
            item = {}
            for col_idx, col_key in enumerate(table_['headers']):
                item[col_key] = row[col_idx]
            items.append(item)
        return items

    def table(self, output_lines):
        """Parse single table from cli output.

        Return dict with list of column names in 'headers' key and
        rows in 'values' key.
        """
        table_ = {'headers': [], 'values': []}
        columns = None

        if not isinstance(output_lines, list):
            output_lines = output_lines.split('\n')

        if not output_lines[-1]:
            # skip last line if empty (just newline at the end)
            output_lines = output_lines[:-1]

        for line in output_lines:
            if self.delimiter_line.match(line):
                columns = self._table_columns(line)
                continue
            if '|' not in line:
                continue
            row = []
            for col in columns:
                row.append(line[col[0]:col[1]].strip())
            if table_['headers']:
                table_['values'].append(row)
            else:
                table_['headers'] = row

        return table_

    def _table_columns(self, first_table_row):
        """Find column ranges in output line.

        Return list of tuples (start,end) for each column
        detected by plus (+) characters in delimiter line.
        """
        positions = []
        start = 1  # there is '+' at 0
        while start < len(first_table_row):
            end = first_table_row.find('+', start)
            if end == -1:
                break
            positions.append((start, end))
            start = end + 1
        return positions
