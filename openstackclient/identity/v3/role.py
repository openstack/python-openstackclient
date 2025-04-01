#   Copyright 2012-2013 OpenStack Foundation
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

"""Identity v3 Role action implementations"""

import logging

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_role(role):
    columns = (
        "id",
        "name",
        "domain_id",
        "description",
    )
    column_headers = (
        "id",
        "name",
        "domain_id",
        "description",
    )
    return (
        column_headers,
        utils.get_item_properties(role, columns),
    )


def _add_identity_and_resource_options_to_parser(parser):
    system_or_domain_or_project = parser.add_mutually_exclusive_group()
    system_or_domain_or_project.add_argument(
        '--system',
        metavar='<system>',
        help=_('Include <system> (all)'),
    )
    system_or_domain_or_project.add_argument(
        '--domain',
        metavar='<domain>',
        help=_('Include <domain> (name or ID)'),
    )
    system_or_domain_or_project.add_argument(
        '--project',
        metavar='<project>',
        help=_('Include <project> (name or ID)'),
    )
    user_or_group = parser.add_mutually_exclusive_group()
    user_or_group.add_argument(
        '--user',
        metavar='<user>',
        help=_('Include <user> (name or ID)'),
    )
    user_or_group.add_argument(
        '--group',
        metavar='<group>',
        help=_('Include <group> (name or ID)'),
    )
    common.add_group_domain_option_to_parser(parser)
    common.add_project_domain_option_to_parser(parser)
    common.add_user_domain_option_to_parser(parser)
    common.add_inherited_option_to_parser(parser)


def _find_sdk_id(
    find_command, name_or_id, validate_actor_existence=True, **kwargs
):
    try:
        resource = find_command(
            name_or_id=name_or_id, ignore_missing=False, **kwargs
        )

    # Mimic the behavior of
    # openstackclient.identity.common._find_identity_resource()
    # and ignore if we don't have permission to find a resource.
    except sdk_exc.ForbiddenException:
        return name_or_id
    except sdk_exc.ResourceNotFound as exc:
        if not validate_actor_existence:
            return name_or_id
        raise exceptions.CommandError from exc
    return resource.id


def _process_identity_and_resource_options(
    parsed_args, identity_client, validate_actor_existence=True
):
    def _find_user():
        domain_id = (
            _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.user_domain,
                validate_actor_existence=validate_actor_existence,
            )
            if parsed_args.user_domain
            else None
        )
        return _find_sdk_id(
            identity_client.find_user,
            name_or_id=parsed_args.user,
            validate_actor_existence=validate_actor_existence,
            domain_id=domain_id,
        )

    def _find_group():
        domain_id = (
            _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.group_domain,
                validate_actor_existence=validate_actor_existence,
            )
            if parsed_args.group_domain
            else None
        )
        return _find_sdk_id(
            identity_client.find_group,
            name_or_id=parsed_args.group,
            validate_actor_existence=validate_actor_existence,
            domain_id=domain_id,
        )

    def _find_project():
        domain_id = (
            _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.project_domain,
                validate_actor_existence=validate_actor_existence,
            )
            if parsed_args.project_domain
            else None
        )
        return _find_sdk_id(
            identity_client.find_project,
            name_or_id=parsed_args.project,
            validate_actor_existence=validate_actor_existence,
            domain_id=domain_id,
        )

    kwargs = {}
    if parsed_args.user and parsed_args.system:
        kwargs['user'] = _find_user()
        kwargs['system'] = parsed_args.system
    elif parsed_args.user and parsed_args.domain:
        kwargs['user'] = _find_user()
        kwargs['domain'] = _find_sdk_id(
            identity_client.find_domain,
            name_or_id=parsed_args.domain,
            validate_actor_existence=validate_actor_existence,
        )
    elif parsed_args.user and parsed_args.project:
        kwargs['user'] = _find_user()
        kwargs['project'] = _find_project()
    elif parsed_args.group and parsed_args.system:
        kwargs['group'] = _find_group()
        kwargs['system'] = parsed_args.system
    elif parsed_args.group and parsed_args.domain:
        kwargs['group'] = _find_group()
        kwargs['domain'] = _find_sdk_id(
            identity_client.find_domain,
            name_or_id=parsed_args.domain,
            validate_actor_existence=validate_actor_existence,
        )
    elif parsed_args.group and parsed_args.project:
        kwargs['group'] = _find_group()
        kwargs['project'] = _find_project()
    else:
        msg = _(
            "Role not added, incorrect set of arguments "
            "provided. See openstack --help for more details"
        )
        raise exceptions.CommandError(msg)

    kwargs['inherited'] = parsed_args.inherited
    return kwargs


