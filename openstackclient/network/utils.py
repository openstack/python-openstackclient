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

from osc_lib import exceptions

from openstackclient.i18n import _


# Transform compute security group rule for display.
def transform_compute_security_group_rule(sg_rule):
    info = {}
    info.update(sg_rule)
    from_port = info.pop('from_port')
    to_port = info.pop('to_port')
    if isinstance(from_port, int) and isinstance(to_port, int):
        port_range = {'port_range': f"{from_port}:{to_port}"}
    elif from_port is None and to_port is None:
        port_range = {'port_range': ""}
    else:
        port_range = {'port_range': f"{from_port}:{to_port}"}
    info.update(port_range)
    if 'cidr' in info['ip_range']:
        info['ip_range'] = info['ip_range']['cidr']
    else:
        info['ip_range'] = ''
    if info['ip_protocol'] is None:
        info['ip_protocol'] = ''
    elif info['ip_protocol'].lower() == 'icmp':
        info['port_range'] = ''
    group = info.pop('group')
    if 'name' in group:
        info['remote_security_group'] = group['name']
    else:
        info['remote_security_group'] = ''
    return info


def str2bool(strbool):
    if strbool is None:
        return None
    return strbool.lower() == 'true'


def str2list(strlist):
    result = []
    if strlist:
        result = strlist.split(';')
    return result


def str2dict(strdict: str) -> dict[str, str]:
    """Convert key1:value1;key2:value2;... string into dictionary.

    :param strdict: string in the form of key1:value1;key2:value2
    """
    result: dict[str, str] = {}
    if not strdict:
        return result
    i = 0
    kvlist = []
    for kv in strdict.split(';'):
        if ':' in kv:
            kvlist.append(kv)
            i += 1
        elif i == 0:
            msg = _("missing value for key '%s'")
            raise exceptions.CommandError(msg % kv)
        else:
            kvlist[i - 1] = f"{kvlist[i - 1]};{kv}"
    for kv in kvlist:
        key, sep, value = kv.partition(':')
        result[key] = value
    return result


def format_security_group_rule_show(obj):
    data = transform_compute_security_group_rule(obj)
    return zip(*sorted(data.items()))


def format_network_port_range(rule):
    # Display port range or ICMP type and code. For example:
    # - ICMP type: 'type=3'
    # - ICMP type and code: 'type=3:code=0'
    # - ICMP code: Not supported
    # - Matching port range: '443:443'
    # - Different port range: '22:24'
    # - Single port: '80:80'
    # - No port range: ''
    port_range = ''
    if is_icmp_protocol(rule['protocol']):
        if rule['port_range_min']:
            port_range += 'type=' + str(rule['port_range_min'])
        if rule['port_range_max']:
            port_range += ':code=' + str(rule['port_range_max'])
    elif rule['port_range_min'] or rule['port_range_max']:
        port_range_min = str(rule['port_range_min'])
        port_range_max = str(rule['port_range_max'])
        if rule['port_range_min'] is None:
            port_range_min = port_range_max
        if rule['port_range_max'] is None:
            port_range_max = port_range_min
        port_range = port_range_min + ':' + port_range_max
    return port_range


def format_remote_ip_prefix(rule):
    remote_ip_prefix = rule['remote_ip_prefix']
    if remote_ip_prefix is None:
        ethertype = rule['ether_type']
        if ethertype == 'IPv4':
            remote_ip_prefix = '0.0.0.0/0'
        elif ethertype == 'IPv6':
            remote_ip_prefix = '::/0'
    return remote_ip_prefix


def convert_ipvx_case(string):
    if string.lower() == 'ipv4':
        return 'IPv4'
    if string.lower() == 'ipv6':
        return 'IPv6'
    return string


def is_icmp_protocol(protocol):
    # NOTE(rtheis): Neutron has deprecated protocol icmpv6.
    # However, while the OSC CLI doesn't document the protocol,
    # the code must still handle it. In addition, handle both
    # protocol names and numbers.
    if protocol in ['icmp', 'icmpv6', 'ipv6-icmp', '1', '58']:
        return True
    else:
        return False


def convert_to_lowercase(string):
    return string.lower()


def get_protocol(parsed_args, default_protocol='any'):
    protocol = default_protocol
    if parsed_args.protocol is not None:
        protocol = parsed_args.protocol
    if hasattr(parsed_args, "proto") and parsed_args.proto is not None:
        protocol = parsed_args.proto
    if protocol == 'any':
        protocol = None
    return protocol


def get_ethertype(parsed_args, protocol):
    ethertype = 'IPv4'
    if parsed_args.ethertype is not None:
        ethertype = parsed_args.ethertype
    elif is_ipv6_protocol(protocol):
        ethertype = 'IPv6'
    return ethertype


def is_ipv6_protocol(protocol):
    # NOTE(rtheis): Neutron has deprecated protocol icmpv6.
    # However, while the OSC CLI doesn't document the protocol,
    # the code must still handle it. In addition, handle both
    # protocol names and numbers.
    if (
        protocol is not None
        and protocol.startswith('ipv6-')
        or protocol in ['icmpv6', '41', '43', '44', '58', '59', '60']
    ):
        return True
    else:
        return False
