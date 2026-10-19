=======================
Accelerator v2 Commands
=======================

.. versionchanged:: 10.4.0
   These commands were moved in-tree from the python-cyborgclient plugin.

accelerator request (ARQ)
-------------------------

An **accelerator request** (ARQ) represents a request for an accelerator
device to be assigned to an instance. ARQs are created against a device
profile and can be bound to an instance and resource provider.

.. autoprogram-cliff:: openstack.accelerator.v2
   :command: accelerator arq *


deployable
----------

A **deployable** is a logical unit of an accelerator device that can be
programmed with a bitstream image.

.. autoprogram-cliff:: openstack.accelerator.v2
   :command: accelerator deployable *


device
------

A **device** is a physical accelerator device discovered by the Cyborg
agent on a compute host.

.. autoprogram-cliff:: openstack.accelerator.v2
   :command: accelerator device disable

.. autoprogram-cliff:: openstack.accelerator.v2
   :command: accelerator device enable

.. autoprogram-cliff:: openstack.accelerator.v2
   :command: accelerator device list

.. autoprogram-cliff:: openstack.accelerator.v2
   :command: accelerator device show


device attribute
----------------

A **device attribute** is a key-value pair associated with a deployable,
used to describe device capabilities or traits.

.. autoprogram-cliff:: openstack.accelerator.v2
   :command: accelerator device attribute *


device profile
--------------

A **device profile** describes the accelerator resources required by a
workload, expressed as a list of resource groups with placement traits
and resource classes.

.. autoprogram-cliff:: openstack.accelerator.v2
   :command: accelerator device profile *
