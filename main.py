#!/usr/bin/env python3
import math
import random

import ppb
from ppb.gomlib import GameObject

import ships
from mathutils import rotated_vector
import config


def wind_direction(vector: ppb.Vector):
    angle = math.atan2(vector.y, vector.x)*360/math.tau
    angle = (angle + 360.0) % 360.0
    if 90-22.5 < angle <= 90+22.5:
        return "N"
    elif 45.0 - 22.5 < angle <= 45.0 + 22.5:
        return "NE"
    elif angle <= 0 + 22.5 or angle > 360.0 - 22.5:
        return "E"
    elif 315.0 - 22.5 < angle <= 315.0 + 22.5:
        return "SE"
    elif 270.0 - 22.5 < angle <= 270.0 + 22.5:
        return "S"
    elif 225.0 - 22.5 < angle <= 225.0 + 22.5:
        return "SW"
    elif 180.0 - 22.5 < angle <= 180.0 + 22.5:
        return "W"
    elif 135.0 - 22.5 < angle <= 135.0 + 22.5:
        return "NW"
    return str(angle)


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


class UILabel(ppb.Sprite):
    image = None
    update_timer = 0
    update_interval = 0.5
    screen_position = ppb.Vector(1, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_update(self, update_event, signal):
        cam = update_event.scene.main_camera
        self.position = cam.position + self.screen_position
        self.update_timer += update_event.time_delta


class WindLabel(UILabel):
    screen_position = ppb.Vector(-8.5, -8.5)
    tags = ("Wind", )
    wind = None

    def on_update(self, update_event, signal):
        super().on_update(update_event, signal)
        if self.update_timer > self.update_interval:
            self.update_timer -= self.update_interval
            self.image = ppb.Text(f"Wind {self.wind.speed:.1f} knots {wind_direction(self.wind.direction)}",
                                  font=config.default_font, color=(255, 255, 255))


class CannonLabel2(UILabel):
    screen_position = ppb.Vector(9, 9)
    tags = ("cannonUI",)
    player = None

    def on_update(self, update_event, signal):
        if self.player is None:
            for p in update_event.scene.get(kind="Player"):
                self.player = p
                break  # Assuming only one player
        super().on_update(update_event, signal)
        if self.update_timer > self.update_interval:
            self.update_timer -= self.update_interval
            font = config.default_font
            font.size = 8
            self.image = ppb.Text(f"       {self.player.max_projectiles}",
                                  font=font, color=(255, 255, 255))

class CannonLabel(UILabel):
    screen_position = ppb.Vector(8.5, 8.8)
    size = 0.5
    image = ppb.Image("assets/sprites/cannon_icon.png")

class LootLabel2(UILabel):
    screen_position = ppb.Vector(9, 7.5)
    tags = ("cannonUI",)
    player = None

    def on_update(self, update_event, signal):
        if self.player is None:
            for p in update_event.scene.get(kind="Player"):
                self.player = p
                break  # Assuming only one player
        super().on_update(update_event, signal)
        if self.update_timer > self.update_interval:
            self.update_timer -= self.update_interval
            font = config.default_font
            font.size = 8
            self.image = ppb.Text(f"       {self.player.upgrade_points}",
                                  font=font, color=(255, 255, 255))


class LootLabel(UILabel):
    screen_position = ppb.Vector(8.5, 7.5)
    size = 1
    image = ppb.Image("assets/sprites/chestpack01openwood_withgold.png")


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
