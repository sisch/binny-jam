from math import sqrt

import ppb as ppb

from effects import Splash, Explosion
import ships


class CannonBall(ppb.Sprite):
    shooter = None
    size = 0.25
    drag = 0.5
    direction = None
    damage = 0.5
    image = ppb.Image("assets/sprites/Default size/Ship parts/cannonBall.png")
    range = None
    last_position = None

    def on_update(self, update_event, signal):
        movement = self.direction * update_event.time_delta
        self.position += movement
        self.range -= movement.length
        self.direction -= self.direction*self.drag*update_event.time_delta
        self.size = min(self.range * 0.1 + self.damage/2, 1.2)
        if self.last_position is not None and self.position.isclose(self.last_position, abs_tol=0.01):
            range = -1
        if self.range <= 0:
            update_event.scene.add(Splash(position=self.position))
            self.shooter.projectiles_flying -= 1
            try:
                update_event.scene.remove(self)
            except:
                ...

        # Detect collision between Projectile and Ship
        for p in update_event.scene.get(kind=ships.Ship):
            if p == self.shooter or isinstance(p, type(self.shooter)):
                continue
            if (p.position - self.position).length <= p.size:
                print(f"Hit {p} at {p.position} with damage {self.damage}")
                update_event.scene.add(Explosion(position=self.position))
                self.shooter.projectiles_flying -= 1
                update_event.scene.remove(self)
                p.take_damage(self)
                print(f"Health after hit {p.health}")
                break
