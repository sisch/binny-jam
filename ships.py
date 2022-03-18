import math
import random

import ppb
from ppb.events import KeyReleased, KeyPressed
from ppb.features.animation import Animation

import config
import labels
import mathutils
from main import Indicator
from effects import Explosion
from mathutils import dot_product_as_cos, lerp_vector, rotated_vector
from weapons import CannonBall


class Ship(ppb.Sprite):
    speed = 1.0
    image = ppb.Image("assets/sprites/Default size/Ships/ship (3).png")
    image_paths = []
    left = None
    right = None
    shoot_right_key = None
    shoot_left_key = None
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
    shoot_timer = 0
    shoot_timeout = 0.5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = ppb.Image(self.image_paths[self.state])
        self.health = self.max_health
        if self.target_rotation is None:
            self.target_rotation = (self.rotation + 180) % 360

    def on_update(self, update_event, signal):
        scene = update_event.scene
        self.shoot_timer -= update_event.time_delta

        # Move
        movement = self.facing * self.speed * update_event.time_delta
        attack_angle_effect = dot_product_as_cos(self.facing, self.wind.direction)
        movement += self.wind_effect * self.facing * (max(0.5, attack_angle_effect * self.wind.speed) * update_event.time_delta)
        if dot_product_as_cos(self.facing, movement) < 0:
            movement = ppb.Vector(0, 0)
        if not self.__dict__.get("is_anchored", False):
            self.position += movement

        # Sink
        if self.health <= 0:
            # TODO: Start Splash animation and spawn pickup
            flotsam = scene.add(Flotsam(position=self.position))
            for indicator in scene.get(kind=labels.Indicator):
                if indicator.target == self:
                    indicator.target = flotsam
                    break
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

    def shoot(self, event, angle=None):
        if self.projectiles_flying >= self.max_projectiles or self.shoot_timer > 0:
            return
        rotation = angle
        if angle is None:
            if random.random() < 0.5:
                rotation = 90
            else:
                rotation = -90
        shoot_direction = rotated_vector(self.facing, rotation)
        event.scene.add(
            CannonBall(shooter=self, position=self.position + shoot_direction / shoot_direction.length * 0.5,
                       direction=shoot_direction * (self.projectile_damage + 1), range=self.projectile_range,
                       damage=self.projectile_damage))
        self.projectiles_flying += 1
        self.shoot_timer = self.shoot_timeout

    def shoot_right(self, event):
        self.shoot(event, angle=90)

    def shoot_left(self, event):
        self.shoot(event, angle=-90)


class Player(Ship):
    left = config.Keys.left
    right = config.Keys.right
    shoot_right_key = config.Keys.use
    shoot_left_key = config.Keys.swap
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
    shoot_timeout = 0.1

    def on_key_pressed(self, key_event: KeyPressed, signal):
        if key_event.key == self.left:
            self.turn_left()
        elif key_event.key == self.right:
            self.turn_right()
        elif key_event.key == self.upgrade:
            self.run_upgrade()
        elif key_event.key == self.toggle_anchor:
            self.is_anchored = not self.is_anchored
        elif key_event.key == self.shoot_right_key:
            self.shoot_right(key_event)
        elif key_event.key == self.shoot_left_key:
            self.shoot_left(key_event)


        if config.DEBUG and key_event.key == ppb.keycodes.Period:
            key_event.scene.add(labels.WonLabel())

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
    turn_timer = 0
    turn_interval = 15
    anchor_timer = 0
    anchor_interval = 25
    sight_radius = 4.0
    player_in_sight = None
    projectile_range = 2.0

    def on_update(self, update_event, signal):
        super().on_update(update_event, signal)

        # detect player
        p = update_event.scene.get(kind=Player)
        player = next(p)
        if player is not None and (player.position - self.position).length <= self.sight_radius:
            self.player_in_sight = player

        # if player is in sight follow player and do nothing else
        if self.player_in_sight is not None:
            self.is_anchored = False
            player_vector = self.player_in_sight.position - self.position
            player_target = (self.player_in_sight.position + self.player_in_sight.facing) - self.position
            self.target_rotation = (self.basis.angle(player_target) + 180) % 360
            print(f"{str(self)}, {self.target_rotation:.1f}")
            distance = player_vector.length
            if distance < self.projectile_range * 0.7:
                self.target_rotation = self.player_in_sight.rotation
                if mathutils.dot_product(self.facing, player_vector) > 0.7:  # Approaching player with side
                    self.shoot(update_event)
            if (self.player_in_sight.position - self.position).length < self.sight_radius * 5:
                self.player_in_sight = None
        else:
            self.turn_timer += update_event.time_delta
            if self.turn_timer > self.turn_interval:
                self.turn_timer -= self.turn_interval
                self.target_rotation = random.random()*360

        self.anchor_timer += update_event.time_delta

        if self.anchor_timer > self.anchor_interval:
            self.anchor_timer -= self.anchor_interval
            self.is_anchored = not self.is_anchored


class Flotsam(ppb.Sprite):
    image = Animation("assets/sprites/Default size/Ships/sunk{1..5}.png", 2.5)

    def on_update(self, update_event, signal):
        for player_ship in update_event.scene.get(kind=Player):
            if (player_ship.position - self.position).length <= self.size:
                player_ship.pickup(self)
                for indicator in update_event.scene.get(kind=labels.Indicator):
                    if indicator.target == self:
                        update_event.scene.remove(indicator)
                        break
                update_event.scene.remove(self)
                break
