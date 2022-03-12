from dataclasses import dataclass

import ppb
from ppb import Scene
from ppb.gomlib import GameObject


@dataclass
class AnimationLooped:
    scene: Scene = None
