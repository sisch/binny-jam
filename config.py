import ppb
from ppb import keycodes

DEBUG = True

number_of_enemies = 11
default_font = ppb.Font("assets/fonts/Fredoka-Regular.ttf", size=24)
large_font = ppb.Font("assets/fonts/Fredoka-Regular.ttf", size=56)

class Keys:
    left = keycodes.Left
    right = keycodes.Right
    up = keycodes.Up
    down = keycodes.Down

    jump = keycodes.Space
    use = keycodes.E
    swap = keycodes.Q

# List of additional properties
def get_upgrade():
    for upgrade in upgrade_list:
        yield upgrade
    yield {
        "max_projectiles": 1,
        "current_upgrade_level": 1,
        "projectile_range": 1
    }



upgrade_list = [
    {
        "max_projectiles": 1,
        "current_upgrade_level": 1,
        "size": 0.6,
        "projectile_range": 0.8,
        "projectile_damage": 0.7
    },
    {
        "max_health": 1,
        "health": 1,
        "max_projectiles": 1,
        "current_upgrade_level": 1,
        "image_paths": [
            "assets/sprites/Default size/Ships/ship (3).png",
            "assets/sprites/Default size/Ships/ship (9).png",
            "assets/sprites/Default size/Ships/ship (15).png"
        ],
        "wind_effect": 0.8,
        "size": 1.0,
        "projectile_range": 1.2,
        "projectile_damage": 1.0
    },
    {
        "max_projectiles": 1,
        "current_upgrade_level": 1,
        "wind_effect": 1.0,
        "size": 1.3,
        "projectile_range": 1.6,
        "projectile_damage": 1.1
    },
    {
        "max_projectiles": 1,
        "current_upgrade_level": 1,
        "size": 1.6,
        "projectile_range": 2.5,
        "projectile_damage": 1.2
    },

]
