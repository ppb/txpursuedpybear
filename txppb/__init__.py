import functools
from typing import Callable, Optional

from twisted.internet import defer, task
from twisted.internet import interfaces
import ppb
from ppb.scenes import BaseScene


class _FinishLoop(Exception):
    pass


@defer.inlineCallbacks
def main_loop(
        reactor: interfaces.IReactorTime,
        engine: ppb.engine.GameEngine
    ) -> defer.Deferred:
    """Run until the game window is closed

    Start the engine, and then call it in a loop,
    until the engine is done running.
    The deferred is fired with `None`
    if the loop closed normally,
    or with an error if there was a problem with the engine.
    """
    def loop_once(engine):
        if not engine.running:
            raise _FinishLoop(engine)
        engine.loop_once()
    loop = task.LoopingCall(loop_once, engine)
    loop.clock = reactor
    engine.start()
    try:
        yield loop.start(0.001)
    except _FinishLoop:
        pass


@defer.inlineCallbacks
def run(
        setup: Callable[[BaseScene], None]=None,
        reactor: Optional[interfaces.IReactorTime]=None,
        *,
        starting_scene: type=BaseScene,
        title: str="PursedPyBear",
        **kwargs
    ) -> defer.Deferred:
    """Run until the game window is closed

    Start the engine, and then call it in a loop,
    until the engine is done running.
    The deferred is fired with `None`
    if the loop closed normally,
    or with an error if there was a problem with the engine.
    """
    if reactor is None:
        from twisted.internet import reactor as _default_reactor
        reactor = _default_reactor
    engine = ppb.make_engine(
        setup,
        starting_scene=starting_scene,
        title=title,
        **kwargs,
    )
    with engine:
        yield main_loop(reactor, engine)
