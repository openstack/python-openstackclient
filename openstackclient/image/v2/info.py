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


import argparse
from collections.abc import Iterable, Sequence
import json
from typing import Any

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns

from openstackclient import command
from openstackclient.i18n import _


class PluginsColumn(cliff_columns.FormattableColumn[list[dict[str, Any]]]):
    # This is used to format the configured plugins when using --detail.
    # There is no nice-looking way of showing these values to the user, so we
    # keep raw json.
    def human_readable(self) -> str:
        return json.dumps(self._value, indent=4)


class ImportInfo(command.ShowOneWithDetails):
    _description = _("Show available import methods")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--detail',
            action='store_true',
            default=False,
            help=_("Shows configured import plugins and their properties"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Sequence[Any]]]:
        image_client = self.app.client_manager.image

        import_info = image_client.get_import_info(
            detail=parsed_args.detail,
        )
        import_methods = import_info.import_methods or {}

        column_headers: tuple[str, ...] = ('Field', 'Value')
        row: tuple[Any, ...] = (
            'import-methods',
            format_columns.ListColumn(import_methods.get('value', [])),
        )

        if parsed_args.detail:
            column_headers += ('Plugins',)
            row += (PluginsColumn(import_info.plugins or []),)

        return (column_headers, (row,))
