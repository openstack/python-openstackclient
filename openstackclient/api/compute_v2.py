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

"""Compute v2 API Library

A collection of wrappers for deprecated Compute v2 APIs that are not
intentionally supported by SDK. Most of these are proxy APIs.
"""

import http

from openstack import exceptions as sdk_exceptions
from osc_lib import exceptions


# security groups


def create_security_group(compute_client, name=None, description=None):
    """Create a new security group

    https://docs.openstack.org/api-ref/compute/#create-security-group

    :param compute_client: A compute client
    :param str name: Security group name
    :param str description: Security group description
    :returns: A security group object
    """
    data = {
        'name': name,
        'description': description,
    }
    response = compute_client.post(
        '/os-security-groups', data=data, microversion='2.1'
    )
    sdk_exceptions.raise_from_response(response)
    return response.json()['security_group']


def list_security_groups(compute_client, all_projects=None):
    """Get all security groups

    https://docs.openstack.org/api-ref/compute/#list-security-groups

    :param compute_client: A compute client
    :param bool all_projects: If true, list from all projects
    :returns: A list of security group objects
    """
    url = '/os-security-groups'
    if all_projects is not None:
        url += f'?all_tenants={all_projects}'
    response = compute_client.get(url, microversion='2.1')
    sdk_exceptions.raise_from_response(response)
    return response.json()['security_groups']


def find_security_group(compute_client, name_or_id):
    """Find the name for a given security group name or ID

    https://docs.openstack.org/api-ref/compute/#show-security-group-details

    :param compute_client: A compute client
    :param name_or_id: The name or ID of the security group to look up
    :returns: A security group object
    :raises exception.NotFound: If a matching security group could not be
        found or more than one match was found
    """
    response = compute_client.get(
        f'/os-security-groups/{name_or_id}', microversion='2.1'
    )
    if response.status_code != http.HTTPStatus.NOT_FOUND:
        # there might be other, non-404 errors
        sdk_exceptions.raise_from_response(response)
        return response.json()['security_group']

    response = compute_client.get('/os-security-groups', microversion='2.1')
    sdk_exceptions.raise_from_response(response)
    found = None
    security_groups = response.json()['security_groups']
    for security_group in security_groups:
        if security_group['name'] == name_or_id:
            if found:
                raise exceptions.NotFound(
                    f'multiple matches found for {name_or_id}'
                )
            found = security_group

    if not found:
        raise exceptions.NotFound(f'{name_or_id} not found')

    return found


def update_security_group(
    compute_client, security_group_id, name=None, description=None
):
    """Update an existing security group

    https://docs.openstack.org/api-ref/compute/#update-security-group

    :param compute_client: A compute client
    :param str security_group_id: The ID of the security group to update
    :param str name: Security group name
    :param str description: Security group description
    :returns: A security group object
    """
    data = {}
    if name:
        data['name'] = name
    if description:
        data['description'] = description
    response = compute_client.put(
        f'/os-security-groups/{security_group_id}',
        data=data,
        microversion='2.1',
    )
    sdk_exceptions.raise_from_response(response)
    return response.json()['security_group']


def delete_security_group(compute_client, security_group_id=None):
    """Delete a security group

    https://docs.openstack.org/api-ref/compute/#delete-security-group

    :param compute_client: A compute client
    :param str security_group_id: Security group ID
    :returns: None
    """
    response = compute_client.delete(
        f'/os-security-groups/{security_group_id}', microversion='2.1'
    )
    sdk_exceptions.raise_from_response(response)


# security group rules


def create_security_group_rule(
    compute_client,
    security_group_id=None,
    ip_protocol=None,
    from_port=None,
    to_port=None,
    remote_ip=None,
    remote_group=None,
):
    """Create a new security group rule

    https://docs.openstack.org/api-ref/compute/#create-security-group-rule

    :param compute_client: A compute client
    :param str security_group_id: Security group ID
    :param str ip_protocol: IP protocol, 'tcp', 'udp' or 'icmp'
    :param int from_port: Source port
    :param int to_port: Destination port
    :param str remote_ip: Source IP address in CIDR notation
    :param str remote_group: Remote security group
    :returns: A security group object
    """
    data = {
        'parent_group_id': security_group_id,
        'ip_protocol': ip_protocol,
        'from_port': from_port,
        'to_port': to_port,
        'cidr': remote_ip,
        'group_id': remote_group,
    }
    response = compute_client.post(
        '/os-security-group-rules', data=data, microversion='2.1'
    )
    sdk_exceptions.raise_from_response(response)
    return response.json()['security_group_rule']


