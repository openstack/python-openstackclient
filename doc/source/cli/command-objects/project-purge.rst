=============
project purge
=============

Clean resources associated with a specific project.

Block Storage v1, v2; Compute v2; Image v1, v2

project purge
-------------

Clean resources associated with a project

.. program:: project purge
.. code:: bash

    openstack project purge
        [--dry-run]
        [--keep-project]
        [--auth-project | --project <project>]
        [--project-domain <project-domain>]

.. option:: --dry-run

    List a project's resources

.. option:: --keep-project

    Clean project resources, but don't delete the project.

.. option:: --auth-project

    Delete resources of the project used to authenticate

.. option:: --project <project>

    Project to clean (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can be
    used in case collisions between project names exist.
