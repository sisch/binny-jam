import ppb

from ppb.features.animation import Animation

from events import AnimationLooped


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


class Explosion(ppb.Sprite):
    image = Animation("assets/sprites/Effects/explosion{1..3}.png", 3)
    size = 1
    timer = 0
    run_once = True
    def __init__(self, **props):
        super().__init__(**props)
        self.duration = self.image.number_of_frames() / self.image.frames_per_second

    def on_update(self, event, signal):
        if self.timer >= self.duration:
            signal(AnimationLooped())
        self.timer += event.time_delta

    def on_animation_looped(self, event, signal):
        if self.run_once:
            event.scene.remove(self)
