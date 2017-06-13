===============================
network auto allocated topology
===============================

An **auto allocated topology** allows admins to quickly set up external
connectivity for end-users. Only one auto allocated topology is allowed per
project. For more information on how to set up the resources required
for auto allocated topology review the documentation at:
http://docs.openstack.org/newton/networking-guide/config-auto-allocation.html

Network v2

network auto allocated topology create
--------------------------------------

Create the auto allocated topology for project

.. program:: network auto allocated topology create
.. code:: bash

    openstack network auto allocated topology create
        [--or-show]
        [--check-resources]
        [--project <project> [--project-domain <project-domain>]]

.. option:: --or-show

    If topology exists returns the topologies information (Default).

.. option:: --check-resources

    Validate the requirements for auto allocated topology.
    Does not return a topology.

.. option:: --project <project>

    Return the auto allocated topology for a given project.
    Default is current project.

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. _network_auto_allocated_topology_create:


network auto allocated topology delete
--------------------------------------

Delete auto allocated topology for project

.. program:: network auto allocated topology delete
.. code:: bash

    openstack network auto allocated topology delete
        [--project <project> [--project-domain <project-domain>]]

.. option:: --project <project>

    Delete auto allocated topology for a given project.
    Default is the current project.

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. _network_auto_allocated_topology_delete:
