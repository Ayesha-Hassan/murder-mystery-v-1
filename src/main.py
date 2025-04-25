import pygame
import math
import os
from core.input import keys_down, safe_remove_key
from core.camera import create_screen
from components.entity import active_objs
from core.area import Area, area
from components.sprite import sprites
from data.tile_types import tile_kinds
from components.investigation import Investigation
from components.journal import Journal
from data.case_data import SCENARIO_TITLE, SCENARIO_INTRO, CLUES
from data.layout_generator import initialize_dynamic_layout
#from core.transform import Transform
from components.player import Player

# Function to wrap text to fit within a given width
def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        width, _ = font.size(test_line)
        
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    
    if current_line:
        lines.append(current_line)
    
    return lines

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
dialogue_active = False  # Flag to track if dialogue is showing
show_dialogue_prompt = True  # Flag to show "press Enter to continue" prompt

# Variables to track clue display
current_clue = None
clue_time = 0
clue_duration = 5000  # Display clue for 5 seconds
clue_active = False  # Flag to track if clue info is showing
show_clue_prompt = True  # Flag to show "press Enter to continue" prompt

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

# Load the Groq API key from .env file if it exists
env_file = ".env"
print(f"Looking for API key in {os.path.abspath(env_file)}")

if os.path.exists(env_file):
    try:
        with open(env_file, "r") as f:
            env_content = f.read()
            print(f"Found .env file with content length: {len(env_content)} characters")
            
            for line in env_content.splitlines():
                if line.startswith("GROQ_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip('"\'')
                    masked_key = f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}" if len(api_key) > 8 else "****"
                    print(f"Found API key in .env file: {masked_key}")
                    os.environ["GROQ_API_KEY"] = api_key
                    break
            else:
                print("No GROQ_API_KEY entry found in .env file")
    except Exception as e:
        print(f"Error loading .env file: {e}")
else:
    print(".env file not found")

# Print current environment variable value (masked for security)
api_key = os.environ.get("GROQ_API_KEY", "")
if api_key:
    masked_key = f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}" if len(api_key) > 8 else "****"
    print(f"GROQ_API_KEY environment variable is set to: {masked_key}")
else:
    print("GROQ_API_KEY environment variable is not set")

# Generate dynamic layout for the game
print("Generating dynamic layout for game elements...")
initialize_dynamic_layout()

# Initialize area with the map file
area = Area("start.map", tile_kinds)

