=============
request token
=============

Identity v3

`Requires: OS-OAUTH1 extension`

request token authorize
-----------------------

Authorize a request token

.. program:: request token authorize
.. code:: bash

    openstack request token authorize
        --request-key <consumer-key>
        --role <role>

.. option:: --request-key <request-key>

    Request token to authorize (ID only) (required)

.. option:: --role <role>

    Roles to authorize (name or ID)
    (repeat option to set multiple values) (required)

request token create
--------------------

Create a request token

.. program:: request token create
.. code:: bash

    openstack request token create
        --consumer-key <consumer-key>
        --consumer-secret <consumer-secret>
        --project <project>
        [--domain <domain>]

.. option:: --consumer-key <consumer-key>

    Consumer key (required)

.. option:: --description <description>

    Consumer secret (required)

.. option:: --project <project>

    Project that consumer wants to access (name or ID) (required)

.. option:: --domain <domain>

    Domain owning <project> (name or ID)
