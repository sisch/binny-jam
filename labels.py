import ppb
import config
import math

import ships


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
    screen_position = ppb.Vector(-9, -8.5)
    tags = ("Wind", )
    wind = None

    def on_update(self, update_event, signal):
        super().on_update(update_event, signal)
        if self.update_timer > self.update_interval:
            self.update_timer -= self.update_interval
            self.image = ppb.Text(f"Wind {self.wind.speed:.1f} knots {wind_direction(self.wind.direction)}",
                                  font=config.large_font, color=(255, 255, 255))


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


class Indicator(ppb.Sprite):
    image = ppb.Image("assets/sprites/Default size/Ship parts/flag (2).png")
    player = None
    target = None
    size = 0.2
    tags = ("Indicator", )

    def on_update(self, update_event, signal):
        if self.player is None or self.target is None:
            update_event.scene.remove(self)
        direction = (self.target.position - self.player.position).normalize()
        self.position = self.player.position + direction
        self.facing = self.target.position - self.position


class WonLabel(UILabel):
    screen_position = ppb.Vector(0, 0)
    size = 4
    image = ppb.Text("You won!", font=config.large_font, color=(180, 180, 20))


class EnemiesLeftLabel(UILabel):
    screen_position = ppb.Vector(-11, 9)

    def on_update(self, update_event, signal):
        super().on_update(update_event, signal)
        number_of_enemies = len(list(update_event.scene.get(kind=ships.Enemy)))
        if number_of_enemies == 0:
            update_event.scene.add(WonLabel())
            signal(ppb.events.ScenePaused)

        self.image = ppb.Text(f"{number_of_enemies} left", font=config.default_font, color=(255, 255, 255))
