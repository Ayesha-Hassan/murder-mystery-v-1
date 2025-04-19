import pygame

class Journal:
    def __init__(self):
        self.entity = None
        self.visible = False
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36)
        self.last_toggle_time = 0
        self.toggle_cooldown = 300  # milliseconds
        
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
    
    def toggle_visibility(self):
        self.visible = not self.visible
        
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
        
        # Draw title
        title_text = "INVESTIGATION JOURNAL"
        title_surface = self.title_font.render(title_text, True, (255, 215, 0))  # Gold color
        screen.blit(title_surface, (journal_x + (journal_bg.get_width() - title_surface.get_width()) // 2, journal_y + 20))
        
        # Draw close instructions
        close_text = "Press J to close journal"
        close_surface = self.font.render(close_text, True, (255, 255, 255))
        screen.blit(close_surface, 
                    (journal_x + journal_bg.get_width() - close_surface.get_width() - 20, 
                     journal_y + journal_bg.get_height() - close_surface.get_height() - 20))
        
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
        
        # Draw clues section
        clues_title = "EVIDENCE COLLECTED:"
        clues_title_surface = self.font.render(clues_title, True, (255, 215, 0))
        screen.blit(clues_title_surface, (journal_x + 30, journal_y + 80))
        
        # List all collected clues
        y_offset = journal_y + 120
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
                
                # Clue description
                desc_text = f"   {clue.text}"
                desc_surface = self.font.render(desc_text, True, (200, 200, 200))
                screen.blit(desc_surface, (journal_x + 50, y_offset))
                y_offset += 40
        
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
        else:
            for i, suspect in enumerate(investigation.interrogated_suspects):
                # Suspect name
                suspect_text = f"{i+1}. {suspect.name}"
                suspect_surface = self.font.render(suspect_text, True, (255, 255, 255))
                screen.blit(suspect_surface, (journal_x + 50, y_offset))
                y_offset += 30
                
                # Suspect alibi
                alibi_text = f"   Alibi: {suspect.alibi}"
                alibi_surface = self.font.render(alibi_text, True, (200, 200, 200))
                screen.blit(alibi_surface, (journal_x + 50, y_offset))
                y_offset += 30
                
                # Suspect testimony
                testimony_text = f"   Testimony: {suspect.testimony}"
                testimony_surface = self.font.render(testimony_text, True, (200, 200, 200))
                screen.blit(testimony_surface, (journal_x + 50, y_offset))
                y_offset += 40 