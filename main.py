#!/usr/bin/env python3
import math
import random

import ppb
from ppb.gomlib import GameObject

import ships
from mathutils import rotated_vector
import config
from labels import LootLabel, LootLabel2, CannonLabel, CannonLabel2, WindLabel

class Wind(GameObject):
    direction = ppb.directions.Up
    speed = 1.0

    def on_update(self, update, signal):
        self.speed = max(0.0, min(2.5, self.speed + random.random() * 0.5 - 0.25))
        random_rotation_offset = (random.random() * 5 - 2.5) * update.time_delta
        self.direction = rotated_vector(self.direction, random_rotation_offset).normalize()

    def on_key_pressed(self, event, signal):
        if config.DEBUG and event.key == ppb.keycodes.W:
            rot = 45
            self.direction = rotated_vector(self.direction, rot)


def setup(scene):
    w = scene.add(Wind())
    scene.add(WindLabel(wind=w))
    player = scene.add(ships.Player(position=ppb.Vector(0, -5), wind=w, facing=ppb.directions.Up))
    for e in range(config.number_of_enemies):
        rnd = random.random()*10 - 5.0, random.random()*20 - 10
        dir = ppb.Vector(math.cos(rnd[0] * math.tau), math.sin(rnd[1] * math.tau))
        scene.add(ships.Enemy(position=ppb.Vector(rnd[0], e*rnd[1]), wind=w, facing=dir, is_anchored=True))
    scene.add(CannonLabel())
    scene.add(CannonLabel2(player=player))
    scene.add(LootLabel())
    scene.add(LootLabel2(player=player))


def run():
    ppb.run(setup)


if __name__ == '__main__':
    run()
