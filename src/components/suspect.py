from components.entity import active_objs
from components.physics import Body
import pygame
import random
from data.case_data import SUSPECTS
from components.dialogue_generator import dialogue_generator

class Suspect:
    def __init__(self, name, alibi, testimony, guilty=False):
        self.entity = None
        self.name = name
        self.alibi = alibi
        self.testimony = testimony
        self.guilty = guilty
        self.interrogated = False
        self.last_interaction_time = 0
        self.interaction_count = 0  # Track the number of interactions with this suspect
        
        # Find and store full personality data from case_data
        self.personality_data = next((s for s in SUSPECTS if s["name"] == name), None)
        self.personality_snippets = self._generate_personality_snippets()
        
        active_objs.append(self)
    
    def _generate_personality_snippets(self):
        """Generate short personality observations from the full personality data"""
        snippets = []
        
        if self.personality_data:
            # For appearance
            if "appearance" in self.personality_data:
                appearance = self.personality_data["appearance"]
                snippets.append(appearance.split(".")[0])  # First sentence of appearance
            
            # For speech pattern
            if "speech_pattern" in self.personality_data:
                speech = self.personality_data["speech_pattern"]
                snippets.append(speech.split(".")[0])  # First sentence of speech pattern
            
            # For personality
            if "personality" in self.personality_data:
                personality_sentences = self.personality_data["personality"].split(".")
                for sentence in personality_sentences:
                    if len(sentence.strip()) > 10:  # Only use non-empty sentences
                        snippets.append(sentence.strip())
        
        # Add some fallback snippets if we don't have data
        if not snippets:
            if self.name == "Alice Cooper":
                snippets = ["Speaks carefully, choosing words with precision", 
                           "Seems uncomfortable talking about Thomas"]
            elif self.name == "Bob Johnson":
                snippets = ["Maintains confident posture despite the situation",
                           "Keeps checking his expensive watch"]
            elif self.name == "Charlie Miller":
                snippets = ["Has bloodshot eyes and seems tired",
                           "Fidgets nervously with his jacket"]
                
        return snippets
    
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
            
            # If player is close enough and presses E key (interact)
            if distance < 64 and pygame.K_e in keys_down:
                self.interact()
                self.last_interaction_time = current_time
    
    def interact(self):
        self.interrogated = True
        print(f"Speaking with suspect: {self.name}")
        
        # Add this suspect's testimony to the investigation
        from components.investigation import Investigation
        from components.player import Player
        from data.case_data import SCENARIO_TITLE, SCENARIO_INTRO
        
        # Generate AI dialogue or use cached version
        scenario_info = {
            "title": SCENARIO_TITLE,
            "intro": SCENARIO_INTRO
        }
        
        # Generate dialogue with AI
        dialogue = dialogue_generator.generate_dialogue(
            self.name, 
            self.personality_data, 
            scenario_info,
            self.interaction_count
        )
        
        # Format the last dialogue with AI-generated content
        self.last_dialogue = {
            "name": self.name,
            "alibi": dialogue["alibi"],
            "testimony": dialogue["testimony"],
            "personality_snippet": dialogue["behavioral_cue"],
            "additional_remark": dialogue["additional_remark"],
            "emotional_state": dialogue["emotional_state"]
        }
        
        # Increment interaction count for this suspect
        self.interaction_count += 1
        
        # Debug output
        print(f"Alibi: {self.last_dialogue['alibi']}")
        print(f"Testimony: {self.last_dialogue['testimony']}")
        
        # Find the player and add testimony to investigation
        for obj in active_objs:
            if isinstance(obj, Player):
                player_entity = obj.entity
                # Find the investigation component
                for e in player_entity.components:
                    if hasattr(e, 'add_suspect_testimony'):
                        e.add_suspect_testimony(self)
                        break
                break 