#   Copyright 2012-2013 OpenStack, LLC.
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

"""Modify Cliff's CommandManager"""

import logging
import pkg_resources

import cliff.commandmanager


LOG = logging.getLogger(__name__)


class CommandManager(cliff.commandmanager.CommandManager):
    """Alters Cliff's default CommandManager behaviour to load additiona
       command groups after initialization.
    """
    def _load_commands(self, group=None):
        if not group:
            group = self.namespace
        for ep in pkg_resources.iter_entry_points(group):
            LOG.debug('found command %r' % ep.name)
            self.commands[ep.name.replace('_', ' ')] = ep
        return

    def add_command_group(self, group=None):
        """Adds another group of command entrypoints"""
        if group:
            self._load_commands(group)
