=======
example
=======

This is a specification for the ``example`` command object. It is not intended
to be a complete template for new commands since other actions, options
and/or arguments may be used. You can include general specification information
before the commands below. This information could include links to related material
or descriptions of similar commands.

[example API name] [example API version]

example create
--------------

Create new example

.. program:: example create
.. code:: bash

    os example create
        <name>

.. describe:: <name>

    New example name

example delete
--------------

Delete example(s)

.. program:: example delete
.. code:: bash

    os example delete
        <example> [<example> ...]

.. describe:: <example>

    Example(s) to delete (name or ID)

example list
------------

List examples

.. program:: example list
.. code:: bash

    os example list

example set
-----------

Set example properties

.. program:: example set
.. code:: bash

    os example set
        [--name <new-name>]
        <example>

.. option:: --name <new-name>

    New example name

.. describe:: <example>

    Example to modify (name or ID)

example show
------------

Display example details

.. program:: example show
.. code:: bash

    os example show
        <example>

.. describe:: <example>

    Example to display (name or ID)
