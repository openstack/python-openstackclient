=======
project
=======

Identity v2, v3

project create
--------------

Create new project

.. program:: project create
.. code:: bash

    os project create
        [--domain <domain>]
        [--parent <project>]
        [--description <description>]
        [--enable | --disable]
        [--property <key=value>]
        [--or-show]
        <name>

.. option:: --domain <domain>

    Domain owning the project (name or ID)

    .. versionadded:: 3

.. option:: --parent <project>

    Parent of the project (name or ID)

    .. versionadded:: 3

.. option:: --description <description>

    Project description

.. option:: --enable

    Enable project (default)

.. option:: --disable

    Disable project

.. option:: --property <key=value>

    Add a property to :ref:`\<name\> <project_create-name>`
    (repeat option to set multiple properties)

.. option:: --or-show

    Return existing project

    If the project already exists return the existing project data and do not fail.

.. _project_create-name:
.. describe:: <name>

    New project name

project delete
--------------

Delete project(s)

.. program:: project delete
.. code:: bash

    os project delete
        [--domain <domain>]
        <project> [<project> ...]

.. option:: --domain <domain>

    Domain owning :ref:`\<project\> <project_delete-project>` (name or ID)

    .. versionadded:: 3

.. _project_delete-project:
.. describe:: <project>

    Project to delete (name or ID)

project list
------------

List projects

.. program:: project list
.. code:: bash

    os project list
        [--domain <domain>]
        [--user <user>]
        [--long]

.. option:: --domain <domain>

    Filter projects by :option:`\<domain\> <--domain>` (name or ID)

    .. versionadded:: 3

.. option:: --user <user>

    Filter projects by :option:`\<user\> <--user>` (name or ID)

    .. versionadded:: 3

.. option:: --long

    List additional fields in output

project set
-----------

Set project properties

.. program:: project set
.. code:: bash

    os project set
        [--name <name>]
        [--domain <domain>]
        [--description <description>]
        [--enable | --disable]
        [--property <key=value>]
        <project>

.. option:: --name <name>

    Set project name

.. option:: --domain <domain>

    Domain owning :ref:`\<project\> <project_set-project>` (name or ID)

    .. versionadded:: 3

.. option:: --description <description>

    Set project description

.. option:: --enable

    Enable project (default)

.. option:: --disable

    Disable project

.. option:: --property <key=value>

    Set a property on :ref:`\<project\> <project_set-project>`
    (repeat option to set multiple properties)

    *Identity version 2 only*

.. _project_set-project:
.. describe:: <project>

    Project to modify (name or ID)

project show
------------

Display project details

.. program:: project show
.. code:: bash

    os project show
        [--domain <domain>]
        <project>

.. option:: --domain <domain>

    Domain owning :ref:`\<project\> <project_show-project>` (name or ID)

    .. versionadded:: 3

.. option:: --parents

    Show the project\'s parents as a list

    .. versionadded:: 3

.. option:: --children

    Show project\'s subtree (children) as a list

    .. versionadded:: 3

.. _project_show-project:
.. describe:: <project>

    Project to display (name or ID)

project unset
-------------

Unset project properties

*Identity version 2 only*

.. program:: project unset
.. code:: bash

    os project unset
        --property <key> [--property <key> ...]
        <project>

.. option:: --property <key>

    Property key to remove from project (repeat option to remove multiple properties)

.. describe:: <project>

    Project to modify (name or ID)
