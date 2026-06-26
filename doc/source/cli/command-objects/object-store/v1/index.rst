==========================
Object Storage v1 Commands
==========================


container
---------

A **container** defines a namespace for **objects**.

.. autoprogram-cliff:: openstack.object_store.v1
   :command: container create

.. autoprogram-cliff:: openstack.object_store.v1
   :command: container delete

.. autoprogram-cliff:: openstack.object_store.v1
   :command: container list

.. autoprogram-cliff:: openstack.object_store.v1
   :command: container save

.. autoprogram-cliff:: openstack.object_store.v1
   :command: container set

.. autoprogram-cliff:: openstack.object_store.v1
   :command: container show

.. autoprogram-cliff:: openstack.object_store.v1
   :command: container unset


object store account
--------------------

An **object store account** represents the top-level of the hierarchy that
is comprised of **containers** and **objects**.

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object store account set

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object store account show

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object store account unset


object
------

An **object** stores data content, such as documents, images, and so on. They
can also store custom metadata with an object.

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object create

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object delete

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object list

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object save

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object set

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object show

.. autoprogram-cliff:: openstack.object_store.v1
   :command: object unset
