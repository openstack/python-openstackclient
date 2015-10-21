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

"""Subclass of keystoneauth1.session"""

from keystoneauth1 import session


class TimingSession(session.Session):
    """A Session that supports collection of timing data per Method URL"""

    def __init__(
            self,
            **kwargs
    ):
        """Pass through all arguments except timing"""
        super(TimingSession, self).__init__(**kwargs)

        # times is a list of tuples: ("method url", elapsed_time)
        self.times = []

    def get_timings(self):
        return self.times

    def reset_timings(self):
        self.times = []

    def request(self, url, method, **kwargs):
        """Wrap the usual request() method with the timers"""
        resp = super(TimingSession, self).request(url, method, **kwargs)
        for h in resp.history:
            self.times.append((
                "%s %s" % (h.request.method, h.request.url),
                h.elapsed,
            ))
        self.times.append((
            "%s %s" % (resp.request.method, resp.request.url),
            resp.elapsed,
        ))
        return resp
