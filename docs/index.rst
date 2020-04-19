Twisted Extension for PursuedPyBear
===================================

Integrate PursuedPyBear with the Twisted event loop.

This module allows running the PursuedPyBear main loop
inside of the Twisted loop.

.. automodule:: txppb
    :members:
   

In order to integrate with a foreign event loop
it is possible to use Twisted's native foreign event loop
integration.

For example,
to integrate with
:code:`asyncio`,
the following needs to be done before importing
:code:`twisted.internet.reactor`:

.. code::

    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())

