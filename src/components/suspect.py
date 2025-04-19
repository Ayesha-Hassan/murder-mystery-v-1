from components.entity import active_objs
from components.physics import Body
import pygame

class Suspect:
    def __init__(self, name, alibi, testimony, guilty=False):
        self.entity = None
        self.name = name
        self.alibi = alibi
        self.testimony = testimony
        self.guilty = guilty
        self.interrogated = False
        self.last_interaction_time = 0
        active_objs.append(self)
    
    def update(self):
        # Check if player is nearby and pressing interact key
        from components.player import Player
        from core.input import keys_down
        
        current_time = pygame.time.get_ticks()
        
        # If we've recently interacted, don't allow another interaction for 2 seconds
        if current_time - self.last_interaction_time < 2000:
            return
            
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
            
            # If player is close enough and presses space key (interact)
            if distance < 64 and pygame.K_e in keys_down:
                self.interact()
                self.last_interaction_time = current_time
    
    def interact(self):
        self.interrogated = True
        print(f"Speaking with suspect: {self.name}")
        print(f"Alibi: {self.alibi}")
        print(f"Testimony: {self.testimony}")
        
        # Add this suspect's testimony to the investigation
        from components.investigation import Investigation
        from components.player import Player
        
        # Find the player and get their investigation component
        for obj in active_objs:
            if isinstance(obj, Player):
                player_entity = obj.entity
                # Find the investigation component
                for e in player_entity.components:
                    if hasattr(e, 'add_suspect_testimony'):
                        e.add_suspect_testimony(self)
                        break
                break 