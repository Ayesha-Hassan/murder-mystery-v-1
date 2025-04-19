import pygame
import math
from core.input import keys_down, safe_remove_key
from core.camera import create_screen
from components.entity import active_objs
from core.area import Area, area
from components.sprite import sprites
from data.tile_types import tile_kinds
from components.investigation import Investigation
from components.journal import Journal
from data.case_data import SCENARIO_TITLE, SCENARIO_INTRO

#hellooooooooo
# Set up 
pygame.init()

pygame.display.set_caption("Murder Mystery Adventure")
screen = create_screen(1280, 720, "Murder Mystery Adventure")

# Setup font for UI
font = pygame.font.SysFont(None, 24)
dialog_font = pygame.font.SysFont(None, 28)
outcome_font = pygame.font.SysFont(None, 48)
intro_font = pygame.font.SysFont(None, 26)
title_font = pygame.font.SysFont(None, 40)

clear_color = (30, 150, 240)
running = True

# Variables to track dialogue display
current_dialogue = None
dialogue_time = 0
dialogue_duration = 5000  # Display dialogue for 5 seconds

# Variables to track clue display
current_clue = None
clue_time = 0
clue_duration = 5000  # Display clue for 5 seconds

# Create journal system
journal = Journal()

# Variables for game outcome display
outcome_fade_start = 0
outcome_fade_duration = 3000  # Time to fade in/out outcome display

# Debug variables
debug_last_space_press = 0
debug_mode = False  # Set to True to enable debug messages

# Scenario intro variables
showing_intro = True
intro_start_time = pygame.time.get_ticks()
intro_duration = 15000  # Show intro for 15 seconds
dismiss_intro_message = "Press any key to continue"

# Initialize area with the map file
area = Area("start.map", tile_kinds)

