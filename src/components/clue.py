from components.entity import active_objs
from components.physics import Body
import pygame

class Clue:
    def __init__(self, clue_text, clue_name):
        self.entity = None
        self.interacted = False
        self.text = clue_text
        self.name = clue_name
        self.discovery_time = None
        active_objs.append(self)
        
    def update(self):
        # Check if player is nearby and pressing interact key
        from components.player import Player
        from core.input import keys_down
        
        player_entity = None
        for obj in active_objs:
            if isinstance(obj, Player):
                player_entity = obj.entity
                break
        
        if player_entity is None:
            return
        
        # Get the body components
        player_body = player_entity.get(Body)
        self_body = self.entity.get(Body)
        
        if player_body and self_body:
            # Check if player is close enough to interact (within 64 pixels)
            player_x, player_y = player_entity.x + player_body.hitbox.x, player_entity.y + player_body.hitbox.y
            self_x, self_y = self.entity.x + self_body.hitbox.x, self.entity.y + self_body.hitbox.y
            
            distance = ((player_x - self_x) ** 2 + (player_y - self_y) ** 2) ** 0.5
            
            # If player is close enough and presses E key (interact)
            if distance < 64 and pygame.K_e in keys_down and not self.interacted:
                self.interact()
    
    def interact(self):
        self.interacted = True
        self.discovery_time = pygame.time.get_ticks()
        print(f"Clue discovered: {self.name}")
        print(f"Information: {self.text}")
        
        # Add this clue to the investigation
        from components.investigation import Investigation
        from components.player import Player
        
        # Find the player and get their investigation component
        for obj in active_objs:
            if isinstance(obj, Player):
                player_entity = obj.entity
                # Find the investigation component
                for e in player_entity.components:
                    if hasattr(e, 'add_clue'):
                        e.add_clue(self)
                        break
                break 