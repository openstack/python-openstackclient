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
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


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
        msg = _("Multiple service matches found for '%s', "
                "use an ID to be more specific.")
        raise exceptions.CommandError(msg % name_type_or_id)

    try:
        # search for service type
        return identity_client.services.find(type=name_type_or_id)
    except identity_exc.NotFound:
        msg = _("No service with a type, name or ID of '%s' exists.")
        raise exceptions.CommandError(msg % name_type_or_id)
    except identity_exc.NoUniqueMatch:
        msg = _("Multiple service matches found for '%s', "
                "use an ID to be more specific.")
        raise exceptions.CommandError(msg % name_type_or_id)


def _get_token_resource(client, resource, parsed_name):
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
        return obj['id'] if obj['name'] == parsed_name else parsed_name
    # diaper defense in case parsing the token fails
    except Exception:  # noqa
        return parsed_name


def _get_domain_id_if_requested(identity_client, domain_name_or_id):
    if not domain_name_or_id:
        return None
    domain = find_domain(identity_client, domain_name_or_id)
    return domain.id


def find_domain(identity_client, name_or_id):
    return _find_identity_resource(identity_client.domains, name_or_id,
                                   domains.Domain)


def find_group(identity_client, name_or_id, domain_name_or_id=None):
    domain_id = _get_domain_id_if_requested(identity_client, domain_name_or_id)
    if not domain_id:
        return _find_identity_resource(identity_client.groups, name_or_id,
                                       groups.Group)
    else:
        return _find_identity_resource(identity_client.groups, name_or_id,
                                       groups.Group, domain_id=domain_id)


def find_project(identity_client, name_or_id, domain_name_or_id=None):
    domain_id = _get_domain_id_if_requested(identity_client, domain_name_or_id)
    if not domain_id:
        return _find_identity_resource(identity_client.projects, name_or_id,
                                       projects.Project)
    else:
        return _find_identity_resource(identity_client.projects, name_or_id,
                                       projects.Project, domain_id=domain_id)


def find_user(identity_client, name_or_id, domain_name_or_id=None):
    domain_id = _get_domain_id_if_requested(identity_client, domain_name_or_id)
    if not domain_id:
        return _find_identity_resource(identity_client.users, name_or_id,
                                       users.User)
    else:
        return _find_identity_resource(identity_client.users, name_or_id,
                                       users.User, domain_id=domain_id)


def _find_identity_resource(identity_client_manager, name_or_id,
                            resource_type, **kwargs):
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
        identity_resource = utils.find_resource(identity_client_manager,
                                                name_or_id, **kwargs)
        if identity_resource is not None:
            return identity_resource
    except identity_exc.Forbidden:
        pass

    return resource_type(None, {'id': name_or_id, 'name': name_or_id})


def add_user_domain_option_to_parser(parser):
    parser.add_argument(
        '--user-domain',
        metavar='<user-domain>',
        help=_('Domain the user belongs to (name or ID). '
               'This can be used in case collisions between user names '
               'exist.'),
    )


def add_group_domain_option_to_parser(parser):
    parser.add_argument(
        '--group-domain',
        metavar='<group-domain>',
        help=_('Domain the group belongs to (name or ID). '
               'This can be used in case collisions between group names '
               'exist.'),
    )


def add_project_domain_option_to_parser(parser):
    parser.add_argument(
        '--project-domain',
        metavar='<project-domain>',
        help=_('Domain the project belongs to (name or ID). '
               'This can be used in case collisions between project names '
               'exist.'),
    )


def add_role_domain_option_to_parser(parser):
    parser.add_argument(
        '--role-domain',
        metavar='<role-domain>',
        help=_('Domain the role belongs to (name or ID). '
               'This must be specified when the name of a domain specific '
               'role is used.'),
    )


def add_inherited_option_to_parser(parser):
    parser.add_argument(
        '--inherited',
        action='store_true',
        default=False,
        help=_('Specifies if the role grant is inheritable to the sub '
               'projects'),
    )
