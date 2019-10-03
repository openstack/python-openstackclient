========
versions
========

Get a list of every version of every service in a given cloud.

versions show
-------------

Show service versions:

.. program:: versions show
.. code:: bash

    openstack versions show
        [--all-interfaces]
        [--interface <interface>]
        [--region-name <region-name>]
        [--service <service>]
        [--status <status>]

.. option:: --all-interfaces

    Return results for every interface of every service.
    [Mutually exclusive with --interface]

.. option:: --interface <interface>

    Limit results to only those on given interface.
    [Default 'public'. Mutually exclusive with --all-interfaces]

.. option:: --region-name <region-name>

    Limit results to only those from a given region.

.. option:: --service <service>

    Limit results to only those for service. The argument should be either
    an exact match to what is in the catalog or a known official value or
    alias from `service-types-authority`_.

.. option:: --status <status>

    Limit results to only those in the given state. Valid values are:

    - SUPPORTED
    - CURRENT
    - DEPRECATED
    - EXPERIMENTAL

.. _service-types-authority: https://service-types.openstack.org/
