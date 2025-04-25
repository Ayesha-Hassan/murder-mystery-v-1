import pygame
from components.entity import active_objs
from data.case_data import SUSPECTS, CLUES

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
        self.accused_weapon = None
        self.guilty_suspect = None  # Store the guilty suspect for reference
        self.debug_mode = True  # Enable debug output
        self.last_debug_time = 0
        
        # Load full suspect data from case_data.py
        self.full_suspect_data = SUSPECTS
        
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
                    self.guilty_suspect = suspect  # Store the guilty suspect
        
        if len(self.interrogated_suspects) == total_suspects and total_suspects > 0:
            self.all_suspects_interrogated = True
            print("All suspects have been interrogated!")
        
        # If all clues are found and all suspects interrogated,
        # the player can make an accusation
        if self.all_clues_found and self.all_suspects_interrogated:
            print("You have all the evidence you need to solve the case!")
            print("Press SPACE to make an accusation!")

    def update(self):
        # Periodic debug output
        current_time = pygame.time.get_ticks()
        if self.debug_mode and current_time - self.last_debug_time > 10000:  # Every 10 seconds
            print("DEBUG: Investigation update method is being called")
            self.last_debug_time = current_time
    
    def accuse_suspect(self, suspect, weapon=None):
        """
        Make an accusation against a specific suspect using a specific weapon.
        
        Args:
            suspect: The Suspect object being accused
            weapon: The Clue object identified as the murder weapon
            
        Returns:
            True if the accusation was correct, False otherwise
        """
        if self.game_solved or self.game_lost:
            return False
            
        self.accusation_time = pygame.time.get_ticks()
        self.accused_suspect = suspect
        self.accused_weapon = weapon
        
        if self.debug_mode:
            print(f"DEBUG: Making accusation against {suspect.name} with weapon {weapon.name if weapon else 'None'}")
        
        # Make sure we have a reference to the guilty suspect
        if not self.guilty_suspect:
            from core.area import area
            from components.suspect import Suspect
            for entity in area.entities:
                suspect_component = entity.get(Suspect)
                if suspect_component and suspect_component.guilty:
                    self.guilty_suspect = suspect_component
                    break
        
        # Find the correct murder weapon
        correct_weapon = "Bloody Rock"  # Default
        for clue in CLUES:
            if "murder weapon" in clue.get("description", "").lower():
                correct_weapon = clue["name"]
                break
        
        # Check if suspect is correct
        suspect_correct = suspect.guilty
        weapon_correct = weapon and weapon.name == correct_weapon
        
        # For game results, only the suspect needs to be correct
        if suspect_correct:
            print(f"You've correctly identified the murderer: {suspect.name}!")
            if weapon_correct:
                print(f"And you correctly identified the {weapon.name} as the murder weapon!")
            else:
                print(f"But the real murder weapon was the {correct_weapon}, not the {weapon.name if weapon else 'unspecified weapon'}.")
            print("Congratulations, you've solved the case!")
            self.game_solved = True
            return True
        else:
            print(f"You've accused {suspect.name}, but they're innocent!")
            print(f"The real murderer was {self.guilty_suspect.name if self.guilty_suspect else 'someone else'}!")
            if weapon and weapon.name == correct_weapon:
                print(f"However, you correctly identified the {weapon.name} as the murder weapon.")
            else:
                print(f"The real murder weapon was the {correct_weapon}, not the {weapon.name if weapon else 'unspecified weapon'}.")
            print("You failed to solve the case. The real murderer got away!")
            self.game_lost = True
            return False 