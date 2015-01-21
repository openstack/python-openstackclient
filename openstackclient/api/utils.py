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

"""API Utilities Library"""


def simple_filter(
    data=None,
    attr=None,
    value=None,
    property_field=None,
):
    """Filter a list of dicts

    :param list data:
        The list to be filtered.  The list is modified in-place and will
        be changed if any filtering occurs.
    :param string attr:
        The name of the attribute to filter.  If attr does not exist no
        match will succeed and no rows will be retrurned.  If attr is
        None no filtering will be performed and all rows will be returned.
    :param sring value:
        The value to filter.  None is considered to be a 'no filter' value.
        '' matches agains a Python empty string.
    :param string property_field:
        The name of the data field containing a property dict to filter.
        If property_field is None, attr is a field name. If property_field
        is not None, attr is a property key name inside the named property
        field.

    :returns:
        Returns the filtered list
    :rtype list:

    This simple filter (one attribute, one exact-match value) searches a
    list of dicts to select items.  It first searches the item dict for a
    matching ``attr`` then does an exact-match on the ``value``.  If
    ``property_field`` is given, it will look inside that field (if it
    exists and is a dict) for a matching ``value``.
    """

    # Take the do-nothing case shortcut
    if not data or not attr or value is None:
        return data

    # NOTE:(dtroyer): This filter modifies the provided list in-place using
    # list.remove() so we need to start at the end so the loop pointer does
    # not skip any items after a deletion.
    for d in reversed(data):
        if attr in d:
            # Searching data fields
            search_value = d[attr]
        elif (property_field and property_field in d and
                type(d[property_field]) is dict):
            # Searching a properties field - do this separately because
            # we don't want to fail over to checking the fields if a
            # property name is given.
            if attr in d[property_field]:
                search_value = d[property_field][attr]
            else:
                search_value = None
        else:
            search_value = None

        # could do regex here someday...
        if not search_value or search_value != value:
            # remove from list
            try:
                data.remove(d)
            except ValueError:
                # it's already gone!
                pass

    return data
