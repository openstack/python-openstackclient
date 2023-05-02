# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from osc_lib.cli import format_columns
from osc_lib.command import command

from openstackclient.i18n import _


class ImportInfo(command.ShowOne):
    _description = _("Show available import methods")

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        import_info = image_client.get_import_info()
        import_methods = import_info.import_methods or {}
        return (
            ('import-methods',),
            (format_columns.ListColumn(import_methods.get('value', [])),),
        )
