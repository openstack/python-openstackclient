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

"""Common identity code"""

from keystoneclient import exceptions as identity_exc
from keystoneclient.v3 import domains
from keystoneclient.v3 import groups
from keystoneclient.v3 import projects
from keystoneclient.v3 import users
from openstack import exceptions as sdk_exceptions
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


def find_service_in_list(service_list, service_id):
    """Find a service by id in service list."""

    for service in service_list:
        if service.id == service_id:
            return service
    raise exceptions.CommandError(
        f"No service with a type, name or ID of '{service_id}' exists."
    )


def find_service(identity_client, name_type_or_id):
    """Find a service by id, name or type."""

    try:
        # search for service id
        return identity_client.services.get(name_type_or_id)
    except identity_exc.NotFound:
        # ignore NotFound exception, raise others
        pass

    try:
        # search for service name
        return identity_client.services.find(name=name_type_or_id)
    except identity_exc.NotFound:
        pass
    except identity_exc.NoUniqueMatch:
        msg = _(
            "Multiple service matches found for '%s', "
            "use an ID to be more specific."
        )
        raise exceptions.CommandError(msg % name_type_or_id)

    try:
        # search for service type
        return identity_client.services.find(type=name_type_or_id)
    except identity_exc.NotFound:
        msg = _("No service with a type, name or ID of '%s' exists.")
        raise exceptions.CommandError(msg % name_type_or_id)
    except identity_exc.NoUniqueMatch:
        msg = _(
            "Multiple service matches found for '%s', "
            "use an ID to be more specific."
        )
        raise exceptions.CommandError(msg % name_type_or_id)


def find_service_sdk(identity_client, name_type_or_id):
    """Find a service by id, name or type."""

    try:
        # search for service name or ID
        return identity_client.find_service(
            name_type_or_id, ignore_missing=False
        )
    except sdk_exceptions.ResourceNotFound:
        pass
    except sdk_exceptions.DuplicateResource as e:
        raise exceptions.CommandError(e.message)

    # search for service type
    services = identity_client.services(type=name_type_or_id)
    try:
        service = next(services)
    except StopIteration:
        msg = _(
            "No service with a type, name or ID of '%(query)s' exists."
        ) % {"query": name_type_or_id}
        raise exceptions.CommandError(msg)

    if next(services, None):
        msg = _(
            "Multiple service matches found for '%(query)s', use an ID to be more specific."
        ) % {"query": name_type_or_id}
        raise exceptions.CommandError(msg)

    return service


def get_resource(manager, name_type_or_id):
    # NOTE (vishakha): Due to bug #1799153 and for any another related case
    # where GET resource API does not support the filter by name,
    # osc_lib.utils.find_resource() method cannot be used because that method
    # try to fall back to list all the resource if requested resource cannot
    # be get via name. Which ends up with NoUniqueMatch error.
    # This new function is the replacement for osc_lib.utils.find_resource()
    # for resources does not support GET by name.
    # For example: identity GET /regions.
    """Find a resource by id or name."""

    try:
        return manager.get(name_type_or_id)
    except identity_exc.NotFound:
        # raise NotFound exception
        msg = _("No resource with name or id of '%s' exists")
        raise exceptions.CommandError(msg % name_type_or_id)


def get_resource_by_id(manager, resource_id):
    """Get resource by ID

    Raises CommandError if the resource is not found
    """
    try:
        return manager.get(resource_id)
    except identity_exc.NotFound:
        msg = _("Resource with id {} not found")
        raise exceptions.CommandError(msg.format(resource_id))


def _get_token_resource(client, resource, parsed_name, parsed_domain=None):
    """Peek into the user's auth token to get resource IDs

    Look into a user's token to try and find the ID of a domain, project or
    user, when given the name. Typically non-admin users will interact with
    the CLI using names. However, by default, keystone does not allow look up
    by name since it would involve listing all entities. Instead opt to use
    the correct ID (from the token) instead.
    :param client: An identity client
    :param resource: A resource to look at in the token, this may be `domain`,
                     `project_domain`, `user_domain`, `project`, or `user`.
    :param parsed_name: This is input from parsed_args that the user is hoping
                        to find in the token.
    :param parsed_domain: This is domain filter from parsed_args that used to
                          filter the results.

    :returns: The ID of the resource from the token, or the original value from
              parsed_args if it does not match.
    """

    try:
        token = client.auth.client.get_token()
        token_data = client.tokens.get_token_data(token)
        token_dict = token_data['token']

        # NOTE(stevemar): If domain is passed, just look at the project domain.
        if resource == 'domain':
            token_dict = token_dict['project']
        obj = token_dict[resource]

        # user/project under different domain may has a same name
        if parsed_domain and parsed_domain not in obj['domain'].values():
            return parsed_name
        if isinstance(obj, list):
            for item in obj:
                if item['name'] == parsed_name:
                    return item['id']
                if item['id'] == parsed_name:
                    return parsed_name
            return parsed_name
        return obj['id'] if obj['name'] == parsed_name else parsed_name
    # diaper defense in case parsing the token fails
    except Exception:  # noqa
        return parsed_name


