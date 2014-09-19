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

"""Common client utilities"""

import getpass
import logging
import os
import six
import time

from oslo.utils import importutils

from openstackclient.common import exceptions


def find_resource(manager, name_or_id):
    """Helper for the _find_* methods."""

    # Try to get entity as integer id
    try:
        if isinstance(name_or_id, int) or name_or_id.isdigit():
            return manager.get(int(name_or_id))
    except exceptions.NotFound:
        pass

    # Try directly using the passed value
    try:
        return manager.get(name_or_id)
    except Exception:
        pass

    kwargs = {}
    if 'NAME_ATTR' in manager.resource_class.__dict__:
        # novaclient does this for oddball resources
        kwargs[manager.resource_class.NAME_ATTR] = name_or_id
    else:
        kwargs['name'] = name_or_id

    # finally try to find entity by name
    try:
        return manager.find(**kwargs)
    # FIXME(dtroyer): The exception to catch here is dependent on which
    #                 client library the manager passed in belongs to.
    #                 Eventually this should be pulled from a common set
    #                 of client exceptions.
    except Exception as ex:
        if type(ex).__name__ == 'NotFound':
            msg = "No %s with a name or ID of '%s' exists." % \
                (manager.resource_class.__name__.lower(), name_or_id)
            raise exceptions.CommandError(msg)
        if type(ex).__name__ == 'NoUniqueMatch':
            msg = "More than one %s exists with the name '%s'." % \
                (manager.resource_class.__name__.lower(), name_or_id)
            raise exceptions.CommandError(msg)
        else:
            raise


def format_dict(data):
    """Return a formatted string of key value pairs

    :param data: a dict
    :param format: optional formatting hints
    :rtype: a string formatted to key='value'
    """

    output = ""
    for s in sorted(data):
        output = output + s + "='" + six.text_type(data[s]) + "', "
    return output[:-2]


def format_list(data):
    """Return a formatted strings

    :param data: a list of strings
    :rtype: a string formatted to a,b,c
    """

    return ', '.join(sorted(data))


def get_item_properties(item, fields, mixed_case_fields=[], formatters={}):
    """Return a tuple containing the item properties.

    :param item: a single item resource (e.g. Server, Project, etc)
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []

    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = getattr(item, field_name, '')
        if field in formatters:
            row.append(formatters[field](data))
        else:
            row.append(data)
    return tuple(row)


def get_dict_properties(item, fields, mixed_case_fields=[], formatters={}):
    """Return a tuple containing the item properties.

    :param item: a single dict resource
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []

    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = item[field_name] if field_name in item else ''
        if field in formatters:
            row.append(formatters[field](data))
        else:
            row.append(data)
    return tuple(row)


def string_to_bool(arg):
    return arg.strip().lower() in ('t', 'true', 'yes', '1')


def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.
    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def get_client_class(api_name, version, version_map):
    """Returns the client class for the requested API version

    :param api_name: the name of the API, e.g. 'compute', 'image', etc
    :param version: the requested API version
    :param version_map: a dict of client classes keyed by version
    :rtype: a client class for the requested API version
    """
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = "Invalid %s client version '%s'. must be one of: %s" % (
              (api_name, version, ', '.join(version_map.keys())))
        raise exceptions.UnsupportedVersion(msg)

    return importutils.import_class(client_path)


def wait_for_status(status_f,
                    res_id,
                    status_field='status',
                    success_status=['active'],
                    sleep_time=5,
                    callback=None):
    """Wait for status change on a resource during a long-running operation

    :param status_f: a status function that takes a single id argument
    :param res_id: the resource id to watch
    :param success_status: a list of status strings for successful completion
    :param status_field: the status attribute in the returned resource object
    :param sleep_time: wait this long (seconds)
    :param callback: called per sleep cycle, useful to display progress
    :rtype: True on success
    """
    while True:
        res = status_f(res_id)
        status = getattr(res, status_field, '').lower()
        if status in success_status:
            retval = True
            break
        elif status == 'error':
            retval = False
            break
        if callback:
            progress = getattr(res, 'progress', None) or 0
            callback(progress)
        time.sleep(sleep_time)
    return retval


def get_effective_log_level():
    """Returns the lowest logging level considered by logging handlers

    Retrieve an return the smallest log level set among the root
    logger's handlers (in case of multiple handlers).
    """
    root_log = logging.getLogger()
    min_log_lvl = logging.CRITICAL
    for handler in root_log.handlers:
        min_log_lvl = min(min_log_lvl, handler.level)
    return min_log_lvl


def get_password(stdin, prompt=None, confirm=True):
    message = prompt or "User Password:"
    if hasattr(stdin, 'isatty') and stdin.isatty():
        try:
            while True:
                first_pass = getpass.getpass(message)
                if not confirm:
                    return first_pass
                second_pass = getpass.getpass("Repeat " + message)
                if first_pass == second_pass:
                    return first_pass
                print("The passwords entered were not the same")
        except EOFError:  # Ctl-D
            raise exceptions.CommandError("Error reading password.")
    raise exceptions.CommandError("There was a request to be prompted for a"
                                  " password and a terminal was not detected.")


def read_blob_file_contents(blob_file):
    try:
        with open(blob_file) as file:
            blob = file.read().strip()
        return blob
    except IOError:
        msg = "Error occurred trying to read from file %s"
        raise exceptions.CommandError(msg % blob_file)
