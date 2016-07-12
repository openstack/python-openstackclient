================
service provider
================

Identity v3

`Requires: OS-FEDERATION extension`

service provider create
-----------------------

Create new service provider

.. program:: service provider create
.. code:: bash

    os service provider create
        [--description <description>]
        [--enable | --disable]
        --auth-url <auth-url>
        --service-provider-url <sp-url>
        <name>

.. option:: --auth-url

    Authentication URL of remote federated service provider (required)

.. option:: --service-provider-url

    A service URL where SAML assertions are being sent (required)

.. option:: --description

    New service provider description

.. option:: --enable

    Enable the service provider (default)

.. option:: --disable

    Disable the service provider

.. describe:: <name>

    New service provider name (must be unique)

service provider delete
-----------------------

Delete service provider(s)

.. program:: service provider delete
.. code:: bash

    os service provider delete
        <service-provider> [<service-provider> ...]

.. describe:: <service-provider>

    Service provider(s) to delete

service provider list
---------------------

List service providers

.. program:: service provider list
.. code:: bash

    os service provider list

service provider set
--------------------

Set service provider properties

.. program:: service provider set
.. code:: bash

    os service provider set
        [--enable | --disable]
        [--description <description>]
        [--auth-url <auth-url>]
        [--service-provider-url <sp-url>]
        <service-provider>

.. option:: --service-provider-url

    New service provider URL, where SAML assertions are sent

.. option:: --auth-url

    New Authentication URL of remote federated service provider

.. option:: --description

    New service provider description

.. option:: --enable

    Enable the service provider

.. option:: --disable

    Disable the service provider

.. describe:: <service-provider>

    Service provider to modify

service provider show
---------------------

Display service provider details

.. program:: service provider show
.. code:: bash

    os service provider show
        <service-provider>

.. describe:: <service-provider>

    Service provider to display