# Add variables for the accusation system
accusation_active = False
accusation_result = None
accusation_fade_start = 0
accusation_fade_duration = 1000  # Time to fade in/out accusation overlay

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
                
            # Handle Enter key for dialogue/clue dismissal
            if event.key == pygame.K_RETURN:
                if dialogue_active:
                    dialogue_active = False
                elif clue_active:
                    clue_active = False
                # If accusation is active, pressing Enter will dismiss it
                elif accusation_result:
                    accusation_result = None

            # Handle accusation system with the SPACE key
            if event.key == pygame.K_SPACE:
                # Find the player entity and get the investigation component
                player_entity = area.search_for_first(Investigation)
                if player_entity:
                    investigation = player_entity.get(Investigation)
                    if investigation and investigation.all_clues_found and investigation.all_suspects_interrogated:
                        # Only activate accusation if not already active and player has found all clues and interrogated all suspects
                        if not accusation_active and not accusation_result:
                            accusation_active = True
                            accusation_fade_start = current_time
                
            keys_down.add(event.key)
            # Debug space key press
            if event.key == pygame.K_SPACE and debug_mode:
                debug_last_space_press = current_time
                print("DEBUG: SPACE key pressed")
        elif event.type == pygame.KEYUP:
            safe_remove_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle accusation selection
            if accusation_active and event.button == 1:  # Left mouse button
                # Find the player entity and get the investigation component
                player_entity = area.search_for_first(Investigation)
                if player_entity:
                    investigation = player_entity.get(Investigation)
                    if investigation:
                        # Check if player clicked on a suspect button
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        for i, suspect in enumerate(investigation.full_suspect_data):
                            suspect_rect = pygame.Rect(
                                screen.get_width() // 2 - 150,
                                200 + i * 80,
                                300,
                                60
                            )
                            if suspect_rect.collidepoint(mouse_x, mouse_y):
                                # Handle accusation
                                from components.suspect import Suspect
                                accused = None
                                for obj in active_objs:
                                    if isinstance(obj, Suspect) and obj.name == suspect["name"]:
                                        accused = obj
                                        break
                                
                                if accused:
                                    # Set the accusation result
                                    investigation.accuse_suspect(accused)
                                    accusation_active = False
                                    accusation_result = "correct" if investigation.game_solved else "wrong"
                                    accusation_fade_start = current_time
                                    
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
                if hasattr(a, 'last_dialogue'):
                    current_dialogue = a.last_dialogue
                else:
                    current_dialogue = {
                        "name": a.name,
                        "alibi": a.alibi,
                        "testimony": a.testimony
                    }
                dialogue_time = a.last_interaction_time
                dialogue_active = True  # Activate dialogue display
        
        # Check if the object is a clue that was just discovered
        from components.clue import Clue
        if isinstance(a, Clue) and a.interacted:
            if a.discovery_time and a.discovery_time > clue_time:
                current_clue = {
                    "name": a.name,
                    "text": a.text
                }
                clue_time = a.discovery_time
                clue_active = True  # Activate clue display
    
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
                accuse_text = "Press SPACE to make an accusation"
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
                        
                        # Find the actual murder weapon
                        actual_weapon = "Bloody Rock"  # Default to the rock as the weapon
                        for clue in CLUES:
                            if "murder weapon" in clue.get("description", "").lower():
                                actual_weapon = clue["name"]
                                break
                        
                        # Create a story of what happened based on the case
                        # Get the additional info from the suspect data
                        guilty_suspect_data = None
                        for suspect_data in investigation.full_suspect_data:
                            if suspect_data["name"] == investigation.guilty_suspect.name:
                                guilty_suspect_data = suspect_data
                                break
                        
                        motive_text = "Unknown"
                        if guilty_suspect_data and "additional_info" in guilty_suspect_data:
                            motive_text = guilty_suspect_data["additional_info"]
                        
                        story_lines = [
                            f"{guilty_suspect_data['name']} was the actual murderer.",
                            f"Motive: {motive_text}",
                            f"Murder weapon: {actual_weapon}",
                            "The murder was committed at night after an argument.",
                            "Evidence including the green fabric and footprints pointed to the killer."
                        ]
                        
                        # If player selected a weapon, show if it was correct
                        if investigation.accused_weapon:
                            if investigation.accused_weapon.name == actual_weapon:
                                weapon_result = f"You correctly identified the {actual_weapon} as the murder weapon."
                            else:
                                weapon_result = f"You wrongly identified {investigation.accused_weapon.name} as the weapon. It was actually the {actual_weapon}."
                            story_lines.insert(3, weapon_result)
                        
                        y_offset = screen.get_height() // 2 + 30
                        for line in story_lines:
                            line_surface = font.render(line, True, (200, 200, 200))
                            line_surface.set_alpha(alpha)
                            screen.blit(line_surface,
                                       (screen.get_width() // 2 - line_surface.get_width() // 2,
                                        y_offset))
                            y_offset += 25
                        
                    # Hint to open journal
                    hint_text = "Open your journal (J) to review the evidence"
                    hint_surface = font.render(hint_text, True, (200, 200, 200))
                    hint_surface.set_alpha(alpha)
                    screen.blit(hint_surface,
                               (screen.get_width() // 2 - hint_surface.get_width() // 2,
                                screen.get_height() // 2 + 60))
            
            # Draw the journal if it should be visible
            journal.draw(screen, investigation)
    
    # Draw accusation UI if active
    if accusation_active:
        # Create a semi-transparent overlay for the accusation screen
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 40))  # Dark blue-ish background
        screen.blit(overlay, (0, 0))
        
        # Draw the accusation title
        accusation_title = "Whom do you accuse of the murder?"
        accusation_title_surface = outcome_font.render(accusation_title, True, (255, 255, 255))
        screen.blit(accusation_title_surface, 
                    (screen.get_width() // 2 - accusation_title_surface.get_width() // 2, 100))
        
        # Find the player entity and get the investigation component
        player_entity = area.search_for_first(Investigation)
        if player_entity:
            investigation = player_entity.get(Investigation)
            if investigation:
                # Track which suspect was clicked (if any)
                selected_suspect = None
                
                # Draw buttons for each suspect
                for i, suspect in enumerate(investigation.full_suspect_data):
                    # Create suspect button
                    suspect_rect = pygame.Rect(
                        screen.get_width() // 2 - 150,
                        200 + i * 80,
                        300,
                        60
                    )
                    
                    # Check if mouse is hovering over button
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    button_color = (100, 50, 50) if suspect_rect.collidepoint(mouse_x, mouse_y) else (60, 30, 30)
                    
                    # Draw button
                    pygame.draw.rect(screen, button_color, suspect_rect)
                    pygame.draw.rect(screen, (200, 150, 100), suspect_rect, 2)  # Button border
                    
                    # Draw suspect name
                    suspect_name_surface = dialog_font.render(suspect["name"], True, (255, 255, 255))
                    screen.blit(suspect_name_surface, 
                                (suspect_rect.x + suspect_rect.width // 2 - suspect_name_surface.get_width() // 2,
                                 suspect_rect.y + suspect_rect.height // 2 - suspect_name_surface.get_height() // 2))
                    
                    # If this suspect was clicked, set as selected
                    if suspect_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
                        selected_suspect = suspect
                
                # Draw instruction
                instruction_text = "Click on the name of the suspect you want to accuse"
                instruction_surface = font.render(instruction_text, True, (200, 200, 200))
                screen.blit(instruction_surface,
                            (screen.get_width() // 2 - instruction_surface.get_width() // 2, 550))
                
                # If a suspect was selected, show the weapon selection
                if selected_suspect and pygame.mouse.get_pressed()[0]:
                    # Draw weapon selection title
                    weapon_title = "Select the murder weapon:"
                    weapon_title_surface = dialog_font.render(weapon_title, True, (255, 255, 255))
                    screen.blit(weapon_title_surface, 
                                (screen.get_width() // 2 - weapon_title_surface.get_width() // 2, 450))
                    
                    # Draw weapon options (use clues as potential weapons)
                    weapons = investigation.discovered_clues
                    
                    for i, clue in enumerate(weapons):
                        # Create weapon button
                        weapon_rect = pygame.Rect(
                            screen.get_width() // 2 - 200,
                            500 + i * 50,
                            400,
                            40
                        )
                        
                        # Check if mouse is hovering over button
                        button_color = (70, 70, 90) if weapon_rect.collidepoint(mouse_x, mouse_y) else (50, 50, 70)
                        
                        # Draw button
                        pygame.draw.rect(screen, button_color, weapon_rect)
                        pygame.draw.rect(screen, (150, 150, 200), weapon_rect, 2)  # Button border
                        
                        # Draw weapon name
                        weapon_name_surface = font.render(clue.name, True, (255, 255, 255))
                        screen.blit(weapon_name_surface, 
                                    (weapon_rect.x + 20,
                                     weapon_rect.y + weapon_rect.height // 2 - weapon_name_surface.get_height() // 2))
                        
                        # If weapon was clicked, submit the accusation
                        if weapon_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
                            # Find the suspect object
                            from components.suspect import Suspect
                            accused = None
                            for obj in active_objs:
                                if isinstance(obj, Suspect) and obj.name == selected_suspect["name"]:
                                    accused = obj
                                    break
                            
                            if accused:
                                # Set the accusation result
                                investigation.accuse_suspect(accused, clue)
                                accusation_active = False
                                accusation_result = "correct" if investigation.game_solved else "wrong"
                                accusation_fade_start = current_time
    
    # Show accusation result if available
    if accusation_result:
        # Create a semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Find the player entity and get the investigation component
        player_entity = area.search_for_first(Investigation)
        if player_entity:
            investigation = player_entity.get(Investigation)
            if investigation and investigation.accused_suspect:
                # Draw result title
                if accusation_result == "correct":
                    result_text = "CASE SOLVED!"
                    result_color = (0, 255, 0)  # Green for success
                    sub_text = f"You correctly identified {investigation.accused_suspect.name} as the murderer!"
                else:
                    result_text = "CASE FAILED!"
                    result_color = (255, 50, 50)  # Red for failure
                    sub_text = f"You wrongly accused {investigation.accused_suspect.name}!"
                
                # Calculate fade in effect
                time_since_accusation = current_time - accusation_fade_start
                fade_progress = min(1.0, time_since_accusation / accusation_fade_duration)
                alpha = int(255 * fade_progress)
                
                # Draw main result text
                result_surface = outcome_font.render(result_text, True, result_color)
                result_surface.set_alpha(alpha)
                screen.blit(result_surface, 
                           (screen.get_width() // 2 - result_surface.get_width() // 2, 
                            screen.get_height() // 2 - 100))
                
                # Draw sub text
                sub_surface = dialog_font.render(sub_text, True, (255, 255, 255))
                sub_surface.set_alpha(alpha)
                screen.blit(sub_surface,
                           (screen.get_width() // 2 - sub_surface.get_width() // 2,
                            screen.get_height() // 2 - 50))
                
                # Find the actual murderer
                guilty_suspect = None
                for suspect_data in investigation.full_suspect_data:
                    if suspect_data.get("guilty", False):
                        guilty_suspect = suspect_data
                        break
                
                if guilty_suspect:
                    # Draw what actually happened
                    actual_header = "What Actually Happened:"
                    actual_header_surface = dialog_font.render(actual_header, True, (255, 215, 0))  # Gold color
                    actual_header_surface.set_alpha(alpha)
                    screen.blit(actual_header_surface,
                               (screen.get_width() // 2 - actual_header_surface.get_width() // 2,
                                screen.get_height() // 2))
                    
                    # Find the actual murder weapon
                    actual_weapon = "Bloody Rock"  # Default to the rock as the weapon
                    for clue in CLUES:
                        if "murder weapon" in clue.get("description", "").lower():
                            actual_weapon = clue["name"]
                            break
                    
                    # Create a story of what happened based on the case
                    # Get the additional info from the suspect data
                    guilty_suspect_data = None
                    for suspect_data in investigation.full_suspect_data:
                        if suspect_data["name"] == investigation.guilty_suspect.name:
                            guilty_suspect_data = suspect_data
                            break
                    
                    motive_text = "Unknown"
                    if guilty_suspect_data and "additional_info" in guilty_suspect_data:
                        motive_text = guilty_suspect_data["additional_info"]
                    
                    story_lines = [
                        f"{guilty_suspect_data['name']} was the actual murderer.",
                        f"Motive: {motive_text}",
                        f"Murder weapon: {actual_weapon}",
                        "The murder was committed at night after an argument.",
                        "Evidence including the green fabric and footprints pointed to the killer."
                    ]
                    
                    # If player selected a weapon, show if it was correct
                    if investigation.accused_weapon:
                        if investigation.accused_weapon.name == actual_weapon:
                            weapon_result = f"You correctly identified the {actual_weapon} as the murder weapon."
                        else:
                            weapon_result = f"You wrongly identified {investigation.accused_weapon.name} as the weapon. It was actually the {actual_weapon}."
                        story_lines.insert(3, weapon_result)
                    
                    y_offset = screen.get_height() // 2 + 30
                    for line in story_lines:
                        line_surface = font.render(line, True, (200, 200, 200))
                        line_surface.set_alpha(alpha)
                        screen.blit(line_surface,
                                   (screen.get_width() // 2 - line_surface.get_width() // 2,
                                    y_offset))
                        y_offset += 25
                
                # Draw dismissal hint
                hint_text = "Press Enter to continue"
                hint_surface = font.render(hint_text, True, (200, 200, 200))
                hint_surface.set_alpha(alpha)
                screen.blit(hint_surface,
                           (screen.get_width() // 2 - hint_surface.get_width() // 2,
                            screen.get_height() // 2 + 120))
    
    # Only show dialogue and clue popups if journal is not open and game is not solved/lost
    if not journal.visible and player_entity:
        investigation = player_entity.get(Investigation)
        
        if not (investigation and (investigation.game_solved or investigation.game_lost)):
            # Display current dialogue if it exists and dialogue is active
            if current_dialogue and dialogue_active:
                # Create a semi-transparent background for the dialogue
                dialog_bg = pygame.Surface((screen.get_width() - 100, 220))  # Made taller for prompt
                dialog_bg.set_alpha(230)  # Increased opacity from 200 to 230
                dialog_bg.fill((0, 0, 0))
                screen.blit(dialog_bg, (50, 450))  # Moved up from 520 to 450
                
                # Display suspect name
                name_text = f"Speaking with {current_dialogue['name']}"
                name_surface = dialog_font.render(name_text, True, (255, 255, 0))
                screen.blit(name_surface, (60, 460))  # Adjusted for new y position
                
                # Display personality snippet if available
                y_offset = 490  # Adjusted for new y position
                if 'personality_snippet' in current_dialogue:
                    notice_text = "You notice: "
                    notice_surface = dialog_font.render(notice_text, True, (180, 180, 255))
                    screen.blit(notice_surface, (60, y_offset))
                    
                    # Word wrap for personality snippet
                    max_width = dialog_bg.get_width() - 150
                    lines = wrap_text(current_dialogue['personality_snippet'], dialog_font, max_width)
                    for line in lines:
                        line_surface = dialog_font.render(line, True, (180, 180, 255))
                        screen.blit(line_surface, (60 + notice_surface.get_width(), y_offset))
                        y_offset += line_surface.get_height() + 2
                    
                    y_offset += 5
                
                # Display alibi with word wrapping
                alibi_label = "Alibi: "
                alibi_surface = dialog_font.render(alibi_label, True, (255, 255, 255))
                screen.blit(alibi_surface, (60, y_offset))
                
                # Word wrap the alibi text
                max_width = dialog_bg.get_width() - 150
                lines = wrap_text(current_dialogue['alibi'], dialog_font, max_width)
                for i, line in enumerate(lines):
                    line_surface = dialog_font.render(line, True, (255, 255, 255))
                    screen.blit(line_surface, (60 + alibi_surface.get_width() if i == 0 else 60 + 20, y_offset))
                    y_offset += line_surface.get_height() + 2
                
                y_offset += 5
                
                # Display testimony with word wrapping
                testimony_label = "Testimony: "
                testimony_surface = dialog_font.render(testimony_label, True, (255, 255, 255))
                screen.blit(testimony_surface, (60, y_offset))
                
                # Word wrap the testimony text
                lines = wrap_text(current_dialogue['testimony'], dialog_font, max_width)
                for i, line in enumerate(lines):
                    line_surface = dialog_font.render(line, True, (255, 255, 255))
                    screen.blit(line_surface, (60 + testimony_surface.get_width() if i == 0 else 60 + 20, y_offset))
                    y_offset += line_surface.get_height() + 2
                
                # Show a hint about the journal
                hint_text = " "
                hint_surface = font.render(hint_text, True, (180, 180, 180))
                screen.blit(hint_surface, (60, 640))  # Adjusted for new y position
                
                # Show "press Enter to continue" prompt with blinking effect
                alpha = int(127 + 127 * abs(math.sin(current_time / 500)))
                prompt_text = "Press Enter to continue"
                prompt_surface = font.render(prompt_text, True, (255, 255, 255))
                prompt_surface.set_alpha(alpha)
                screen.blit(prompt_surface, (screen.get_width() // 2 - prompt_surface.get_width() // 2, 630))  # Adjusted for new y position
            
            # Display current clue if it exists and clue display is active
            if current_clue and clue_active:
                # Create a semi-transparent background for the clue info
                clue_bg = pygame.Surface((screen.get_width() - 100, 120))
                clue_bg.set_alpha(230)  # Increased opacity from 200 to 230
                clue_bg.fill((0, 0, 0))
                screen.blit(clue_bg, (50, 320))  # Moved up from 380 to 320
                
                # Display clue name
                clue_name_text = f"Clue discovered: {current_clue['name']}"
                clue_name_surface = dialog_font.render(clue_name_text, True, (255, 255, 0))
                screen.blit(clue_name_surface, (60, 330))  # Adjusted for new y position
                
                # Display clue information with word wrapping
                info_label = "Information: "
                info_surface = dialog_font.render(info_label, True, (255, 255, 255))
                screen.blit(info_surface, (60, 365))  # Adjusted for new y position
                
                # Word wrap the clue text
                max_width = clue_bg.get_width() - 150
                lines = wrap_text(current_clue['text'], dialog_font, max_width)
                y_offset = 365  # Adjusted for new y position
                for i, line in enumerate(lines):
                    line_surface = dialog_font.render(line, True, (255, 255, 255))
                    screen.blit(line_surface, (60 + info_surface.get_width() if i == 0 else 60 + 20, y_offset))
                    y_offset += line_surface.get_height() + 2
                
                # Show "press Enter to continue" prompt with blinking effect
                alpha = int(127 + 127 * abs(math.sin(current_time / 500)))
                prompt_text = "Press Enter to continue"
                prompt_surface = font.render(prompt_text, True, (255, 255, 255))
                prompt_surface.set_alpha(alpha)
                screen.blit(prompt_surface, (screen.get_width() // 2 - prompt_surface.get_width() // 2, 420))  # Adjusted for new y position
    
    pygame.display.flip()

    # Cap the frames
    pygame.time.delay(17)


# Break down Pygame
pygame.quit()