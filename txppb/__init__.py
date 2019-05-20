import functools
from typing import Any, Callable

from twisted.internet import defer, task
import ppb
from ppb.scenes import BaseScene


class _FinishLoop(Exception):
    pass


@defer.inlineCallbacks
def main_loop(reactor, engine):
    def loop_once(engine):
        if not engine.running:
            raise _FinishLoop(engine)
        print("woohoo")
        engine.loop_once()
    loop = task.LoopingCall(loop_once, engine)
    loop.clock = reactor
    engine.start()
    try:
        yield loop.start(0.001)
    except _FinishLoop:
        pass


def make_engine(reactor=None,
                setup: Callable[[Any, BaseScene], None]=None, *,
                starting_scene=BaseScene, title="PursedPyBear"):
    if reactor is None:
        from twisted.internet import reactor as _default_reactor
        reactor = _default_reactor
    setup = functools.partial(setup, reactor)
    return ppb.make_engine(setup, starting_scene=starting_scene, title=title)


@defer.inlineCallbacks
def run(reactor=None,
        setup: Callable[[Any, BaseScene], None]=None, *,
        starting_scene=BaseScene, title="PursedPyBear"):
    engine = make_engine(
        reactor,
        setup,
        starting_scene=starting_scene,
        title=title
    )
    with engine:
        yield main_loop(reactor, engine)
