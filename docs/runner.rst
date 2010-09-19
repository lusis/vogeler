:class:`VogelerRunner`
======================
This instantiates an instance of a :class:`vogeler.runner.VogelerRunner` for operating in the Runner role.

The job of the runner role is to place messages on the broadcast exchange for consumption by the client role.

Those messages are tagged with a :attr:`vogeler.runner.VogelerRunner.destination` which is used by clients to determine if messages should be acted on.

The :mod:`runner` Module
------------------------

.. automodule:: vogeler.runner
    :members:
    :undoc-members:
    :show-inheritance:
