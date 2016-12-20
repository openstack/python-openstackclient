======
policy
======

Identity v3

policy create
-------------

Create new policy

.. program:: policy create
.. code:: bash

    openstack policy create
        [--type <type>]
        <filename>

.. option:: --type <type>

    New MIME type of the policy rules file (defaults to application/json)

.. describe:: <filename>

    New serialized policy rules file

policy delete
-------------

Delete policy(s)

.. program:: policy delete
.. code:: bash

    openstack policy delete
        <policy> [<policy> ...]

.. describe:: <policy>

    Policy(s) to delete

policy list
-----------

List policies

.. program:: policy list
.. code:: bash

    openstack policy list
        [--long]

.. option:: --long

    List additional fields in output

policy set
----------

Set policy properties

.. program:: policy set
.. code:: bash

    openstack policy set
        [--type <type>]
        [--rules <filename>]
        <policy>

.. option:: --type <type>

    New MIME type of the policy rules file

.. describe:: --rules <filename>

    New serialized policy rules file

.. describe:: <policy>

    Policy to modify

policy show
-----------

Display policy details

.. program:: policy show
.. code:: bash

    openstack policy show
        <policy>

.. describe:: <policy>

    Policy to display
