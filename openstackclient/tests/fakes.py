#   Copyright 2013 Nebula Inc.
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

import json
import six
import sys

import requests


AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"


class FakeStdout:
    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        result = ''
        for line in self.content:
            result = result + line
        return result


class FakeApp(object):
    def __init__(self, _stdout):
        self.stdout = _stdout
        self.client_manager = None
        self.stdin = sys.stdin
        self.stdout = _stdout or sys.stdout
        self.stderr = sys.stderr


class FakeClientManager(object):
    def __init__(self):
        self.compute = None
        self.identity = None
        self.image = None
        self.object = None
        self.volume = None
        self.network = None
        self.session = None
        self.auth_ref = None


class FakeModule(object):
    def __init__(self, name, version):
        self.name = name
        self.__version__ = version


class FakeResource(object):
    def __init__(self, manager, info, loaded=False):
        self.manager = manager
        self._info = info
        self._add_details(info)
        self._loaded = loaded

    def _add_details(self, info):
        for (k, v) in six.iteritems(info):
            setattr(self, k, v)

    def __repr__(self):
        reprkeys = sorted(k for k in self.__dict__.keys() if k[0] != '_' and
                          k != 'manager')
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)


class FakeResponse(requests.Response):
    def __init__(self, headers={}, status_code=200, data=None, encoding=None):
        super(FakeResponse, self).__init__()

        self.status_code = status_code

        self.headers.update(headers)
        self._content = json.dumps(data)
        if not isinstance(self._content, six.binary_type):
            self._content = self._content.encode()
