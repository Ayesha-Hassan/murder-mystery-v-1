from components.entity import Entity
from components.sprite import Sprite
from components.player import Player
from components.physics import Body
from components.teleporter import Teleporter
from components.clue import Clue
from components.suspect import Suspect
from components.investigation import Investigation


entity_factories = [
    # 0
    lambda args: Entity(Player(), Sprite("player.png"), Body(8, 48, 16, 16), Investigation()),

    # 1
    lambda args: Entity(Sprite("tree.png"), Body(16, 96, 32, 32)),      

    # 2
    lambda args: Entity(Sprite("rock.png"), Body()), 

    # 3
    lambda args: Entity(Teleporter(args[0], args[1], args[2]), Sprite("teleporter_up.png")),

    # 4
    lambda args: Entity(Teleporter(args[0], args[1], args[2]), Sprite("teleporter_right.png")),

    # 5
    lambda args: Entity(Teleporter(args[0], args[1], args[2]), Sprite("teleporter_down.png")),

    # 6
    lambda args: Entity(Teleporter(args[0], args[1], args[2]), Sprite("teleporter_left.png")),
    
    # 7 - Clue entity
    lambda args: Entity(Clue(args[0], args[1]), Sprite("clue.png"), Body(0, 0, 32, 32)),
    
    # 8 - Suspect entity
    lambda args: Entity(Suspect(args[0], args[1], args[2], args[3] == "true"), Sprite(args[4]), Body(8, 48, 16, 16)),
]

def create_entity(id, x, y, data=None):
    factory = entity_factories[id]
    e = factory(data)
    e.x = x*32
    e.y = y*32
    return e

        