=================
identity provider
=================

Identity v3

`Requires: OS-FEDERATION extension`

identity provider create
------------------------

Create new identity provider

.. program:: identity provider create
.. code:: bash

    os identity provider create
        [--description <description>]
        [--enable | --disable]
        <name>

.. option:: --description

    New identity provider description

.. option:: --enable

    Enable the identity provider (default)

.. option:: --disable

    Disable the identity provider

.. describe:: <name>

    New identity provider name (must be unique)

identity provider delete
------------------------

Delete identity provider

.. program:: identity provider delete
.. code:: bash

    os identity provider delete
        <identity-provider>

.. describe:: <identity-provider>

    Identity provider to delete

identity provider list
----------------------

List identity providers

.. program:: identity provider list
.. code:: bash

    os identity provider list

identity provider set
---------------------

Set identity provider properties

.. program:: identity provider set
.. code:: bash

    os identity provider set
        [--enable | --disable]
        <identity-provider>

.. option:: --enable

    Enable the identity provider

.. option:: --disable

    Disable the identity provider

.. describe:: <identity-provider>

    Identity provider to modify

identity provider show
----------------------

Display identity provider details

.. program:: identity provider show
.. code:: bash

    os identity provider show
        <identity-provider>

.. describe:: <identity-provider>

    Identity provider to display
