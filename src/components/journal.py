import pygame
from data.case_data import SCENARIO_TITLE, SCENARIO_INTRO, VICTIM, SUSPECT_EVIDENCE, CHARACTER_DYNAMICS

class Journal:
    def __init__(self):
        self.entity = None
        self.visible = False
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 22)
        self.last_toggle_time = 0
        self.toggle_cooldown = 300  # milliseconds
        self.current_page = 0  # 0 = clues/suspects, 1 = case details, 2 = evidence summary, 3 = personalities
        self.total_pages = 4  # Added one more page for character personalities
        
        # Scrolling system
        self.scroll_offset = 0
        self.max_scroll_offset = 0
        self.scroll_speed = 20
        self.scrollbar_active = False
        self.scrollbar_dragging = False
        self.scrollbar_rect = None
        self.scrollbar_y = 0
        
    def update(self):
        # Check for J key press to toggle journal
        from core.input import keys_down, safe_remove_key
        
        current_time = pygame.time.get_ticks()
        
        # Add a cooldown to prevent multiple toggles
        if pygame.K_j in keys_down and current_time - self.last_toggle_time > self.toggle_cooldown:
            self.toggle_visibility()
            self.last_toggle_time = current_time
            # Safely remove the key
            safe_remove_key(pygame.K_j)
            
        # Check for left/right arrow keys to navigate journal pages when visible
        if self.visible:
            if pygame.K_RIGHT in keys_down and current_time - self.last_toggle_time > self.toggle_cooldown:
                self.current_page = (self.current_page + 1) % self.total_pages
                self.scroll_offset = 0  # Reset scroll position when changing pages
                self.last_toggle_time = current_time
                safe_remove_key(pygame.K_RIGHT)
                
            if pygame.K_LEFT in keys_down and current_time - self.last_toggle_time > self.toggle_cooldown:
                self.current_page = (self.current_page - 1) % self.total_pages
                self.scroll_offset = 0  # Reset scroll position when changing pages
                self.last_toggle_time = current_time
                safe_remove_key(pygame.K_LEFT)
                
            # Scrolling with up/down keys
            if pygame.K_UP in keys_down:
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                safe_remove_key(pygame.K_UP)
                
            if pygame.K_DOWN in keys_down:
                self.scroll_offset = min(self.max_scroll_offset, self.scroll_offset + self.scroll_speed)
                safe_remove_key(pygame.K_DOWN)
                
            # Handle mouse wheel for scrolling
            mouse_wheel = pygame.mouse.get_rel()[1]
            if mouse_wheel != 0:
                self.scroll_offset = max(0, min(self.max_scroll_offset, self.scroll_offset - mouse_wheel * 5))
                
            # Handle scrollbar dragging
            if self.scrollbar_dragging:
                _, mouse_y = pygame.mouse.get_pos()
                if pygame.mouse.get_pressed()[0]:  # Left mouse button still held
                    journal_height = 520  # Height of viewable area in journal
                    content_height = self.max_scroll_offset + journal_height
                    scrollbar_height = journal_height * (journal_height / content_height)
                    
                    # Calculate new scroll position based on mouse position
                    scrollbar_top = 100 + 10  # Journal top position + padding
                    scrollbar_range = journal_height - scrollbar_height - 20  # Scrollable range
                    
                    # Calculate scroll percentage based on mouse position
                    scroll_percent = (mouse_y - scrollbar_top) / scrollbar_range
                    scroll_percent = max(0, min(1, scroll_percent))
                    
                    # Apply scroll offset
                    self.scroll_offset = int(scroll_percent * self.max_scroll_offset)
                else:
                    # Release scrollbar if mouse button is released
                    self.scrollbar_dragging = False
    
    def toggle_visibility(self):
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0  # Reset scroll position when opening journal
        
    def draw(self, screen, investigation):
        if not self.visible:
            # Only draw journal instructions when not visible
            hint_text = "Press J to open your investigation journal"
            hint_surface = self.font.render(hint_text, True, (255, 255, 255))
            screen.blit(hint_surface, (screen.get_width() - hint_surface.get_width() - 10, 10))
            return
            
        # Draw journal background
        journal_bg = pygame.Surface((screen.get_width() - 200, screen.get_height() - 200))
        journal_bg.set_alpha(230)
        journal_bg.fill((50, 40, 30))  # Brown-ish color
        
        # Add a border
        pygame.draw.rect(journal_bg, (139, 69, 19), pygame.Rect(0, 0, journal_bg.get_width(), journal_bg.get_height()), 5)
        
        # Position journal in center of screen
        journal_x = 100
        journal_y = 100
        screen.blit(journal_bg, (journal_x, journal_y))
        
        # Create a clipping rect for the content area
        content_rect = pygame.Rect(journal_x + 10, journal_y + 70, journal_bg.get_width() - 20, journal_bg.get_height() - 120)
        clip_rect = screen.get_clip()
        screen.set_clip(content_rect)
        
        # Draw different content based on current page
        self.max_scroll_offset = 0  # Reset before drawing content
        
        if self.current_page == 0:
            self.max_scroll_offset = self._draw_investigation_page(screen, journal_x, journal_y, journal_bg, investigation)
        elif self.current_page == 1:
            self.max_scroll_offset = self._draw_case_details_page(screen, journal_x, journal_y, journal_bg)
        elif self.current_page == 2:
            self.max_scroll_offset = self._draw_evidence_summary_page(screen, journal_x, journal_y, journal_bg, investigation)
        else:
            self.max_scroll_offset = self._draw_character_profiles_page(screen, journal_x, journal_y, journal_bg, investigation)
            
        # Restore clip rect
        screen.set_clip(clip_rect)
        
        # Draw page navigation indicators
        nav_text = f"Page {self.current_page + 1}/{self.total_pages} (Use arrow keys to navigate, Up/Down to scroll)"
        nav_surface = self.small_font.render(nav_text, True, (200, 200, 200))
        screen.blit(nav_surface, 
                   (journal_x + (journal_bg.get_width() - nav_surface.get_width()) // 2, 
                    journal_y + journal_bg.get_height() - 50))
        
        # Draw title based on current page
        if self.current_page == 0:
            title_text = "INVESTIGATION JOURNAL"
        elif self.current_page == 1:
            title_text = "CASE DETAILS: " + SCENARIO_TITLE
        elif self.current_page == 2:
            title_text = "EVIDENCE SUMMARY"
        else:
            title_text = "CHARACTER PROFILES"
            
        title_surface = self.title_font.render(title_text, True, (255, 215, 0))  # Gold color
        screen.blit(title_surface, (journal_x + (journal_bg.get_width() - title_surface.get_width()) // 2, journal_y + 20))
        
        # Draw close instructions
        close_text = "Press J to close journal"
        close_surface = self.font.render(close_text, True, (255, 255, 255))
        screen.blit(close_surface, 
                    (journal_x + journal_bg.get_width() - close_surface.get_width() - 20, 
                     journal_y + journal_bg.get_height() - 20))
        
        # Draw case status (if solved or lost)
        if investigation.game_solved or investigation.game_lost:
            case_status_y = journal_y + 60
            
            if investigation.game_solved:
                status_text = "CASE SOLVED! You caught the murderer!"
                status_color = (0, 255, 0)  # Green for success
            else:
                status_text = "CASE FAILED! You accused the wrong person!"
                status_color = (255, 0, 0)  # Red for failure
                
            status_surface = self.font.render(status_text, True, status_color)
            screen.blit(status_surface, (journal_x + (journal_bg.get_width() - status_surface.get_width()) // 2, case_status_y))
            
            # If we have an accused suspect, show their name
            if investigation.accused_suspect:
                accused_text = f"You accused: {investigation.accused_suspect.name}"
                accused_surface = self.font.render(accused_text, True, (255, 255, 255))
                screen.blit(accused_surface, (journal_x + (journal_bg.get_width() - accused_surface.get_width()) // 2, case_status_y + 30))
                
                # Show the weapon used if provided
                if investigation.accused_weapon:
                    weapon_text = f"With weapon: {investigation.accused_weapon.name}"
                    weapon_surface = self.font.render(weapon_text, True, (255, 255, 255))
                    screen.blit(weapon_surface, (journal_x + (journal_bg.get_width() - weapon_surface.get_width()) // 2, case_status_y + 55))
                
                # Show the actual culprit if wrong accusation
                if investigation.game_lost and investigation.guilty_suspect:
                    truth_y = case_status_y + (80 if investigation.accused_weapon else 60)
                    truth_text = f"The real murderer was: {investigation.guilty_suspect.name}"
                    truth_surface = self.font.render(truth_text, True, (255, 215, 0))  # Gold color
                    screen.blit(truth_surface, (journal_x + (journal_bg.get_width() - truth_surface.get_width()) // 2, truth_y))
                    
                    # Find the actual murder weapon
                    from data.case_data import CLUES
                    actual_weapon = "Bloody Rock"  # Default to the rock as the weapon
                    for clue in CLUES:
                        if "murder weapon" in clue.get("description", "").lower():
                            actual_weapon = clue["name"]
                            break
                    
                    # Show the actual weapon
                    actual_weapon_text = f"The murder weapon was: {actual_weapon}"
                    actual_weapon_surface = self.font.render(actual_weapon_text, True, (255, 215, 0))
                    screen.blit(actual_weapon_surface, (journal_x + (journal_bg.get_width() - actual_weapon_surface.get_width()) // 2, truth_y + 25))
                    
                    # Add more details about what happened
                    guilty_data = None
                    for suspect in investigation.full_suspect_data:
                        if suspect["name"] == investigation.guilty_suspect.name:
                            guilty_data = suspect
                            break
                    
                    if guilty_data:
                        motive_text = f"Motive: {guilty_data.get('additional_info', 'Unknown')}"
                        motive_surface = self.font.render(motive_text, True, (200, 200, 200))
                        screen.blit(motive_surface, (journal_x + 50, truth_y + 55))
                        
                        crime_text = "The murder occurred after an argument by the lake."
                        crime_surface = self.font.render(crime_text, True, (200, 200, 200))
                        screen.blit(crime_surface, (journal_x + 50, truth_y + 80))
        
        # Draw scrollbar if needed
        self._draw_scrollbar(screen, journal_x, journal_y, journal_bg)
            
    def _draw_scrollbar(self, screen, journal_x, journal_y, journal_bg):
        # Only draw scrollbar if we have content that can be scrolled
        if self.max_scroll_offset <= 0:
            self.scrollbar_active = False
            return
            
        # Calculate scrollbar position and size
        scrollbar_x = journal_x + journal_bg.get_width() - 20
        journal_height = journal_bg.get_height() - 120  # Viewable content area height
        content_height = self.max_scroll_offset + journal_height
        
        # Calculate scrollbar height (proportional to content vs visible area)
        scrollbar_height = max(30, journal_height * (journal_height / content_height))
        
        # Calculate scrollbar position based on scroll offset
        scroll_percent = self.scroll_offset / self.max_scroll_offset if self.max_scroll_offset > 0 else 0
        scrollbar_y = journal_y + 70 + (journal_height - scrollbar_height) * scroll_percent
        
        # Draw scrollbar track
        track_rect = pygame.Rect(scrollbar_x, journal_y + 70, 10, journal_height)
        pygame.draw.rect(screen, (80, 70, 60), track_rect)
        
        # Draw scrollbar handle
        self.scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, 10, scrollbar_height)
        pygame.draw.rect(screen, (180, 160, 140), self.scrollbar_rect)
        
        # Check for scrollbar interaction
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left mouse button
        
        if self.scrollbar_rect.collidepoint(mouse_x, mouse_y):
            # Highlight scrollbar on hover
            pygame.draw.rect(screen, (220, 200, 180), self.scrollbar_rect)
            if mouse_clicked and not self.scrollbar_dragging:
                self.scrollbar_dragging = True
                
        self.scrollbar_active = True
            
    def _draw_investigation_page(self, screen, journal_x, journal_y, journal_bg, investigation):
        # Draw clues section with scrolling
        base_y = journal_y + 70 - self.scroll_offset  # Starting position adjusted for scrolling
        y_offset = base_y
        
        clues_title = "EVIDENCE COLLECTED:"
        clues_title_surface = self.font.render(clues_title, True, (255, 215, 0))
        screen.blit(clues_title_surface, (journal_x + 30, y_offset))
        
        # List all collected clues
        y_offset += 40
        if not investigation.discovered_clues:
            no_clues_text = "No evidence collected yet."
            no_clues_surface = self.font.render(no_clues_text, True, (200, 200, 200))
            screen.blit(no_clues_surface, (journal_x + 50, y_offset))
            y_offset += 30
        else:
            for i, clue in enumerate(investigation.discovered_clues):
                # Clue name
                clue_text = f"{i+1}. {clue.name}"
                clue_surface = self.font.render(clue_text, True, (255, 255, 255))
                screen.blit(clue_surface, (journal_x + 50, y_offset))
                y_offset += 30
                
                # Clue description - use word wrapping
                max_width = journal_bg.get_width() - 100
                y_offset = self._draw_wrapped_text(screen, f"   {clue.text}", self.font, (200, 200, 200), 
                                               journal_x + 50, y_offset, max_width)
                y_offset += 10
        
        # Draw suspects section
        suspects_title = "SUSPECT INTERVIEWS:"
        suspects_title_surface = self.font.render(suspects_title, True, (255, 215, 0))
        screen.blit(suspects_title_surface, (journal_x + 30, y_offset))
        
        # List all interviewed suspects
        y_offset += 40
        if not investigation.interrogated_suspects:
            no_suspects_text = "No suspects interviewed yet."
            no_suspects_surface = self.font.render(no_suspects_text, True, (200, 200, 200))
            screen.blit(no_suspects_surface, (journal_x + 50, y_offset))
            y_offset += 30
        else:
            for i, suspect in enumerate(investigation.interrogated_suspects):
                # Suspect name
                suspect_text = f"{i+1}. {suspect.name}"
                suspect_surface = self.font.render(suspect_text, True, (255, 255, 255))
                screen.blit(suspect_surface, (journal_x + 50, y_offset))
                y_offset += 30
                
                # Suspect alibi - use word wrapping
                max_width = journal_bg.get_width() - 100
                alibi_label = "   Alibi: "
                alibi_label_surface = self.font.render(alibi_label, True, (200, 200, 200))
                screen.blit(alibi_label_surface, (journal_x + 50, y_offset))
                
                # Word wrap the alibi text
                y_offset = self._draw_wrapped_text(screen, suspect.alibi, self.font, (200, 200, 200),
                                              journal_x + 50 + alibi_label_surface.get_width(), y_offset, 
                                              max_width - alibi_label_surface.get_width())
                
                # Suspect testimony - use word wrapping
                testimony_label = "   Testimony: "
                testimony_label_surface = self.font.render(testimony_label, True, (200, 200, 200))
                screen.blit(testimony_label_surface, (journal_x + 50, y_offset))
                
                # Word wrap the testimony text
                y_offset = self._draw_wrapped_text(screen, suspect.testimony, self.font, (200, 200, 200),
                                              journal_x + 50 + testimony_label_surface.get_width(), y_offset,
                                              max_width - testimony_label_surface.get_width())
                y_offset += 20
        
        # Return the maximum scroll offset (total content height - visible area)
        content_height = y_offset - base_y
        visible_height = journal_bg.get_height() - 120
        return max(0, content_height - visible_height)

    def _draw_case_details_page(self, screen, journal_x, journal_y, journal_bg):
        # Draw case background
        base_y = journal_y + 70 - self.scroll_offset  # Starting position adjusted for scrolling
        y_offset = base_y
        
        # Draw scenario intro with word wrapping
        words = SCENARIO_INTRO.split()
        line = ""
        max_width = journal_bg.get_width() - 70
        
        for word in words:
            test_line = line + word + " "
            test_surface = self.small_font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() > max_width:
                text_surface = self.small_font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (journal_x + 35, y_offset))
                line = word + " "
                y_offset += 25
            else:
                line = test_line
                
        # Render the last line
        if line:
            text_surface = self.small_font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (journal_x + 35, y_offset))
            y_offset += 40
            
        # Draw victim information
        victim_title = "VICTIM: " + VICTIM["name"]
        victim_title_surface = self.font.render(victim_title, True, (255, 215, 0))
        screen.blit(victim_title_surface, (journal_x + 30, y_offset))
        y_offset += 30
        
        victim_age = f"Age: {VICTIM['age']}"
        victim_age_surface = self.small_font.render(victim_age, True, (255, 255, 255))
        screen.blit(victim_age_surface, (journal_x + 50, y_offset))
        y_offset += 25
        
        # Description with word wrapping
        words = VICTIM["description"].split()
        line = "Description: "
        max_width = journal_bg.get_width() - 100
        
        for word in words:
            test_line = line + word + " "
            test_surface = self.small_font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() > max_width:
                text_surface = self.small_font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (journal_x + 50, y_offset))
                line = "  " + word + " "  # Indent continuation line
                y_offset += 25
            else:
                line = test_line
                
        # Render the last line
        if line:
            text_surface = self.small_font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (journal_x + 50, y_offset))
            y_offset += 35
            
        # Relationships
        rel_title = "Relationships:"
        rel_title_surface = self.small_font.render(rel_title, True, (255, 255, 255))
        screen.blit(rel_title_surface, (journal_x + 50, y_offset))
        y_offset += 25
        
        for name, relationship in VICTIM["relationships"].items():
            rel_text = f"  • {name}: {relationship}"
            
            # Word wrap for each relationship
            words = rel_text.split()
            line = ""
            
            for word in words:
                test_line = line + word + " "
                test_surface = self.small_font.render(test_line, True, (200, 200, 200))
                
                if test_surface.get_width() > max_width:
                    text_surface = self.small_font.render(line, True, (200, 200, 200))
                    screen.blit(text_surface, (journal_x + 50, y_offset))
                    line = "    " + word + " "  # Additional indent for continuation
                    y_offset += 25
                else:
                    line = test_line
                    
            # Render the last line
            if line:
                text_surface = self.small_font.render(line, True, (200, 200, 200))
                screen.blit(text_surface, (journal_x + 50, y_offset))
                y_offset += 25
                
        # Return the maximum scroll offset
        content_height = y_offset - base_y
        visible_height = journal_bg.get_height() - 120
        return max(0, content_height - visible_height)

    def _draw_evidence_summary_page(self, screen, journal_x, journal_y, journal_bg, investigation):
        base_y = journal_y + 70 - self.scroll_offset  # Starting position adjusted for scrolling
        y_offset = base_y
        
        # Only show evidence summaries for suspects that have been interviewed
        interviewed_names = [suspect.name for suspect in investigation.interrogated_suspects]
        
        if not interviewed_names:
            no_evidence_text = "Interview suspects to see evidence summaries."
            no_evidence_surface = self.font.render(no_evidence_text, True, (255, 255, 255))
            screen.blit(no_evidence_surface, (journal_x + 50, y_offset))
            # Return minimal scroll offset since not much content
            return 0
            
        evidence_intro = "Evidence pointing to each suspect:"
        evidence_intro_surface = self.font.render(evidence_intro, True, (255, 255, 255))
        screen.blit(evidence_intro_surface, (journal_x + 35, y_offset))
        y_offset += 40
        
        max_width = journal_bg.get_width() - 100
        
        for suspect_name, evidence_list in SUSPECT_EVIDENCE.items():
            # Only show for interviewed suspects
            if suspect_name not in interviewed_names:
                continue
                
            # Suspect name as subheading
            suspect_heading = suspect_name
            suspect_heading_surface = self.font.render(suspect_heading, True, (255, 215, 0))
            screen.blit(suspect_heading_surface, (journal_x + 50, y_offset))
            y_offset += 30
            
            # List evidence points
            for evidence in evidence_list:
                evidence_text = f"• {evidence}"
                
                # Word wrap for each evidence point
                words = evidence_text.split()
                line = ""
                
                for word in words:
                    test_line = line + word + " "
                    test_surface = self.small_font.render(test_line, True, (200, 200, 200))
                    
                    if test_surface.get_width() > max_width:
                        text_surface = self.small_font.render(line, True, (200, 200, 200))
                        screen.blit(text_surface, (journal_x + 60, y_offset))
                        line = "  " + word + " "  # Indent continuation line
                        y_offset += 25
                    else:
                        line = test_line
                        
                # Render the last line
                if line:
                    text_surface = self.small_font.render(line, True, (200, 200, 200))
                    screen.blit(text_surface, (journal_x + 60, y_offset))
                    y_offset += 25
                    
            y_offset += 15  # Extra space between suspects 
        
        # Return the maximum scroll offset
        content_height = y_offset - base_y
        visible_height = journal_bg.get_height() - 120
        return max(0, content_height - visible_height)

    def _draw_character_profiles_page(self, screen, journal_x, journal_y, journal_bg, investigation):
        """
        Draw the character profiles page with personality details.
        This shows when self.current_page == 3
        """
        base_y = journal_y + 70 - self.scroll_offset  # Starting position adjusted for scrolling
        y_offset = base_y
        max_width = journal_bg.get_width() - 70
        
        # Add a dynamic title about relationships
        dynamics_title = "CHARACTER PERSONALITIES AND RELATIONSHIPS"
        dynamics_title_surface = self.font.render(dynamics_title, True, (200, 200, 120))
        screen.blit(dynamics_title_surface, (journal_x + 30, y_offset))
        y_offset += 40
        
        # Only show personalities for interviewed suspects
        interviewed_names = [suspect.name for suspect in investigation.interrogated_suspects]
        
        if not interviewed_names:
            no_suspects_text = "Interview suspects to reveal their profiles."
            no_suspects_surface = self.font.render(no_suspects_text, True, (200, 200, 200))
            screen.blit(no_suspects_surface, (journal_x + 50, y_offset))
            # Return minimal scroll offset since not much content
            return 0
        
        # Draw victim profile first if we've interviewed at least one suspect
        if interviewed_names:
            victim_title = f"VICTIM: {VICTIM['name']}"
            victim_title_surface = self.font.render(victim_title, True, (255, 215, 0))
            screen.blit(victim_title_surface, (journal_x + 35, y_offset))
            y_offset += 30
            
            # Display victim personality
            if "personality" in VICTIM:
                y_offset = self._draw_wrapped_text(screen, f"Personality: {VICTIM['personality']}", 
                                       self.small_font, (200, 200, 200), journal_x + 50, y_offset, max_width)
                y_offset += 30  # Extra space after victim section
        
        # Draw profiles for each interviewed suspect
        for suspect in investigation.interrogated_suspects:
            # Find the corresponding suspect data in case_data.py
            suspect_data = next((s for s in SUSPECT_EVIDENCE if s == suspect.name), None)
            full_data = next((s for s in investigation.full_suspect_data if s["name"] == suspect.name), None)
            
            if full_data:
                # Draw suspect name
                suspect_heading = f"SUSPECT: {suspect.name}"
                suspect_heading_surface = self.font.render(suspect_heading, True, (255, 215, 0))
                screen.blit(suspect_heading_surface, (journal_x + 35, y_offset))
                y_offset += 30
                
                # Display personality if available
                if "personality" in full_data:
                    y_offset = self._draw_wrapped_text(screen, f"Personality: {full_data['personality']}", 
                                           self.small_font, (200, 200, 200), journal_x + 50, y_offset, max_width)
                    y_offset += 30
                
                # Display appearance if available
                if "appearance" in full_data:
                    y_offset = self._draw_wrapped_text(screen, f"Appearance: {full_data['appearance']}", 
                                           self.small_font, (200, 200, 200), journal_x + 50, y_offset, max_width)
                    y_offset += 30
                
                # Display speech pattern if available
                if "speech_pattern" in full_data:
                    y_offset = self._draw_wrapped_text(screen, f"Speech: {full_data['speech_pattern']}", 
                                           self.small_font, (200, 200, 200), journal_x + 50, y_offset, max_width)
                    y_offset += 40  # Extra space after each suspect
        
        # Return the maximum scroll offset
        content_height = y_offset - base_y
        visible_height = journal_bg.get_height() - 120
        return max(0, content_height - visible_height)
    
    def _draw_wrapped_text(self, screen, text, font, color, x, y, max_width):
        """Helper function to draw word-wrapped text at the specified position"""
        words = text.split()
        line = ""
        y_offset = y
        
        for word in words:
            test_line = line + word + " "
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() > max_width:
                text_surface = font.render(line, True, color)
                screen.blit(text_surface, (x, y_offset))
                line = word + " "
                y_offset += 25
            else:
                line = test_line
                
        # Render the last line
        if line:
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (x, y_offset))
            
        return y_offset + 25  # Return the new y position after the text 