=====
quota
=====

Resource quotas appear in multiple APIs, OpenStackClient presents them as a
single object with multiple properties.

Block Storage v1, v2, Compute v2, Network v2

quota set
---------

Set quotas for project

.. program:: quota set
.. code:: bash

    os quota set
        # Compute settings
        [--cores <num-cores>]
        [--fixed-ips <num-fixed-ips>]
        [--floating-ips <num-floating-ips>]
        [--injected-file-size <injected-file-bytes>]
        [--injected-files <num-injected-files>]
        [--instances <num-instances>]
        [--key-pairs <num-key-pairs>]
        [--properties <num-properties>]
        [--ram <ram-mb>]
        [--server-groups <num-server-groups>]
        [--server-group-members <num-server-group-members>]

        # Block Storage settings
        [--backups <new-backups>]
        [--backup-gigabytes <new-backup-gigabytes>]
        [--gigabytes <new-gigabytes>]
        [--per-volume-gigabytes <new-per-volume-gigabytes>]
        [--snapshots <new-snapshots>]
        [--volumes <new-volumes>]
        [--volume-type <volume-type>]

        # Network settings
        [--floating-ips <num-floatingips>]
        [--secgroup-rules <num-security-group-rules>]
        [--secgroups <num-security-groups>]
        [--networks <num-networks>]
        [--subnets <num-subnets>]
        [--ports <num-ports>]
        [--routers <num-routers>]
        [--rbac-policies <num-rbac-policies>]
        [--vips <num-vips>]
        [--subnetpools <num-subnetpools>]
        [--members <num-members>]
        [--health-monitors <num-health-monitors>]

        <project>

Set quotas for class

.. code:: bash

    os quota set
        --class
        # Compute settings
        [--cores <num-cores>]
        [--fixed-ips <num-fixed-ips>]
        [--floating-ips <num-floating-ips>]
        [--injected-file-size <injected-file-bytes>]
        [--injected-files <num-injected-files>]
        [--instances <num-instances>]
        [--key-pairs <num-key-pairs>]
        [--properties <num-properties>]
        [--ram <ram-mb>]
        [--server-groups <num-server-groups>]
        [--server-group-members <num-server-group-members>]

        # Block Storage settings
        [--backups <new-backups>]
        [--backup-gigabytes <new-backup-gigabytes>]
        [--gigabytes <new-gigabytes>]
        [--per-volume-gigabytes <new-per-volume-gigabytes>]
        [--snapshots <new-snapshots>]
        [--volumes <new-volumes>]

        <class>

.. option:: --class

    Set quotas for ``<class>``

.. option:: --properties <new-properties>

    New value for the properties quota

.. option:: --ram <new-ram>

    New value for the ram quota

.. option:: --secgroup-rules <new-secgroup-rules>

    New value for the secgroup-rules quota

.. option:: --instances <new-instances>

    New value for the instances quota

.. option:: --key-pairs <new-key-pairs>

    New value for the key-pairs quota

.. option:: --fixed-ips <new-fixed-ips>

    New value for the fixed-ips quota

.. option:: --secgroups <new-secgroups>

    New value for the secgroups quota

.. option:: --injected-file-size <new-injected-file-size>

    New value for the injected-file-size quota

.. option:: --server-groups <new-server-groups>

    New value for the server-groups quota

.. option:: --server-group-members <new-server-group-members>

    New value for the server-group-members quota

.. option:: --floating-ips <new-floating-ips>

    New value for the floating-ips quota

.. option:: --injected-files <new-injected-files>

    New value for the injected-files quota

.. option:: --cores <new-cores>

    New value for the cores quota

.. option:: --injected-path-size <new-injected-path-size>

    New value for the injected-path-size quota

.. option:: --backups <new-backups>

    New value for the backups quota

.. option:: --backup-gigabytes <new-backup-gigabytes>

    New value for the backup gigabytes quota

.. option:: --gigabytes <new-gigabytes>

    New value for the gigabytes quota

.. option:: --per-volume-gigabytes <new-per-volume-gigabytes>

    New value for the gigabytes quota of per volume

.. option:: --volumes <new-volumes>

    New value for the volumes quota

.. option:: --snapshots <new-snapshots>

    New value for the snapshots quota

.. option:: --volume-type <volume-type>

    Set quotas for a specific <volume-type>. The supported quotas are:
    gigabytes, snapshots, volumes.

.. option:: --networks <num-networks>

    New value for the networks quota

.. option:: --subnets <num-subnets>

    New value for the subnets quota

.. option:: --ports <num-ports>

    New value for the ports quota

.. option:: --routers <num-routers>

    New value for the routers quota

.. option:: --rbac-policies <num-rbac-policies>

    New value for the rbac-policies quota

.. option:: --vips <num-vips>

    New value for the vips quota

.. option:: --subnetpools <num-subnetpools>

    New value for the subnetpools quota

.. option:: --members <num-members>

    New value for the members quota

.. option:: --health-monitors <num-health-monitors>

    New value for the health-monitors quota

quota show
----------

Show quotas for project or class

.. program:: quota show
.. code:: bash

    os quota show
        [--default]
        [<project>]


.. option:: --default

    Show default quotas for :ref:`\<project\> <quota_show-project>`

.. _quota_show-project:
.. describe:: <project>

    Show quotas for this project (name or ID)

.. code:: bash

    os quota show
        --class
        [<class>]

.. option:: --class

    Show quotas for :ref:`\<class\> <quota_show-class>`

.. _quota_show-class:
.. describe:: <class>

    Show quotas for this class (name or ID)
