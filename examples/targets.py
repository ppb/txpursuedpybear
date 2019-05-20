import logging
import ppb
from ppb import Vector
from ppb import keycodes
import txppb
import klein
from dataclasses import dataclass
from typing import Any
from twisted.internet import task, endpoints
from twisted.web.server import Site


class MoverMixin(ppb.BaseSprite):
    velocity = Vector(0, 0)

    def on_update(self, update, signal):
        self.position += self.velocity * update.time_delta


class Player(MoverMixin, ppb.BaseSprite):
    # We handle movement by mapping each key to a velocity vector
    # and adding it on press and subtracting it on release.
    left_vector = Vector(-1, 0)
    right_vector = Vector(1, 0)
    _rotation = 180

    def on_key_pressed(self, event, signal):
        if event.key in (keycodes.A, keycodes.Left):
            self.velocity += self.left_vector
        elif event.key in (keycodes.D, keycodes.Right):
            self.velocity += self.right_vector
        elif event.key is keycodes.Space:
            self._fire_bullet(event.scene)

    def on_key_released(self, event, signal):
        if event.key in (keycodes.A, keycodes.Left):
            self.velocity -= self.left_vector
        elif event.key in (keycodes.D, keycodes.Right):
            self.velocity -= self.right_vector

    def on_button_pressed(self, event, signal):
        if event.button is ppb.buttons.Primary:
            self._fire_bullet(event.scene)

    def _fire_bullet(self, scene):
        scene.add(
            Bullet(pos=self.position),
            tags=['bullet']
        )


class Bullet(MoverMixin, ppb.BaseSprite):
    velocity = Vector(0, 2)
    _rotation = 180

    def on_update(self, update, signal):
        super().on_update(update, signal)  # Execute movement

        scene = update.scene
        
        if self.position.y > scene.main_camera.frame_bottom:
            scene.remove(self)
        else:
            for target in scene.get(tag='target'):
                d = (target.position - self.position).length
                if d <= target.radius:
                    scene.remove(self)
                    scene.remove(target)
                    break


class Target(ppb.BaseSprite):
    radius = 0.5


def setup(reactor, scene):
    scene.add(Player(pos=Vector(0, 0)), tags=['player'])

    # 5 targets in x = -3.75 -> 3.75, with margin
    for x in (-3, -1.5, 0, 1.5, 3):
        scene.add(Target(pos=Vector(x, 1.875)), tags=['target'])

    TargetCounter.web_server(
        reactor=reactor,
        scene=scene,
        description="tcp:8080"
    )


@dataclass(eq=False)
class TargetCounter(object):

    scene: Any

    app = klein.Klein()

    @app.route('/')
    def count(self, request):
        live = sum(1 for x in self.scene.get(tag='target'))
        return str(live)

    @classmethod
    def web_server(cls, reactor, scene, description):
        ep = endpoints.serverFromString(reactor, description)
        counter = cls(scene)
        return reactor.callWhenRunning(ep.listen, Site(counter.app.resource()))


def main(reactor):
    return txppb.run(reactor, setup)


if __name__ == "__main__":
    import sys
    task.react(main, sys.argv[1:])
