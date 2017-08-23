============
implied role
============

Identity v3


implied role create
-------------------

Creates an association between prior and implied roles

.. program:: implied role create
.. code:: bash

    openstack implied role create
        <role>
        --implied-role <role>

.. option:: <role>

    Prior role <role> (name or ID) implies another role

.. option:: --implied-role <role>

    <role> (name or ID) implied by another role


implied role delete
-------------------

Deletes an association between prior and implied roles

.. program:: implied role delete
.. code:: bash

    openstack implied role delete
        <role>
        --implied-role <role>

.. option:: <role>

    Prior role <role> (name or ID) implies another role

.. option:: --implied-role <role>

    <role> (name or ID) implied by another role

implied role list
-----------------

List implied roles

.. program:: implied role list
.. code:: bash

    openstack implied role list
