import ppb
from ppb.events import KeyReleased, KeyPressed

import config
from effects import Explosion
from mathutils import dot_product_as_cos, lerp_vector, rotated_vector
from weapons import CannonBall


class Ship(ppb.Sprite):
    speed = 1.0
    image = ppb.Image("assets/sprites/Default size/Ships/ship (3).png")
    image_paths = []
    left = None
    right = None
    shoot_right = None
    shoot_left = None
    turn_speed = 1.5
    direction = ppb.directions.Up
    projectile_speed = 1.0
    projectiles_flying = 0
    max_projectiles = 1
    wind = None
    health = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.basis = ppb.directions.Down
        self.facing = self.direction
        self.image = ppb.Image(self.image_paths[0])

    def on_update(self, update_event, signal):
        scene = update_event.scene
        movement = self.facing * self.speed * update_event.time_delta
        wind_effect = dot_product_as_cos(self.facing, self.wind.direction)
        if config.DEBUG:
            print(f"{wind_effect:.2f}")
        movement += self.facing * (wind_effect * self.wind.speed * update_event.time_delta)
        if dot_product_as_cos(self.facing, movement) < 0:
            movement = ppb.Vector(0, 0)
        self.position += movement
        if self.health <= 0:
            # TODO: Start Splash animation and spawn pickup
            scene.remove(self)

    def take_damage(self, projectile):
        self.health -= projectile.damage
        if self.health <= 0:
            return
        self.image = ppb.Image(self.image_paths[-self.health])
        self.speed *= 0.5


class Player(Ship):
    left = config.Keys.move_left
    right = config.Keys.move_right
    shoot_right = config.Keys.use
    shoot_left = config.Keys.swap
    cam_origin = None
    cam_target = None
    cam_progress = 0
    image_paths = [
        "assets/sprites/Default size/Ships/ship (3).png",
        "assets/sprites/Default size/Ships/ship (9).png",
        "assets/sprites/Default size/Ships/ship (15).png"
    ]

    def on_key_pressed(self, key_event: KeyPressed, signal):
        if key_event.key == self.left:
            self.rotate(15)
        elif key_event.key == self.right:
            self.rotate(-15)
        elif key_event.key == self.shoot_right or key_event.key == self.shoot_left:
            if self.projectiles_flying >= self.max_projectiles:
                return
            rotation = 90 if key_event.key == self.shoot_right else -90
            shoot_direction = rotated_vector(self.facing, rotation)
            key_event.scene.add(CannonBall(shooter=self, position=self.position + shoot_direction * 0.5, direction=shoot_direction * (self.speed + self.projectile_speed)))
            self.projectiles_flying += 1

    def on_key_released(self, key_event: KeyReleased, signal):
        if key_event.key == self.left:
            self.direction = ppb.Vector(1, 0)
        elif key_event.key == self.right:
            self.direction = ppb.Vector(-1, 0)

    def on_update(self, update_event, signal):
        super().on_update(update_event, signal)
        cam = update_event.scene.main_camera
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


class Enemy(Ship):
    image_paths = [
        "assets/sprites/Default size/Ships/ship (2).png",
        "assets/sprites/Default size/Ships/ship (8).png",
        "assets/sprites/Default size/Ships/ship (14).png"
    ]