# Game Loop
while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # If showing intro, any key will dismiss it
            if showing_intro:
                showing_intro = False
                
            keys_down.add(event.key)
            # Debug space key press
            if event.key == pygame.K_SPACE and debug_mode:
                debug_last_space_press = current_time
                print("DEBUG: SPACE key pressed")
        elif event.type == pygame.KEYUP:
            safe_remove_key(event.key)

    # Show scenario intro if needed
    if showing_intro:
        # Check if intro duration has elapsed
        if current_time - intro_start_time > intro_duration:
            showing_intro = False
        else:
            # Draw intro screen
            screen.fill((0, 0, 0))  # Black background
            
            # Draw title
            title_text = SCENARIO_TITLE
            title_surface = title_font.render(title_text, True, (255, 215, 0))  # Gold color
            screen.blit(title_surface, (screen.get_width() // 2 - title_surface.get_width() // 2, 100))
            
            # Draw intro text with word wrap
            lines = []
            words = SCENARIO_INTRO.split()
            line = ""
            max_width = screen.get_width() - 200
            
            for word in words:
                test_line = line + word + " "
                test_surface = intro_font.render(test_line, True, (255, 255, 255))
                
                if test_surface.get_width() > max_width:
                    lines.append(line)
                    line = word + " "
                else:
                    line = test_line
                    
            if line:
                lines.append(line)
                
            y_offset = 180
            for line in lines:
                line_surface = intro_font.render(line, True, (255, 255, 255))
                screen.blit(line_surface, (100, y_offset))
                y_offset += 30
                
            # Draw dismiss message
            # Make it blink by varying alpha based on time
            alpha = int(127 + 127 * abs(math.sin(current_time / 500)))
            dismiss_surface = intro_font.render(dismiss_intro_message, True, (200, 200, 200))
            dismiss_surface.set_alpha(alpha)
            screen.blit(dismiss_surface, (screen.get_width() // 2 - dismiss_surface.get_width() // 2, 600))
            
            pygame.display.flip()
            pygame.time.delay(17)
            continue  # Skip the rest of the loop

    # Update Code
    for a in active_objs:
        a.update()
        
        # Check if the object is a suspect with dialogue
        from components.suspect import Suspect
        if isinstance(a, Suspect) and a.interrogated:
            if a.last_interaction_time > dialogue_time:
                current_dialogue = {
                    "name": a.name,
                    "alibi": a.alibi,
                    "testimony": a.testimony
                }
                dialogue_time = a.last_interaction_time
        
        # Check if the object is a clue that was just discovered
        from components.clue import Clue
        if isinstance(a, Clue) and a.interacted:
            if a.discovery_time and a.discovery_time > clue_time:
                current_clue = {
                    "name": a.name,
                    "text": a.text
                }
                clue_time = a.discovery_time
    
    # Update journal
    journal.update()

    # Draw Code
    screen.fill(clear_color)
    area.map.draw(screen)
    for s in sprites:
        s.draw(screen)
        
    # Draw UI for investigation status
    # Find the player entity and get the investigation component
    player_entity = area.search_for_first(Investigation)
    if player_entity:
        investigation = player_entity.get(Investigation)
        
        # Display investigation status
        if investigation:
            # Show clue count
            clue_text = f"Clues found: {len(investigation.discovered_clues)}/{len(SCENARIO_INTRO.split('clues'))}"
            clue_surface = font.render(clue_text, True, (255, 255, 255))
            screen.blit(clue_surface, (10, 10))
            
            # Show suspect count
            suspect_text = f"Suspects interviewed: {len(investigation.interrogated_suspects)}/3"
            suspect_surface = font.render(suspect_text, True, (255, 255, 255))
            screen.blit(suspect_surface, (10, 40))
            
            # Debug information
            if debug_mode and investigation.all_clues_found and investigation.all_suspects_interrogated:
                ready_text = "READY TO ACCUSE - Press SPACE near a suspect"
                ready_surface = font.render(ready_text, True, (255, 255, 0))
                screen.blit(ready_surface, (10, 70))
                
                if current_time - debug_last_space_press < 2000:  # Show for 2 seconds after SPACE press
                    space_pressed_text = "SPACE KEY PRESSED!"
                    space_pressed_surface = font.render(space_pressed_text, True, (0, 255, 0))
                    screen.blit(space_pressed_surface, (10, 100))
            
            # Show instructions
            instruction_text = "Press E to interact with clues and suspects"
            instruction_surface = font.render(instruction_text, True, (255, 255, 255))
            screen.blit(instruction_surface, (10, 680))
            
            # Add accusation instruction if player has found all clues and interrogated all suspects
            if investigation.all_clues_found and investigation.all_suspects_interrogated:
                accuse_text = "Press SPACE near a suspect to accuse them of the murder"
                accuse_surface = font.render(accuse_text, True, (255, 200, 0))
                screen.blit(accuse_surface, (10, 650))
            
            # Track the beginning of outcome display
            if (investigation.game_solved or investigation.game_lost) and outcome_fade_start == 0:
                outcome_fade_start = current_time
            
            # Show case result if the game is solved or lost
            if investigation.game_solved or investigation.game_lost:
                # Calculate fade alpha based on time since outcome
                time_since_outcome = current_time - outcome_fade_start
                fade_progress = min(1.0, time_since_outcome / outcome_fade_duration)
                alpha = int(255 * fade_progress)
                
                # Create full-screen semi-transparent overlay
                if not journal.visible:  # Don't show overlay if journal is open
                    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
                    overlay.set_alpha(min(180, alpha))
                    overlay.fill((0, 0, 0))
                    screen.blit(overlay, (0, 0))
                    
                    # Display outcome message
                    if investigation.game_solved:
                        outcome_text = "CASE SOLVED!"
                        outcome_color = (0, 255, 0)  # Green for success
                        
                        sub_text = f"You correctly identified {investigation.accused_suspect.name} as the murderer!"
                    else:
                        outcome_text = "CASE FAILED!"
                        outcome_color = (255, 50, 50)  # Red for failure
                        
                        sub_text = f"You wrongly accused {investigation.accused_suspect.name}!"
                    
                    # Primary outcome text
                    outcome_surface = outcome_font.render(outcome_text, True, outcome_color)
                    outcome_surface.set_alpha(alpha)
                    screen.blit(outcome_surface, 
                               (screen.get_width() // 2 - outcome_surface.get_width() // 2, 
                                screen.get_height() // 2 - 50))
                    
                    # Secondary outcome text
                    if investigation.accused_suspect:
                        sub_surface = dialog_font.render(sub_text, True, (255, 255, 255))
                        sub_surface.set_alpha(alpha)
                        screen.blit(sub_surface,
                                   (screen.get_width() // 2 - sub_surface.get_width() // 2,
                                    screen.get_height() // 2 + 10))
                        
                    # Hint to open journal
                    hint_text = "Open your journal (J) to review the evidence"
                    hint_surface = font.render(hint_text, True, (200, 200, 200))
                    hint_surface.set_alpha(alpha)
                    screen.blit(hint_surface,
                               (screen.get_width() // 2 - hint_surface.get_width() // 2,
                                screen.get_height() // 2 + 60))
            
            # Draw the journal if it should be visible
            journal.draw(screen, investigation)
    
    # Only show dialogue and clue popups if journal is not open and game is not solved/lost
    if not journal.visible and player_entity:
        investigation = player_entity.get(Investigation)
        
        if not (investigation and (investigation.game_solved or investigation.game_lost)):
            # Display current dialogue if it exists and is within the time window
            if current_dialogue and current_time - dialogue_time < dialogue_duration:
                # Create a semi-transparent background for the dialogue
                dialog_bg = pygame.Surface((screen.get_width() - 100, 150))
                dialog_bg.set_alpha(200)
                dialog_bg.fill((0, 0, 0))
                screen.blit(dialog_bg, (50, 550))
                
                # Display suspect name
                name_text = f"Speaking with {current_dialogue['name']}"
                name_surface = dialog_font.render(name_text, True, (255, 255, 0))
                screen.blit(name_surface, (60, 560))
                
                # Display alibi
                alibi_text = f"Alibi: {current_dialogue['alibi']}"
                alibi_surface = dialog_font.render(alibi_text, True, (255, 255, 255))
                screen.blit(alibi_surface, (60, 595))
                
                # Display testimony
                testimony_text = f"Testimony: {current_dialogue['testimony']}"
                testimony_surface = dialog_font.render(testimony_text, True, (255, 255, 255))
                screen.blit(testimony_surface, (60, 630))
            
            # Display current clue if it exists and is within the time window
            if current_clue and current_time - clue_time < clue_duration:
                # Create a semi-transparent background for the clue info
                clue_bg = pygame.Surface((screen.get_width() - 100, 100))
                clue_bg.set_alpha(200)
                clue_bg.fill((0, 0, 0))
                screen.blit(clue_bg, (50, 430))
                
                # Display clue name
                clue_name_text = f"Clue discovered: {current_clue['name']}"
                clue_name_surface = dialog_font.render(clue_name_text, True, (255, 255, 0))
                screen.blit(clue_name_surface, (60, 440))
                
                # Display clue information
                clue_info_text = f"Information: {current_clue['text']}"
                clue_info_surface = dialog_font.render(clue_info_text, True, (255, 255, 255))
                screen.blit(clue_info_surface, (60, 480))
    
    pygame.display.flip()

    # Cap the frames
    pygame.time.delay(17)


# Break down Pygame
pygame.quit()