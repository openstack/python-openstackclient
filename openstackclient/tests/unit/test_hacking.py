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

import importlib.util
import os
import re
import subprocess
import sys
import unittest

import fixtures

ROOT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')
)
SELFTEST_REGEX = re.compile(r'\b(Okay|[HEW]\d{3}|O\d{3}):\s(.*)')

# Checks that filter on 'openstackclient/tests/unit' in the filename need the
# temp file written into that path structure so the check is not skipped.
_UNIT_TEST_SUBDIRS = {
    'O401': os.path.join('openstackclient', 'tests', 'unit'),
    'O402': os.path.join('openstackclient', 'tests', 'unit'),
}


def _load_checks():
    spec = importlib.util.spec_from_file_location(
        '_osc_hacking_checks',
        os.path.join(ROOT_DIR, 'hacking', 'checks.py'),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _get_examples(check):
    for line in check.__doc__.splitlines():
        line = line.lstrip()
        match = SELFTEST_REGEX.match(line)
        if match:
            yield match.group(1), match.group(2)


class HackingTestCase(unittest.TestCase):
    def _test_check(self, code, source):
        lines = [
            part.replace(r'\t', '\t') + '\n' for part in source.split(r'\n')
        ]
        subdir = {
            'O401': os.path.join('openstackclient', 'tests', 'unit'),
            'O402': os.path.join('openstackclient', 'tests', 'unit'),
        }.get(code, '')

        with fixtures.TempDir() as tmp:
            dirpath = os.path.join(tmp.path, subdir) if subdir else tmp.path
            if subdir:
                os.makedirs(dirpath)

            fpath = os.path.join(dirpath, 'test_tmp.py')
            with open(fpath, 'w') as f:
                f.write(''.join(lines))

            cmd = [
                sys.executable,
                '-mflake8',
                '--config',
                os.path.join(ROOT_DIR, 'tox.ini'),
                f'--select={code}',
                '--format=%(code)s\t%(path)s\t%(row)d',
                fpath,
            ]
            out, _ = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, cwd=ROOT_DIR
            ).communicate()
            out = out.decode('utf-8')

            if code == 'Okay':
                self.assertEqual('', out)
            else:
                self.assertNotEqual('', out, f"Failed to trigger rule {code}")
                self.assertEqual(code, out.split('\t')[0].rstrip(':'), out)

    def test_checks(self):
        checks_module = _load_checks()

        for name in sorted(dir(checks_module)):
            check = getattr(checks_module, name)
            if not callable(check):
                continue

            if getattr(check, 'skip_on_py3', None) is not False:
                continue

            if not check.__doc__:
                continue

            for code, source in _get_examples(check):
                with self.subTest(check=name, example=source):
                    self._test_check(code, source)
