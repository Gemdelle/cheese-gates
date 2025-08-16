import pygame
from .base_screen import Screen
from ui.button import Button

class TypewriterText:
    def __init__(self, text, font, color, speed=30):
        self.full_text = text
        self.current_text = ""
        self.font = font
        self.color = color
        self.char_index = 0
        self.time_per_char = 1.0 / speed  # seconds per character
        self.time_accumulated = 0
        self.completed = False
        
    def update(self, dt):
        if not self.completed:
            self.time_accumulated += dt
            chars_to_add = int(self.time_accumulated / self.time_per_char)
            if chars_to_add > 0:
                self.time_accumulated = 0
                self.char_index = min(self.char_index + chars_to_add, len(self.full_text))
                self.current_text = self.full_text[:self.char_index]
                self.completed = self.char_index >= len(self.full_text)
                
    def draw(self, screen, pos):
        text_surface = self.font.render(self.current_text, True, self.color)
        screen.blit(text_surface, pos)
        
    def skip(self):
        self.current_text = self.full_text
        self.char_index = len(self.full_text)
        self.completed = True

class TutorialStage:
    def __init__(self, title, description, image=None):
        self.title = title
        self.description = description
        self.image = image
        self.alpha = 0  # For fade transitions
        self.typewriter = None
        self.completed = False
        
    def start(self, font):
        self.typewriter = TypewriterText(self.description, font, (255, 255, 255))
        
    def update(self, dt):
        if self.typewriter:
            self.typewriter.update(dt)
            if self.typewriter.completed:
                self.completed = True

class InstructionsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Create tutorial stages
        self.stages = [
            TutorialStage(
                "Movement",
                "Use WASD or arrow keys to move your character around the maze."
            ),
            TutorialStage(
                "Objective",
                "Collect all the cheese pieces while avoiding the traps!"
            ),
            TutorialStage(
                "Power-ups",
                "Look for special power-ups that will help you on your journey."
            ),
            TutorialStage(
                "Victory",
                "Complete all levels to become the Cheese Master!"
            )
        ]
        
        self.current_stage = 0
        self.stages[0].start(self.font)
        
        # Back button
        self.back_button = Button(100, game.HEIGHT - 50, 120, 40, "Back")
        
        # Next button
        self.next_button = Button(game.WIDTH - 100, game.HEIGHT - 50, 120, 40, "Next")
        
        # Show cursor
        pygame.mouse.set_visible(True)
        
        # Transition properties
        self.transition_time = 0.5
        self.transition_timer = 0
        self.transitioning = False
        self.transition_out = False
        
    def update(self, dt):
        self.back_button.update(dt)
        self.next_button.update(dt)
        
        current = self.stages[self.current_stage]
        current.update(dt)
        
        if self.transitioning:
            self.transition_timer += dt
            progress = self.transition_timer / self.transition_time
            
            if self.transition_out:
                current.alpha = max(0, 255 * (1 - progress))
                if progress >= 1:
                    self.transition_out = False
                    self.transition_timer = 0
                    self.current_stage += 1
                    if self.current_stage < len(self.stages):
                        self.stages[self.current_stage].start(self.font)
            else:
                current.alpha = min(255, 255 * progress)
                if progress >= 1:
                    self.transitioning = False
                    
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        current = self.stages[self.current_stage]
        
        # Draw title
        title_surface = self.title_font.render(current.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.game.WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw description
        if current.typewriter:
            current.typewriter.draw(self.screen, (50, 200))
        
        # Draw buttons
        self.back_button.draw(self.screen)
        if self.current_stage < len(self.stages) - 1:
            self.next_button.draw(self.screen)
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_hovered:
                from .level_selection_screen import LevelSelectionScreen
                self.game.change_screen(LevelSelectionScreen(self.game))
            elif self.next_button.is_hovered and self.current_stage < len(self.stages) - 1:
                if not self.transitioning:
                    self.transitioning = True
                    self.transition_out = True
                    self.transition_timer = 0
                    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Skip current typewriter animation
                current = self.stages[self.current_stage]
                if current.typewriter and not current.typewriter.completed:
                    current.typewriter.skip()
            elif event.key == pygame.K_ESCAPE:
                from .level_selection_screen import LevelSelectionScreen
                self.game.change_screen(LevelSelectionScreen(self.game))