class AddRole(command.Command):
    _description = _(
        "Adds a role assignment to a user or group on the "
        "system, a domain, or a project"
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to add to <user> (name or ID)'),
        )
        _add_identity_and_resource_options_to_parser(parser)
        common.add_role_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        if (
            not parsed_args.user
            and not parsed_args.domain
            and not parsed_args.group
            and not parsed_args.project
        ):
            msg = _(
                "Role not added, incorrect set of arguments "
                "provided. See openstack --help for more details"
            )
            raise exceptions.CommandError(msg)

        domain_id = None
        if parsed_args.role_domain:
            domain_id = _find_sdk_id(
                identity_client.find_domain, name_or_id=parsed_args.role_domain
            )
        role = _find_sdk_id(
            identity_client.find_role,
            name_or_id=parsed_args.role,
            domain_id=domain_id,
        )

        add_kwargs = _process_identity_and_resource_options(
            parsed_args, identity_client
        )

        if add_kwargs.get("domain"):
            if add_kwargs.get("user"):
                identity_client.assign_domain_role_to_user(
                    domain=add_kwargs["domain"],
                    user=add_kwargs["user"],
                    role=role,
                    inherited=add_kwargs["inherited"],
                )
            if add_kwargs.get("group"):
                identity_client.assign_domain_role_to_group(
                    domain=add_kwargs["domain"],
                    group=add_kwargs["group"],
                    role=role,
                    inherited=add_kwargs["inherited"],
                )
        elif add_kwargs.get("project"):
            if add_kwargs.get("user"):
                identity_client.assign_project_role_to_user(
                    project=add_kwargs["project"],
                    user=add_kwargs["user"],
                    role=role,
                    inherited=add_kwargs["inherited"],
                )
            if add_kwargs.get("group"):
                identity_client.assign_project_role_to_group(
                    project=add_kwargs["project"],
                    group=add_kwargs["group"],
                    role=role,
                    inherited=add_kwargs["inherited"],
                )
        elif add_kwargs.get("system"):
            if add_kwargs["inherited"]:
                LOG.warning(
                    _(
                        "'--inherited' was given, which is not supported "
                        "when adding a system role. This will be an error "
                        "in a future release."
                    )
                )
                # TODO(0weng): This should be an error in a future release
            if add_kwargs.get("user"):
                identity_client.assign_system_role_to_user(
                    system=add_kwargs["system"],
                    user=add_kwargs["user"],
                    role=role,
                )
            if add_kwargs.get("group"):
                identity_client.assign_system_role_to_group(
                    system=add_kwargs["system"],
                    group=add_kwargs["group"],
                    role=role,
                )


class CreateRole(command.ShowOne):
    _description = _("Create new role")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<role-name>',
            help=_('New role name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Add description about the role'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the role belongs to (name or ID)'),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing role'),
        )
        common.add_resource_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        create_kwargs = {}
        if parsed_args.domain:
            create_kwargs['domain_id'] = _find_sdk_id(
                identity_client.find_domain, name_or_id=parsed_args.domain
            )

        if parsed_args.name:
            create_kwargs['name'] = parsed_args.name
        if parsed_args.description:
            create_kwargs['description'] = parsed_args.description
        create_kwargs['options'] = common.get_immutable_options(parsed_args)

        try:
            role = identity_client.create_role(**create_kwargs)

        except sdk_exc.ConflictException:
            if parsed_args.or_show:
                role = identity_client.find_role(
                    name_or_id=parsed_args.name,
                    domain_id=parsed_args.domain,
                    ignore_missing=False,
                )
                LOG.info(_('Returning existing role %s'), role.name)
            else:
                raise

        return _format_role(role)


