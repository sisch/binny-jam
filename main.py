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
    speed = 2.0

    def on_update(self, update, signal):
        self.speed = max(0.0, min(5.0, self.speed + random.random() * 0.5 - 0.25))
        random_rotation_offset = (random.random() * 5 - 2.5) * update.time_delta
        self.direction = rotated_vector(self.direction, random_rotation_offset).normalize()

    def on_key_pressed(self, event, signal):
        if config.DEBUG and event.key == ppb.keycodes.W:
            rot = 45
            self.direction = rotated_vector(self.direction, rot)


class WindLabel(ppb.Sprite):
    position = ppb.Vector(-1, -1)
    image = None
    update_timer = 0
    update_interval = 0.5
    tags = ("Wind", )
    wind = None

    def on_update(self, update_event, signal):
        cam = update_event.scene.main_camera
        self.position = cam.position + ppb.Vector(-8.5, -8.5)
        self.update_timer += update_event.time_delta
        if self.update_timer > self.update_interval:
            self.update_timer -= self.update_interval
            self.image = ppb.Text(f"Wind {self.wind.speed:.1f} knots {wind_direction(self.wind.direction)}", font=ppb.Font("assets/fonts/Fredoka-Regular.ttf", size=12), color=(255, 255, 255))



def setup(scene):
    w = scene.add(Wind())
    scene.add(WindLabel(wind=w))
    scene.add(ships.Player(position=ppb.Vector(0, -5), wind=w))
    scene.add(ships.Enemy(position=ppb.Vector(0, 0), wind=w, direction=ppb.Vector(1, 0)))


def run():
    ppb.run(setup)


if __name__ == '__main__':
    run()
