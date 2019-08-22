======================
application credential
======================

Identity v3

With application credentials, a user can grant their applications limited
access to their cloud resources. Once created, users can authenticate with an
application credential by using the ``v3applicationcredential`` auth type.

application credential create
-----------------------------

Create new application credential

.. program:: application credential create
.. code:: bash

    openstack application credential create
        [--secret <secret>]
        [--role <role>]
        [--expiration <expiration>]
        [--description <description>]
        [--restricted|--unrestricted]
        [--access-rules <access-rules>]
        <name>

.. option:: --secret <secret>

    Secret to use for authentication (if not provided, one will be generated)

.. option:: --role <role>

    Roles to authorize (name or ID) (repeat option to set multiple values)

.. option:: --expiration <expiration>

    Sets an expiration date for the application credential (format of
    YYYY-mm-ddTHH:MM:SS)

.. option:: --description <description>

    Application credential description

.. option:: --unrestricted

    Enable application credential to create and delete other application
    credentials and trusts (this is potentially dangerous behavior and is
    disabled by default)

.. option:: --restricted

    Prohibit application credential from creating and deleting other
    application credentials and trusts (this is the default behavior)

.. option:: --access-rules

   Either a string or file path containing a JSON-formatted list of access
   rules, each containing a request method, path, and service, for example
   '[{"method": "GET", "path": "/v2.1/servers", "service": "compute"}]'

.. describe:: <name>

    Name of the application credential


application credential delete
-----------------------------

Delete application credential(s)

.. program:: application credential delete
.. code:: bash

    openstack application credential delete
        <application-credential> [<application-credential> ...]

.. describe:: <application-credential>

    Application credential(s) to delete (name or ID)

application credential list
---------------------------

List application credentials

.. program:: application credential list
.. code:: bash

    openstack application credential list
        [--user <user>]
        [--user-domain <user-domain>]

.. option:: --user

    User whose application credentials to list (name or ID)

.. option:: --user-domain

    Domain the user belongs to (name or ID). This can be
    used in case collisions between user names exist.

application credential show
---------------------------

Display application credential details

.. program:: application credential show
.. code:: bash

    openstack application credential show
        <application-credential>

.. describe:: <application-credential>

    Application credential to display (name or ID)
