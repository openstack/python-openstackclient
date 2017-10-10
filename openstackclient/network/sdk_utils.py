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

import six


def get_osc_show_columns_for_sdk_resource(
    sdk_resource,
    osc_column_map,
    invisible_columns=None
):
    """Get and filter the display and attribute columns for an SDK resource.

    Common utility function for preparing the output of an OSC show command.
    Some of the columns may need to get renamed, others made invisible.

    :param sdk_resource: An SDK resource
    :param osc_column_map: A hash of mappings for display column names
    :param invisible_columns: A list of invisible column names

    :returns: Two tuples containing the names of the display and attribute
              columns
    """

    if getattr(sdk_resource, 'allow_get', None) is not None:
        resource_dict = sdk_resource.to_dict(
            body=True, headers=False, ignore_none=False)
    else:
        resource_dict = sdk_resource

    # Build the OSC column names to display for the SDK resource.
    attr_map = {}
    display_columns = list(resource_dict.keys())
    invisible_columns = [] if invisible_columns is None else invisible_columns
    for col_name in invisible_columns:
        if col_name in display_columns:
            display_columns.remove(col_name)
    for sdk_attr, osc_attr in six.iteritems(osc_column_map):
        if sdk_attr in display_columns:
            attr_map[osc_attr] = sdk_attr
            display_columns.remove(sdk_attr)
        if osc_attr not in display_columns:
            display_columns.append(osc_attr)
    sorted_display_columns = sorted(display_columns)

    # Build the SDK attribute names for the OSC column names.
    attr_columns = []
    for column in sorted_display_columns:
        new_column = attr_map[column] if column in attr_map else column
        attr_columns.append(new_column)
    return tuple(sorted_display_columns), tuple(attr_columns)
