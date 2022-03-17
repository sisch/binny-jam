import math

import ppb
from ppb.events import KeyReleased, KeyPressed
from ppb.features.animation import Animation

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
    turn_speed = 45
    direction = ppb.directions.Down
    projectile_range = 0.5
    projectiles_flying = 0
    projectile_damage = 0.5
    max_projectiles = 1
    wind = None
    wind_effect = 0
    health = 1
    max_health = 1
    is_anchored = False
    state = 0
    size = 0.4
    target_rotation = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = ppb.Image(self.image_paths[self.state])
        self.health = self.max_health
        self.target_rotation = (self.rotation + 180) % 360

    def on_update(self, update_event, signal):
        scene = update_event.scene

        # Move
        movement = self.facing * self.speed * update_event.time_delta
        wind_effect = dot_product_as_cos(self.facing, self.wind.direction)
        movement += self.wind_effect * self.facing * (wind_effect * self.wind.speed * update_event.time_delta)
        if dot_product_as_cos(self.facing, movement) < 0:
            movement = ppb.Vector(0, 0)
        if not self.__dict__.get("is_anchored", False):
            self.position += movement

        # Sink
        if self.health <= 0:
            # TODO: Start Splash animation and spawn pickup
            scene.add(Flotsam(position=self.position))
            scene.remove(self)
            return

        # Turn
        if self.target_rotation is not None and abs(max(self.target_rotation,self.rotation)-min(self.target_rotation, self.rotation)) > 10:
            direction = self.shortest_rotation_direction(self.rotation, self.target_rotation)
            self.rotate(direction*self.turn_speed*update_event.time_delta)

    def shortest_rotation_direction(self, from_rotation, to_rotation):
        fro = from_rotation /360 * math.tau
        to = to_rotation /360 * math.tau
        rotation = (fro-to + 5*math.tau/2) % math.tau - math.tau/2
        return rotation / abs(rotation)

    def turn_right(self, degrees=15):
        self.target_rotation = (self.target_rotation - degrees + 360) % 360

    def turn_left(self, degrees=15):
        self.target_rotation = (self.target_rotation + degrees + 360) % 360

    def take_damage(self, projectile):
        if self.health <= 0:
            return
        self.health -= projectile.damage
        self.state = 0 if self.health == self.max_health else 1 if self.health / self.max_health >= 0.5 else 2
        self.image = ppb.Image(self.image_paths[self.state])
        self.speed *= 0.5


class Player(Ship):
    left = config.Keys.left
    right = config.Keys.right
    shoot_right = config.Keys.use
    shoot_left = config.Keys.swap
    upgrade = config.Keys.up
    toggle_anchor = config.Keys.down
    cam_origin = None
    cam_target = None
    cam_progress = 0
    image_paths = [
        "assets/sprites/Default size/Ships/dinghyLarge1.png",
        "assets/sprites/Default size/Ships/dinghyLarge2.png",
        "assets/sprites/Default size/Ships/dinghyLarge3.png"
    ]
    upgrade_points = 0
    current_upgrade_level = 0
    upgrades_available = config.get_upgrade()

    def on_key_pressed(self, key_event: KeyPressed, signal):
        if key_event.key == self.left:
            self.turn_left()
        elif key_event.key == self.right:
            self.turn_right()
        elif key_event.key == self.upgrade:
            self.run_upgrade()
        elif key_event.key == self.toggle_anchor:
            self.is_anchored = not self.is_anchored
        elif key_event.key == self.shoot_right or key_event.key == self.shoot_left:
            if self.projectiles_flying >= self.max_projectiles:
                return
            rotation = 90 if key_event.key == self.shoot_right else -90
            shoot_direction = rotated_vector(self.facing, rotation)
            key_event.scene.add(CannonBall(shooter=self, position=self.position + shoot_direction * 0.5,
                                           direction=shoot_direction, range=self.projectile_range,
                                           damage=self.projectile_damage))
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

    def pickup(self, object):
        if isinstance(object, Flotsam):
            self.upgrade_points += 1
            self.health = min(self.health + 1, self.max_health)
            self.state = 0 if self.health == self.max_health else 1 if self.health / self.max_health >= 0.5 else 2

    def run_upgrade(self):
        cost = self.current_upgrade_level + 1
        if config.DEBUG:
            print(f"Upgrade costs: {cost}, available points: {self.upgrade_points}")
        if self.upgrade_points >= cost:
            self.upgrade_points -= cost
            for k, v in next(self.upgrades_available).items():
                if config.DEBUG:
                    print(k, v)
                if hasattr(self, k):
                    attribute = getattr(self, k)
                    if type(attribute) == int:
                        setattr(self, k, v+attribute)
                    else:
                        setattr(self, k, v)
            self.image = ppb.Image(self.image_paths[self.state])


class Enemy(Ship):
    image_paths = [
        "assets/sprites/Default size/Ships/ship (2).png",
        "assets/sprites/Default size/Ships/ship (8).png",
        "assets/sprites/Default size/Ships/ship (14).png"
    ]
    max_health = 2
    size = 1
    wind_effect = 1

    def on_update(self, update_event, signal):
        super().on_update(update_event, signal)
        ...


class Flotsam(ppb.Sprite):
    image = Animation("assets/sprites/Default size/Ships/sunk{1..5}.png", 2.5)

    def on_update(self, update_event, signal):
        for player_ship in update_event.scene.get(kind=Player):
            if (player_ship.position - self.position).length <= self.size:
                player_ship.pickup(self)
                update_event.scene.remove(self)
                break
