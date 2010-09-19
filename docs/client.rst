:class:`VogelerClient`
====================================================
This instantiates an instance of a :class:`vogeler.client.VogelerClient` for operating in the Client role.

The job of the client role is to consume messages from a broadcast exchange from a runner, validate the request against a set of authorized plugins and run said plugin.

Results are then posted onto a different exchange for consumption by the Server role.

The :mod:`client` Module
------------------------

.. automodule:: vogeler.client
    :members:
    :undoc-members:
    :show-inheritance:
