import functools
from typing import Callable

from twisted.internet import defer, task
from twisted.internet import interfaces
import ppb
from ppb.scenes import BaseScene


class _FinishLoop(Exception):
    pass


@defer.inlineCallbacks
def main_loop(reactor: interfaces.IReactorTime, engine: ppb.engine.GameEngine):
    """Run forever

    Run blah blah"""
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


def make_engine(reactor=None,
                setup: Callable[[BaseScene], None]=None, *,
                starting_scene=BaseScene, title="PursedPyBear",
                **kwargs):
    if reactor is None:
        from twisted.internet import reactor as _default_reactor
        reactor = _default_reactor
    return ppb.make_engine(
        setup,
        starting_scene=starting_scene,
        title=title,
        reactor=reactor,
        **kwargs
    )


@defer.inlineCallbacks
def run(setup: Callable[[BaseScene], None]=None,
        reactor=None, *,
        starting_scene=BaseScene, title="PursedPyBear",
        **kwargs):
    engine = make_engine(
        reactor,
        setup,
        starting_scene=starting_scene,
        title=title,
        **kwargs,
    )
    with engine:
        yield main_loop(reactor, engine)
