======
domain
======

Identity v3

domain create
-------------

Create new domain

.. program:: domain create
.. code:: bash

    os domain create
        [--description <description>]
        [--enable | --disable]
        [--or-show]
        <domain-name>

.. option:: --description <description>

    New domain description

.. option:: --enable

    Enable domain (default)

.. option:: --disable

    Disable domain

.. option:: --or-show

    Return existing domain

    If the domain already exists, return the existing domain data and do not fail.

.. describe:: <domain-name>

    New domain name

domain delete
-------------

Delete domain(s)

.. program:: domain delete
.. code:: bash

    os domain delete
        <domain> [<domain> ...]

.. describe:: <domain>

    Domain(s) to delete (name or ID)

domain list
-----------

List domains

.. program:: domain list
.. code:: bash

    os domain list

domain set
----------

Set domain properties

.. program:: domain set
.. code:: bash

    os domain set
        [--name <name>]
        [--description <description>]
        [--enable | --disable]
        <domain>

.. option:: --name <name>

    New domain name

.. option:: --description <description>

    New domain description

.. option:: --enable

    Enable domain

.. option:: --disable

    Disable domain

.. describe:: <domain>

    Domain to modify (name or ID)

domain show
-----------

Display domain details

.. program:: domain show
.. code:: bash

    os domain show
        <domain>

.. describe:: <domain>

    Domain to display (name or ID)