def delete_security_group_rule(compute_client, security_group_rule_id=None):
    """Delete a security group rule

    https://docs.openstack.org/api-ref/compute/#delete-security-group-rule

    :param compute_client: A compute client
    :param str security_group_rule_id: Security group rule ID
    :returns: None
    """
    response = compute_client.delete(
        f'/os-security-group-rules/{security_group_rule_id}',
        microversion='2.1',
    )
    sdk_exceptions.raise_from_response(response)


# networks


def create_network(compute_client, name, subnet, share_subnet=None):
    """Create a new network

    https://docs.openstack.org/api-ref/compute/#create-network

    :param compute_client: A compute client
    :param str name: Network label
    :param int subnet: Subnet for IPv4 fixed addresses in CIDR notation
    :param bool share_subnet: Shared subnet between projects
    :returns: A network object
    """
    data = {
        'label': name,
        'cidr': subnet,
    }
    if share_subnet is not None:
        data['share_address'] = share_subnet

    response = compute_client.post(
        '/os-networks', data=data, microversion='2.1'
    )
    sdk_exceptions.raise_from_response(response)
    return response.json()['network']


def list_networks(compute_client):
    """Get all networks

    https://docs.openstack.org/api-ref/compute/#list-networks

    :param compute_client: A compute client
    :returns: A list of network objects
    """
    response = compute_client.get('/os-networks', microversion='2.1')
    sdk_exceptions.raise_from_response(response)
    return response.json()['networks']


def find_network(compute_client, name_or_id):
    """Find the ID for a given network name or ID

    https://docs.openstack.org/api-ref/compute/#show-network-details

    :param compute_client: A compute client
    :param name_or_id: The name or ID of the network to look up
    :returns: A network object
    :raises exception.NotFound: If a matching network could not be found or
        more than one match was found
    """
    response = compute_client.get(
        f'/os-networks/{name_or_id}', microversion='2.1'
    )
    if response.status_code != http.HTTPStatus.NOT_FOUND:
        # there might be other, non-404 errors
        sdk_exceptions.raise_from_response(response)
        return response.json()['network']

    response = compute_client.get('/os-networks', microversion='2.1')
    sdk_exceptions.raise_from_response(response)
    found = None
    networks = response.json()['networks']
    for network in networks:
        if network['label'] == name_or_id:
            if found:
                raise exceptions.NotFound(
                    f'multiple matches found for {name_or_id}'
                )
            found = network

    if not found:
        raise exceptions.NotFound(f'{name_or_id} not found')

    return found


def delete_network(compute_client, network_id):
    """Delete a network

    https://docs.openstack.org/api-ref/compute/#delete-network

    :param compute_client: A compute client
    :param string network_id: The network ID
    :returns: None
    """
    response = compute_client.delete(
        f'/os-networks/{network_id}', microversion='2.1'
    )
    sdk_exceptions.raise_from_response(response)


# floating ips


def create_floating_ip(compute_client, network):
    """Create a new floating ip

    https://docs.openstack.org/api-ref/compute/#create-allocate-floating-ip-address

    :param network: Name of floating IP pool
    :returns: A floating IP object
    """
    response = compute_client.post(
        '/os-floating-ips', data={'pool': network}, microversion='2.1'
    )
    sdk_exceptions.raise_from_response(response)
    return response.json()['floating_ip']


def list_floating_ips(compute_client):
    """Get all floating IPs

    https://docs.openstack.org/api-ref/compute/#list-floating-ip-addresses

    :returns: A list of floating IP objects
    """
    response = compute_client.get('/os-floating-ips', microversion='2.1')
    sdk_exceptions.raise_from_response(response)
    return response.json()['floating_ips']


def get_floating_ip(compute_client, floating_ip_id):
    """Get a floating IP

    https://docs.openstack.org/api-ref/compute/#show-floating-ip-address-details

    :param string floating_ip_id: The floating IP address
    :returns: A floating IP object
    """
    response = compute_client.get(
        f'/os-floating-ips/{floating_ip_id}', microversion='2.1'
    )
    sdk_exceptions.raise_from_response(response)
    return response.json()['floating_ip']


def delete_floating_ip(compute_client, floating_ip_id):
    """Delete a floating IP

    https://docs.openstack.org/api-ref/compute/#delete-deallocate-floating-ip-address

    :param string floating_ip_id: The floating IP address
    :returns: None
    """
    response = compute_client.delete(
        f'/os-floating-ips/{floating_ip_id}', microversion='2.1'
    )
    sdk_exceptions.raise_from_response(response)


# floating ip pools


def list_floating_ip_pools(compute_client):
    """Get all floating IP pools

    https://docs.openstack.org/api-ref/compute/#list-floating-ip-pools

    :param compute_client: A compute client
    :returns: A list of floating IP pool objects
    """
    response = compute_client.get('/os-floating-ip-pools', microversion='2.1')
    sdk_exceptions.raise_from_response(response)

    return response.json()['floating_ip_pools']
