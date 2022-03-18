#!/usr/bin/env python3
import math
import random

import ppb
from ppb.gomlib import GameObject

import ships
from mathutils import rotated_vector
import config
from labels import LootLabel, LootLabel2, CannonLabel, CannonLabel2, WindLabel, Indicator, EnemiesLeftLabel


class Wind(GameObject):
    direction = ppb.directions.Up
    speed = 1.0
    timer = 0
    change_interval = 5

    def on_update(self, update, signal):
        self.speed = max(0.0, min(2.5, self.speed + random.random() * 0.5 - 0.25))

        self.timer += update.time_delta
        if self.timer >= self.change_interval:
            self.timer -= self.change_interval
            random_rotation_offset = random.random() * 50 - 25
            self.direction = rotated_vector(self.direction, random_rotation_offset).normalize()

    def on_key_pressed(self, event, signal):
        if config.DEBUG and event.key == ppb.keycodes.W:
            rot = 45
            self.direction = rotated_vector(self.direction, rot)


def setup(scene):
    w = scene.add(Wind())
    scene.add(WindLabel(wind=w))
    player = scene.add(ships.Player(position=ppb.Vector(0, 0), wind=w, facing=ppb.directions.Up))
    difficulty = 1.0
    for e in range(config.number_of_enemies):
        angle = random.random() * math.tau  # 0 - 360 degrees in radians
        radius = random.random() * (5*difficulty) + 3
        spawn_position = ppb.Vector(radius*math.cos(angle), radius*math.sin(angle))
        # Check for collision once. Not nice but suitable for now
        for enemy in scene.get(kind=ships.Enemy):
            if (enemy.position - spawn_position).length <= enemy.size:
                angle = random.random() * math.tau
                spawn_position = ppb.Vector(radius * math.cos(angle), radius * math.sin(angle))
        angle = random.random() * math.tau
        look_direction = ppb.Vector(math.cos(angle), math.sin(angle))
        enemy_ship = scene.add(ships.Enemy(
            position=spawn_position,
            wind=w,
            facing=look_direction,
            is_anchored=True,
            anchor_timer=random.random()*20,
            turn_timer=random.random()*15,
            max_projectiles=math.ceil(difficulty),
            projectile_range=1.5 + 0.1 * 2**difficulty,
            shoot_timeout=1/difficulty))
        scene.add(Indicator(player=player, target=enemy_ship))
        if e > 3:
            difficulty += 0.5
    scene.add(CannonLabel())
    scene.add(CannonLabel2(player=player))
    scene.add(LootLabel())
    scene.add(LootLabel2(player=player))
    scene.add(EnemiesLeftLabel())


def run():
    ppb.run(setup, title="Letter of Sean ... or Was It Marque?")


if __name__ == '__main__':
    run()
