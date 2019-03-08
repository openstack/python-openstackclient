=====================
network segment range
=====================

A **network segment range** is a resource for tenant network segment
allocation.
A network segment range exposes the segment range management to be administered
via the Neutron API. In addition, it introduces the ability for the
administrator to control the segment ranges globally or on a per-tenant basis.

Network v2

network segment range create
----------------------------

Create new network segment range

.. program:: network segment range create
.. code:: bash

    openstack network segment range create
          (--private | --shared)
          [--project <project> [--project-domain <project-domain>]]
          --network-type <network-type>
          [--physical-network <physical-network-name>]
          --minimum <minimum-segmentation-id>
          --maximum <maximum-segmentation-id>
          <name>

.. option:: --private

    Network segment range is assigned specifically to the project

.. option:: --shared

    Network segment range is shared with other projects

.. option:: --project <project>

    Network segment range owner (name or ID). Optional when the segment
    range is shared

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --physical-network <physical-network-name>

    Physical network name of this network segment range

.. option:: --network-type <network-type>

    Network type of this network segment range
    (geneve, gre, vlan or vxlan)

.. option:: --minimum <minimum-segmentation-id>

    Minimum segment identifier for this network segment range which is based
    on the network type, VLAN ID for vlan network type and tunnel ID for
    geneve, gre and vxlan network types

.. option:: --maximum <maximum-segmentation-id>

    Maximum segment identifier for this network segment range which is based
    on the network type, VLAN ID for vlan network type and tunnel ID for
    geneve, gre and vxlan network types

.. _network_segment_range_create-name:
.. describe:: <name>

    Name of new network segment range

network segment range delete
----------------------------

Delete network segment range(s)

.. program:: network segment range delete
.. code:: bash

    openstack network segment range delete
        <network-segment-range> [<network-segment-range> ...]

.. _network_segment_range_delete-network-segment-range:
.. describe:: <network-segment-range>

    Network segment range (s) to delete (name or ID)

network segment range list
--------------------------

List network segment ranges

.. program:: network segment range list
.. code:: bash

    openstack network segment range list
        [--long]
        [--used | --unused]
        [--available | --unavailable]

.. option:: --long

    List additional fields in output

.. option:: --used

    List network segment ranges that have segments in use

.. option:: --unused

    List network segment ranges that do not have segments not in use

.. option:: --available

    List network segment ranges that have available segments

.. option:: --unavailable

    List network segment ranges without available segments

network segment range set
-------------------------

Set network segment range properties

.. program:: network segment range set
.. code:: bash

    openstack network segment range set
        [--name <name>]
        [--minimum <minimum-segmentation-id>]
        [--maximum <maximum-segmentation-id>]
        <network-segment-range>

.. option:: --name <name>

    Set network segment range name

.. option:: --minimum <minimum-segmentation-id>

    Set network segment range minimum segment identifier

.. option:: --maximum <maximum-segmentation-id>

    Set network segment range maximum segment identifier

.. _network_segment_range_set-network-segment-range:
.. describe:: <network-segment-range>

    Network segment range to modify (name or ID)

network segment range show
--------------------------

Display network segment range details

.. program:: network segment range show
.. code:: bash

    openstack network segment range show
        <network-segment-range>

.. _network_segment_range_show-network-segment-range:
.. describe:: <network-segment-range>

    Network segment range to display (name or ID)
