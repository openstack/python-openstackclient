=====
trust
=====

Identity v3

trust create
------------

Create new trust

.. program:: trust create
.. code:: bash

    os trust create
        --project <project>
        --role <role>
        [--impersonate]
        [--expiration <expiration>]
        [--project-domain <domain>]
        [--trustor-domain <domain>]
        [--trustee-domain <domain>]
        <trustor>
        <trustee>

.. option:: --project <project>

    Project being delegated (name or ID) (required)

.. option:: --role <role>

    Roles to authorize (name or ID) (repeat option to set multiple values, required)

.. option:: --impersonate

    Tokens generated from the trust will represent <trustor> (defaults to False)

.. option:: --expiration <expiration>

    Sets an expiration date for the trust (format of YYYY-mm-ddTHH:MM:SS)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can be
    used in case collisions between user names exist.

.. option:: --trustor-domain <trustor-domain>

    Domain that contains <trustor> (name or ID)

.. option:: --trustee-domain <trustee-domain>

    Domain that contains <trustee> (name or ID)

.. describe:: <trustor-user>

    User that is delegating authorization (name or ID)

.. describe:: <trustee-user>

    User that is assuming authorization (name or ID)


trust delete
------------

Delete trust(s)

.. program:: trust delete
.. code:: bash

    os trust delete
        <trust> [<trust> ...]

.. describe:: <trust>

    Trust(s) to delete

trust list
----------

List trusts

.. program:: trust list
.. code:: bash

    os trust list

trust show
----------

Display trust details

.. program:: trust show
.. code:: bash

    os trust show
        <trust>

.. describe:: <trust>

    Trust to display
