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
        port_range = {'port_range': "%u:%u" % (from_port, to_port)}
    elif from_port is None and to_port is None:
        port_range = {'port_range': ""}
    else:
        port_range = {'port_range': "%s:%s" % (from_port, to_port)}
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


def str2dict(strdict):
    """Convert key1:value1;key2:value2;... string into dictionary.

    :param strdict: string in the form of key1:value1;key2:value2
    """
    result = {}
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
            kvlist[i - 1] = "%s;%s" % (kvlist[i - 1], kv)
    for kv in kvlist:
        key, sep, value = kv.partition(':')
        result[key] = value
    return result
