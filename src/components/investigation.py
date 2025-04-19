import pygame
from components.entity import active_objs

class Investigation:
    def __init__(self):
        self.entity = None
        self.discovered_clues = []
        self.interrogated_suspects = []
        self.game_solved = False
        self.game_lost = False
        self.all_clues_found = False
        self.all_suspects_interrogated = False
        self.accusation_time = 0
        self.accused_suspect = None
        self.debug_mode = True  # Enable debug output
        self.last_debug_time = 0
        
        # Add to active objects so update method is called
        active_objs.append(self)
        print("DEBUG: Investigation component initialized and added to active_objs")
        
    def add_clue(self, clue):
        if clue not in self.discovered_clues:
            self.discovered_clues.append(clue)
            print(f"Added clue to investigation: {clue.name}")
            self._check_progress()
    
    def add_suspect_testimony(self, suspect):
        if suspect not in self.interrogated_suspects:
            self.interrogated_suspects.append(suspect)
            print(f"Added testimony from {suspect.name}")
            self._check_progress()
    
    def _check_progress(self):
        # This method checks if the player has made enough progress
        # to solve the mystery
        from core.area import area
        
        # Check if we've found all clues
        total_clues = 0
        for entity in area.entities:
            from components.clue import Clue
            if entity.has(Clue):
                total_clues += 1
                
        if len(self.discovered_clues) == total_clues and total_clues > 0:
            self.all_clues_found = True
            print("All clues have been found!")
        
        # Check if we've interrogated all suspects
        total_suspects = 0
        guilty_suspect = None
        for entity in area.entities:
            from components.suspect import Suspect
            suspect = entity.get(Suspect)
            if suspect:
                total_suspects += 1
                if suspect.guilty:
                    guilty_suspect = suspect
        
        if len(self.interrogated_suspects) == total_suspects and total_suspects > 0:
            self.all_suspects_interrogated = True
            print("All suspects have been interrogated!")
        
        # If all clues are found and all suspects interrogated,
        # the player can make an accusation
        if self.all_clues_found and self.all_suspects_interrogated:
            print("You have all the evidence you need to solve the case!")
            print("Press SPACE key to accuse the guilty suspect when near them!")

    def update(self):
        # Periodic debug output
        current_time = pygame.time.get_ticks()
        if self.debug_mode and current_time - self.last_debug_time > 10000:  # Every 10 seconds
            print("DEBUG: Investigation update method is being called")
            self.last_debug_time = current_time
            
        from components.player import Player
        from components.suspect import Suspect
        from components.physics import Body
        from core.input import keys_down
        
        # Only allow accusation if all clues and suspects have been processed
        # and the game is not already solved or lost
        if not (self.all_clues_found and self.all_suspects_interrogated) or self.game_solved or self.game_lost:
            return
        
        # Check for SPACE key to make accusation (instead of A key)
        if pygame.K_SPACE not in keys_down:
            return
        
        # Debug message
        if self.debug_mode:
            print("DEBUG: Investigation update - SPACE key detected")
            
        # Find the player entity
        from core.area import area
        player_entity = area.search_for_first(Player)
        
        if not player_entity:
            if self.debug_mode:
                print("DEBUG: Could not find player entity")
            return
            
        # Check if player is near any suspect
        player_body = player_entity.get(Body)
        if not player_body:
            if self.debug_mode:
                print("DEBUG: Player does not have a body component")
            return
            
        if self.debug_mode:
            print(f"DEBUG: Player position: ({player_entity.x}, {player_entity.y})")
            print(f"DEBUG: Checking {len(area.entities)} entities for suspects")
            
        for e in area.entities:
            suspect = e.get(Suspect)
            if not suspect:
                continue
                
            if self.debug_mode:
                print(f"DEBUG: Found suspect {suspect.name} at position ({e.x}, {e.y})")
                
            suspect_body = e.get(Body)
            if not suspect_body:
                if self.debug_mode:
                    print(f"DEBUG: Suspect {suspect.name} does not have a body component")
                continue
                
            # Calculate distance to suspect
            player_x = player_entity.x + player_body.hitbox.x
            player_y = player_entity.y + player_body.hitbox.y
            suspect_x = e.x + suspect_body.hitbox.x
            suspect_y = e.y + suspect_body.hitbox.y
            
            distance = ((player_x - suspect_x) ** 2 + (player_y - suspect_y) ** 2) ** 0.5
            
            if self.debug_mode:
                print(f"DEBUG: Distance to {suspect.name}: {distance}")
            
            # If close enough, check if this is the guilty suspect
            if distance < 64:
                if self.debug_mode:
                    print(f"DEBUG: Making accusation against {suspect.name}")
                    
                self.accusation_time = pygame.time.get_ticks()
                self.accused_suspect = suspect
                
                if suspect.guilty:
                    print(f"You've correctly identified the murderer: {suspect.name}!")
                    print("Congratulations, you've solved the case!")
                    self.game_solved = True
                else:
                    print(f"You've accused {suspect.name}, but they're innocent!")
                    print("You failed to solve the case. The real murderer got away!")
                    self.game_lost = True 