class DeleteRole(command.Command):
    _description = _("Delete role(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'roles',
            metavar='<role>',
            nargs='+',
            help=_('Role(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the role belongs to (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        domain_id = None
        if parsed_args.domain:
            domain_id = _find_sdk_id(
                identity_client.find_domain, parsed_args.domain
            )
        errors = 0
        for role in parsed_args.roles:
            try:
                role_id = _find_sdk_id(
                    identity_client.find_role,
                    name_or_id=role,
                    domain_id=domain_id,
                )
                identity_client.delete_role(role=role_id, ignore_missing=False)
            except Exception as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to delete role with "
                        "name or ID '%(role)s': %(e)s"
                    ),
                    {'role': role, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.roles)
            msg = _("%(errors)s of %(total)s roles failed to delete.") % {
                'errors': errors,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListRole(command.Lister):
    _description = _("List roles")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Include <domain> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        if parsed_args.domain:
            domain = identity_client.find_domain(
                name_or_id=parsed_args.domain,
            )
            data = identity_client.roles(domain_id=domain.id)
            return (
                ('ID', 'Name', 'Domain'),
                (
                    utils.get_item_properties(s, ('id', 'name'))
                    + (domain.name,)
                    for s in data
                ),
            )

        else:
            data = identity_client.roles()
            return (
                ('ID', 'Name'),
                (utils.get_item_properties(s, ('id', 'name')) for s in data),
            )


class RemoveRole(command.Command):
    _description = _(
        "Removes a role assignment from system/domain/project : user/group"
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to remove (name or ID)'),
        )
        _add_identity_and_resource_options_to_parser(parser)
        common.add_role_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        if (
            not parsed_args.user
            and not parsed_args.domain
            and not parsed_args.group
            and not parsed_args.project
        ):
            msg = _(
                "Incorrect set of arguments provided. "
                "See openstack --help for more details"
            )
            raise exceptions.CommandError(msg)

        domain_id = None
        if parsed_args.role_domain:
            domain_id = _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.role_domain,
            )
        role = _find_sdk_id(
            identity_client.find_role,
            name_or_id=parsed_args.role,
            domain_id=domain_id,
        )

        remove_kwargs = _process_identity_and_resource_options(
            parsed_args,
            identity_client,
            validate_actor_existence=False,
        )

        if remove_kwargs.get("domain"):
            if remove_kwargs.get("user"):
                identity_client.unassign_domain_role_from_user(
                    domain=remove_kwargs["domain"],
                    user=remove_kwargs["user"],
                    role=role,
                    inherited=remove_kwargs["inherited"],
                )
            if remove_kwargs.get("group"):
                identity_client.unassign_domain_role_from_group(
                    domain=remove_kwargs["domain"],
                    group=remove_kwargs["group"],
                    role=role,
                    inherited=remove_kwargs["inherited"],
                )
        elif remove_kwargs.get("project"):
            if remove_kwargs.get("user"):
                identity_client.unassign_project_role_from_user(
                    project=remove_kwargs["project"],
                    user=remove_kwargs["user"],
                    role=role,
                    inherited=remove_kwargs["inherited"],
                )
            if remove_kwargs.get("group"):
                identity_client.unassign_project_role_from_group(
                    project=remove_kwargs["project"],
                    group=remove_kwargs["group"],
                    role=role,
                    inherited=remove_kwargs["inherited"],
                )
        elif remove_kwargs.get("system"):
            if remove_kwargs.get("user"):
                identity_client.unassign_system_role_from_user(
                    system=remove_kwargs["system"],
                    user=remove_kwargs["user"],
                    role=role,
                )
            if remove_kwargs.get("group"):
                identity_client.unassign_system_role_from_group(
                    system=remove_kwargs["system"],
                    group=remove_kwargs["group"],
                    role=role,
                )


class SetRole(command.Command):
    _description = _("Set role properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to modify (name or ID)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Add description about the role'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the role belongs to (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set role name'),
        )
        common.add_resource_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        update_kwargs = {}
        if parsed_args.description:
            update_kwargs["description"] = parsed_args.description
        if parsed_args.name:
            update_kwargs["name"] = parsed_args.name

        domain_id = None
        if parsed_args.domain:
            domain_id = _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.domain,
            )
            update_kwargs["domain_id"] = domain_id

        update_kwargs["options"] = common.get_immutable_options(parsed_args)
        role = _find_sdk_id(
            identity_client.find_role,
            name_or_id=parsed_args.role,
            domain_id=domain_id,
        )
        update_kwargs["role"] = role

        identity_client.update_role(**update_kwargs)


class ShowRole(command.ShowOne):
    _description = _("Display role details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to display (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the role belongs to (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        domain_id = None
        if parsed_args.domain:
            domain_id = _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.domain,
            )

        role = identity_client.find_role(
            name_or_id=parsed_args.role,
            domain_id=domain_id,
            ignore_missing=False,
        )

        return _format_role(role)
