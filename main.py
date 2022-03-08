#!/usr/bin/env python3
import math
import random

import ppb
from ppb.events import KeyPressed, KeyReleased
from ppb.features.animation import Animation
from ppb.gomlib import GameObject

import config
from events import AnimationLooped

DEBUG=True



def lerp(a,b,t):
    return a*(1-t)+b*t


def lerp_vector(a, b, t):
    c = ppb.Vector(lerp(a.x, b.x, t), lerp(a.y, b.y, t))
    return c

def rotated_vector(vector, angle_in_degrees):
    ang_in_rad = angle_in_degrees / 360.0 * math.tau
    new_vec = ppb.Vector(
        math.cos(ang_in_rad) * vector.x + math.sin(ang_in_rad) * vector.y,
        -math.sin(ang_in_rad) * vector.x + math.cos(ang_in_rad) * vector.y)
    return new_vec

def dot_product(vec1, vec2):
    return vec1.x * vec2.x + vec1.y*vec2.y

def dot_product_as_cos(vec1,vec2):
    return dot_product(vec1, vec2) / (vec1.length * vec2.length)


class Player(ppb.Sprite):
    speed = 1.0
    image = ppb.Image("assets/sprites/Default size/Ships/ship (3).png")
    left = config.Keys.move_left
    right = config.Keys.move_right
    shoot_right = config.Keys.use
    shoot_left = config.Keys.swap
    turn_speed = 1.5
    direction = ppb.directions.Up
    projectile_speed = 1.0
    cam_origin = None
    cam_target = None
    cam_progress = 0
    projectiles_flying = 0
    wind = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.basis = ppb.directions.Down
        self.facing = self.direction

    def on_update(self, update_event, signal):
        scene = update_event.scene
        cam = scene.main_camera
        movement = self.facing * self.speed * update_event.time_delta
        wind_effect = dot_product_as_cos(self.facing, self.wind.direction)
        if DEBUG:
            print(f"{wind_effect:.2f}")
        movement += self.facing * (wind_effect*self.wind.speed * update_event.time_delta)
        if dot_product_as_cos(self.facing, movement) < 0:
            movement = ppb.Vector(0, 0)
        self.position += movement
        if self.cam_origin is None and (cam.position - self.position).length > 4:
            self.cam_origin = cam.position
            self.cam_target = self.position

        if self.cam_origin is not None and self.cam_target is not None:
            self.cam_progress += update_event.time_delta
            cam.position = lerp_vector(self.cam_origin, self.cam_target, self.cam_progress)
            if self.cam_progress >= 1:
                cam.position = self.cam_target
                self.cam_origin = None
                self.cam_target = None
                self.cam_progress = 0

    def on_key_pressed(self, key_event: KeyPressed, signal):
        if key_event.key == self.left:
            self.rotate(15)
        elif key_event.key == self.right:
            self.rotate(-15)
        elif key_event.key == self.shoot_right or key_event.key == self.shoot_left:
            if self.projectiles_flying > 3:
                return
            rotation = 90 if key_event.key == self.shoot_right else -90
            shoot_direction = rotated_vector(self.facing, rotation)
            key_event.scene.add(Projectile(shooter=self, position=self.position + shoot_direction*0.5, direction=shoot_direction*(self.speed + self.projectile_speed)))
            self.projectiles_flying += 1

    def on_key_released(self, key_event: KeyReleased, signal):
        if key_event.key == self.left:
            self.direction = ppb.Vector(1, 0)
        elif key_event.key == self.right:
            self.direction = ppb.Vector(-1, 0)


class Projectile(ppb.Sprite):
    shooter = None
    size = 0.25
    drag = 0.5
    direction = None
    image = ppb.Image("assets/sprites/Default size/Ship parts/cannonBall.png")

    def on_update(self, update_event, signal):
        self.position += self.direction * update_event.time_delta
        self.direction -= self.direction*self.drag*update_event.time_delta
        if self.direction.length < 0.3:
            update_event.scene.add(Splash(position=self.position))
            self.shooter.projectiles_flying -= 1
            update_event.scene.remove(self)


class Splash(ppb.Sprite):
    image = Animation("assets/sprites/Effects/Splash{1..3}.png", 3)
    size = 0.4
    timer = 0
    def __init__(self, **props):
        super().__init__(**props)
        self.duration = self.image.number_of_frames() / self.image.frames_per_second

    def on_update(self, event, signal):
        if self.timer >= self.duration:
            signal(AnimationLooped())
        self.timer += event.time_delta

    def on_animation_looped(self, event, signal):
        event.scene.remove(self)


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
        if DEBUG and event.key == ppb.keycodes.W:
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
    scene.add(Player(position=ppb.Vector(0, -5), wind=w))

def run():
    ppb.run(setup)


if __name__ == '__main__':
    run()
