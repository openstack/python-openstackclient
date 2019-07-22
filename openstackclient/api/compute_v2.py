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

"""Compute v2 API Library"""

from keystoneauth1 import exceptions as ksa_exceptions
from osc_lib.api import api
from osc_lib import exceptions
from osc_lib.i18n import _


# TODO(dtroyer): Mingrate this to osc-lib
class InvalidValue(Exception):
    """An argument value is not valid: wrong type, out of range, etc"""
    message = "Supplied value is not valid"


class APIv2(api.BaseAPI):
    """Compute v2 API"""

    def __init__(self, **kwargs):
        super(APIv2, self).__init__(**kwargs)

    # Overrides

    def _check_integer(self, value, msg=None):
        """Attempt to convert value to an integer

        Raises InvalidValue on failure

        :param value:
            Convert this to an integer.  None is converted to 0 (zero).
        :param msg:
            An alternate message for the exception, must include exactly
            one substitution to receive the attempted value.
        """

        if value is None:
            return 0

        try:
            value = int(value)
        except (TypeError, ValueError):
            if not msg:
                msg = _("%s is not an integer") % value
            raise InvalidValue(msg)
        return value

    # TODO(dtroyer): Override find() until these fixes get into an osc-lib
    #                minimum release
    def find(
        self,
        path,
        value=None,
        attr=None,
    ):
        """Find a single resource by name or ID

        :param string path:
            The API-specific portion of the URL path
        :param string value:
            search expression (required, really)
        :param string attr:
            name of attribute for secondary search
        """

        try:
            ret = self._request('GET', "/%s/%s" % (path, value)).json()
            if isinstance(ret, dict):
                # strip off the enclosing dict
                key = list(ret.keys())[0]
                ret = ret[key]
        except (
            ksa_exceptions.NotFound,
            ksa_exceptions.BadRequest,
        ):
            kwargs = {attr: value}
            try:
                ret = self.find_one(path, **kwargs)
            except ksa_exceptions.NotFound:
                msg = _("%s not found") % value
                raise exceptions.NotFound(msg)

        return ret

    # Floating IPs

    def floating_ip_add(
        self,
        server,
        address,
        fixed_address=None,
    ):
        """Add a floating IP to a server

        :param server:
            The :class:`Server` (or its ID) to add an IP to.
        :param address:
            The FloatingIP or string floating address to add.
        :param fixed_address:
            The FixedIP the floatingIP should be associated with (optional)
        """

        url = '/servers'

        server = self.find(
            url,
            attr='name',
            value=server,
        )

        address = address.ip if hasattr(address, 'ip') else address
        if fixed_address:
            if hasattr(fixed_address, 'ip'):
                fixed_address = fixed_address.ip

            body = {
                'address': address,
                'fixed_address': fixed_address,
            }
        else:
            body = {
                'address': address,
            }

        return self._request(
            "POST",
            "/%s/%s/action" % (url, server['id']),
            json={'addFloatingIp': body},
        )

    def floating_ip_create(
        self,
        pool=None,
    ):
        """Create a new floating ip

        https://docs.openstack.org/api-ref/compute/#create-allocate-floating-ip-address

        :param pool: Name of floating IP pool
        """

        url = "/os-floating-ips"

        try:
            return self.create(
                url,
                json={'pool': pool},
            )['floating_ip']
        except (
            ksa_exceptions.NotFound,
            ksa_exceptions.BadRequest,
        ):
            msg = _("%s not found") % pool
            raise exceptions.NotFound(msg)

    def floating_ip_delete(
        self,
        floating_ip_id=None,
    ):
        """Delete a floating IP

        https://docs.openstack.org/api-ref/compute/#delete-deallocate-floating-ip-address

        :param string floating_ip_id:
            Floating IP ID
        """

        url = "/os-floating-ips"

        if floating_ip_id is not None:
            return self.delete('/%s/%s' % (url, floating_ip_id))

        return None

    def floating_ip_find(
        self,
        floating_ip=None,
    ):
        """Return a security group given name or ID

        https://docs.openstack.org/api-ref/compute/#list-floating-ip-addresses

        :param string floating_ip:
            Floating IP address
        :returns: A dict of the floating IP attributes
        """

        url = "/os-floating-ips"

        return self.find(
            url,
            attr='ip',
            value=floating_ip,
        )

    def floating_ip_list(
        self,
    ):
        """Get floating IPs

        https://docs.openstack.org/api-ref/compute/#show-floating-ip-address-details

        :returns:
            list of floating IPs
        """

        url = "/os-floating-ips"

        return self.list(url)["floating_ips"]

    def floating_ip_remove(
        self,
        server,
        address,
    ):
        """Remove a floating IP from a server

        :param server:
            The :class:`Server` (or its ID) to add an IP to.
        :param address:
            The FloatingIP or string floating address to add.
        """

        url = '/servers'

        server = self.find(
            url,
            attr='name',
            value=server,
        )

        address = address.ip if hasattr(address, 'ip') else address
        body = {
            'address': address,
        }

        return self._request(
            "POST",
            "/%s/%s/action" % (url, server['id']),
            json={'removeFloatingIp': body},
        )

    # Floating IP Pools

    def floating_ip_pool_list(
        self,
    ):
        """Get floating IP pools

        https://docs.openstack.org/api-ref/compute/?expanded=#list-floating-ip-pools

        :returns:
            list of floating IP pools
        """

        url = "/os-floating-ip-pools"

        return self.list(url)["floating_ip_pools"]

    # Hosts

    def host_list(
        self,
        zone=None,
    ):
        """Lists hypervisor Hosts

        https://docs.openstack.org/api-ref/compute/#list-hosts
        Valid for Compute 2.0 - 2.42

        :param string zone:
            Availability zone
        :returns: A dict of the floating IP attributes
        """

        url = "/os-hosts"
        if zone:
            url = '/os-hosts?zone=%s' % zone

        return self.list(url)["hosts"]

    def host_set(
        self,
        host=None,
        status=None,
        maintenance_mode=None,
        **params
    ):
        """Modify host properties

        https://docs.openstack.org/api-ref/compute/#update-host-status
        Valid for Compute 2.0 - 2.42

        status
        maintenance_mode
        """

        url = "/os-hosts"

        params = {}
        if status:
            params['status'] = status
        if maintenance_mode:
            params['maintenance_mode'] = maintenance_mode
        if params == {}:
            # Don't bother calling if nothing given
            return None
        else:
            return self._request(
                "PUT",
                "/%s/%s" % (url, host),
                json=params,
            ).json()

    def host_show(
        self,
        host=None,
    ):
        """Show host

        https://docs.openstack.org/api-ref/compute/#show-host-details
        Valid for Compute 2.0 - 2.42
        """

        url = "/os-hosts"

        r_host = self.find(
            url,
            attr='host_name',
            value=host,
        )

        data = []
        for h in r_host:
            data.append(h['resource'])
        return data

    # Networks

    def network_create(
        self,
        name=None,
        subnet=None,
        share_subnet=None,
    ):
        """Create a new network

        https://docs.openstack.org/api-ref/compute/#create-network

        :param string name:
            Network label (required)
        :param integer subnet:
            Subnet for IPv4 fixed addresses in CIDR notation (required)
        :param integer share_subnet:
            Shared subnet between projects, True or False
        :returns: A dict of the network attributes
        """

        url = "/os-networks"

        params = {
            'label': name,
            'cidr': subnet,
        }
        if share_subnet is not None:
            params['share_address'] = share_subnet

        return self.create(
            url,
            json={'network': params},
        )['network']

    def network_delete(
        self,
        network=None,
    ):
        """Delete a network

        https://docs.openstack.org/api-ref/compute/#delete-network

        :param string network:
            Network name or ID
        """

        url = "/os-networks"

        network = self.find(
            url,
            attr='label',
            value=network,
        )['id']
        if network is not None:
            return self.delete('/%s/%s' % (url, network))

        return None

    def network_find(
        self,
        network=None,
    ):
        """Return a network given name or ID

        https://docs.openstack.org/api-ref/compute/#show-network-details

        :param string network:
            Network name or ID
        :returns: A dict of the network attributes
        """

        url = "/os-networks"

        return self.find(
            url,
            attr='label',
            value=network,
        )

    def network_list(
        self,
    ):
        """Get networks

        https://docs.openstack.org/api-ref/compute/#list-networks

        :returns:
            list of networks
        """

        url = "/os-networks"

        return self.list(url)["networks"]

    # Security Groups

    def security_group_create(
        self,
        name=None,
        description=None,
    ):
        """Create a new security group

        https://docs.openstack.org/api-ref/compute/#create-security-group

        :param string name:
            Security group name
        :param integer description:
            Security group description
        """

        url = "/os-security-groups"

        params = {
            'name': name,
            'description': description,
        }

        return self.create(
            url,
            json={'security_group': params},
        )['security_group']

    def security_group_delete(
        self,
        security_group=None,
    ):
        """Delete a security group

        https://docs.openstack.org/api-ref/compute/#delete-security-group

        :param string security_group:
            Security group name or ID
        """

        url = "/os-security-groups"

        security_group = self.find(
            url,
            attr='name',
            value=security_group,
        )['id']
        if security_group is not None:
            return self.delete('/%s/%s' % (url, security_group))

        return None

    def security_group_find(
        self,
        security_group=None,
    ):
        """Return a security group given name or ID

        https://docs.openstack.org/api-ref/compute/#show-security-group-details

        :param string security_group:
            Security group name or ID
        :returns: A dict of the security group attributes
        """

        url = "/os-security-groups"

        return self.find(
            url,
            attr='name',
            value=security_group,
        )

    def security_group_list(
        self,
        limit=None,
        marker=None,
        search_opts=None,
    ):
        """Get security groups

        https://docs.openstack.org/api-ref/compute/#list-security-groups

        :param integer limit:
            query return count limit
        :param string marker:
            query marker
        :param search_opts:
            (undocumented) Search filter dict
            all_tenants: True|False - return all projects
        :returns:
            list of security groups names
        """

        params = {}
        if search_opts is not None:
            params = dict((k, v) for (k, v) in search_opts.items() if v)
        if limit:
            params['limit'] = limit
        if marker:
            params['offset'] = marker

        url = "/os-security-groups"
        return self.list(url, **params)["security_groups"]

    def security_group_set(
        self,
        security_group=None,
        # name=None,
        # description=None,
        **params
    ):
        """Update a security group

        https://docs.openstack.org/api-ref/compute/#update-security-group

        :param string security_group:
            Security group name or ID

        TODO(dtroyer): Create an update method in osc-lib
        """

        # Short-circuit no-op
        if params is None:
            return None

        url = "/os-security-groups"

        security_group = self.find(
            url,
            attr='name',
            value=security_group,
        )
        if security_group is not None:
            for (k, v) in params.items():
                # Only set a value if it is already present
                if k in security_group:
                    security_group[k] = v
            return self._request(
                "PUT",
                "/%s/%s" % (url, security_group['id']),
                json={'security_group': security_group},
            ).json()['security_group']
        return None

    # Security Group Rules

    def security_group_rule_create(
        self,
        security_group_id=None,
        ip_protocol=None,
        from_port=None,
        to_port=None,
        remote_ip=None,
        remote_group=None,
    ):
        """Create a new security group rule

        https://docs.openstack.org/api-ref/compute/#create-security-group-rule

        :param string security_group_id:
            Security group ID
        :param ip_protocol:
            IP protocol, 'tcp', 'udp' or 'icmp'
        :param from_port:
            Source port
        :param to_port:
            Destination port
        :param remote_ip:
            Source IP address in CIDR notation
        :param remote_group:
            Remote security group
        """

        url = "/os-security-group-rules"

        if ip_protocol.lower() not in ['icmp', 'tcp', 'udp']:
            raise InvalidValue(
                "%(s) is not one of 'icmp', 'tcp', or 'udp'" % ip_protocol
            )

        params = {
            'parent_group_id': security_group_id,
            'ip_protocol': ip_protocol,
            'from_port': self._check_integer(from_port),
            'to_port': self._check_integer(to_port),
            'cidr': remote_ip,
            'group_id': remote_group,
        }

        return self.create(
            url,
            json={'security_group_rule': params},
        )['security_group_rule']

    def security_group_rule_delete(
        self,
        security_group_rule_id=None,
    ):
        """Delete a security group rule

        https://docs.openstack.org/api-ref/compute/#delete-security-group-rule

        :param string security_group_rule_id:
            Security group rule ID
        """

        url = "/os-security-group-rules"
        if security_group_rule_id is not None:
            return self.delete('/%s/%s' % (url, security_group_rule_id))

        return None