def find_domain(identity_client, name_or_id):
    return _find_identity_resource(
        identity_client.domains, name_or_id, domains.Domain
    )


def find_group(identity_client, name_or_id, domain_name_or_id=None):
    if domain_name_or_id is None:
        return _find_identity_resource(
            identity_client.groups, name_or_id, groups.Group
        )

    domain_id = find_domain(identity_client, domain_name_or_id).id
    return _find_identity_resource(
        identity_client.groups,
        name_or_id,
        groups.Group,
        domain_id=domain_id,
    )


def find_project(identity_client, name_or_id, domain_name_or_id=None):
    if domain_name_or_id is None:
        return _find_identity_resource(
            identity_client.projects, name_or_id, projects.Project
        )
    domain_id = find_domain(identity_client, domain_name_or_id).id
    return _find_identity_resource(
        identity_client.projects,
        name_or_id,
        projects.Project,
        domain_id=domain_id,
    )


def find_user(identity_client, name_or_id, domain_name_or_id=None):
    if domain_name_or_id is None:
        return _find_identity_resource(
            identity_client.users, name_or_id, users.User
        )
    domain_id = find_domain(identity_client, domain_name_or_id).id
    return _find_identity_resource(
        identity_client.users, name_or_id, users.User, domain_id=domain_id
    )


def _find_identity_resource(
    identity_client_manager, name_or_id, resource_type, **kwargs
):
    """Find a specific identity resource.

    Using keystoneclient's manager, attempt to find a specific resource by its
    name or ID. If Forbidden to find the resource (a common case if the user
    does not have permission), then return the resource by creating a local
    instance of keystoneclient's Resource.

    The parameter identity_client_manager is a keystoneclient manager,
    for example: keystoneclient.v3.users or keystoneclient.v3.projects.

    The parameter resource_type is a keystoneclient resource, for example:
    keystoneclient.v3.users.User or keystoneclient.v3.projects.Project.

    :param identity_client_manager: the manager that contains the resource
    :type identity_client_manager: `keystoneclient.base.CrudManager`
    :param name_or_id: the resources's name or ID
    :type name_or_id: string
    :param resource_type: class that represents the resource type
    :type resource_type: `keystoneclient.base.Resource`

    :returns: the resource in question
    :rtype: `keystoneclient.base.Resource`

    """

    try:
        identity_resource = utils.find_resource(
            identity_client_manager, name_or_id, **kwargs
        )
        if identity_resource is not None:
            return identity_resource
    except (exceptions.Forbidden, identity_exc.Forbidden):
        pass

    return resource_type(None, {'id': name_or_id, 'name': name_or_id})


def get_immutable_options(parsed_args):
    options = {}
    if parsed_args.immutable:
        options['immutable'] = True
    if parsed_args.no_immutable:
        options['immutable'] = False
    return options


def add_user_domain_option_to_parser(parser):
    parser.add_argument(
        '--user-domain',
        metavar='<user-domain>',
        help=_(
            'Domain the user belongs to (name or ID). '
            'This can be used in case collisions between user names '
            'exist.'
        ),
    )


def add_group_domain_option_to_parser(parser):
    parser.add_argument(
        '--group-domain',
        metavar='<group-domain>',
        help=_(
            'Domain the group belongs to (name or ID). '
            'This can be used in case collisions between group names '
            'exist.'
        ),
    )


def add_project_domain_option_to_parser(parser, enhance_help=lambda _h: _h):
    parser.add_argument(
        '--project-domain',
        metavar='<project-domain>',
        help=enhance_help(
            _(
                'Domain the project belongs to (name or ID). This '
                'can be used in case collisions between project '
                'names exist.'
            )
        ),
    )


def add_role_domain_option_to_parser(parser):
    parser.add_argument(
        '--role-domain',
        metavar='<role-domain>',
        help=_(
            'Domain the role belongs to (name or ID). '
            'This must be specified when the name of a domain specific '
            'role is used.'
        ),
    )


def add_inherited_option_to_parser(parser):
    parser.add_argument(
        '--inherited',
        action='store_true',
        default=False,
        help=_(
            'Specifies if the role grant is inheritable to the sub projects'
        ),
    )


def add_resource_option_to_parser(parser):
    enable_group = parser.add_mutually_exclusive_group()
    enable_group.add_argument(
        '--immutable',
        action='store_true',
        help=_(
            'Make resource immutable. An immutable project may not '
            'be deleted or modified except to remove the immutable flag'
        ),
    )
    enable_group.add_argument(
        '--no-immutable',
        action='store_true',
        help=_('Make resource mutable (default)'),
    )
