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


class CommandFailed(Exception):
    def __init__(self, returncode, cmd, output, stderr):
        super(CommandFailed, self).__init__()
        self.returncode = returncode
        self.cmd = cmd
        self.stdout = output
        self.stderr = stderr

    def __str__(self):
        return ("Command '%s' returned non-zero exit status %d.\n"
                "stdout:\n%s\n"
                "stderr:\n%s" % (self.cmd, self.returncode,
                                 self.stdout, self.stderr))
