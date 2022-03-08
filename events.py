from dataclasses import dataclass

import ppb
from ppb import Scene


@dataclass
class AnimationLooped:
    scene: Scene = None
