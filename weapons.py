import ppb as ppb

from effects import Splash, Explosion
import ships


class CannonBall(ppb.Sprite):
    shooter = None
    size = 0.25
    drag = 0.5
    direction = None
    damage = 1
    image = ppb.Image("assets/sprites/Default size/Ship parts/cannonBall.png")

    def on_update(self, update_event, signal):
        self.position += self.direction * update_event.time_delta
        self.direction -= self.direction*self.drag*update_event.time_delta

        if self.direction.length < 0.3:
            update_event.scene.add(Splash(position=self.position))
            self.shooter.projectiles_flying -= 1
            update_event.scene.remove(self)

        # Detect collision between Projectile and Ship
        for p in update_event.scene.get(kind=ships.Ship):
            if p == self.shooter:
                continue
            if (p.position - self.position).length <= p.size:
                update_event.scene.add(Explosion(position=self.position))
                self.shooter.projectiles_flying -= 1
                update_event.scene.remove(self)
                p.take_damage(self)
                break
