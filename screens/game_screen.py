import pygame
from .base_screen import Screen
from entities.player import Player
from ui.pause_modal import PauseModal

class GameScreen(Screen):
    def __init__(self, game, level=1):
        super().__init__(game)
        self.level = level
        self.pause_modal = None
        
        # Background (scaled if needed)
        background_raw = pygame.image.load("background.jpg").convert()
        if background_raw.get_width() != game.WIDTH or background_raw.get_height() != game.HEIGHT:
            self.background = pygame.transform.smoothscale(background_raw, (game.WIDTH, game.HEIGHT))
        else:
            self.background = background_raw
            
        self.player = Player((game.WIDTH // 2, game.HEIGHT // 2))
        self.all_sprites = pygame.sprite.Group(self.player)
        self.world_rect = self.screen.get_rect()
        
        # Create level text
        self.font = pygame.font.Font(None, 36)
        self.level_text = self.font.render(f"Level {level}", True, (255, 255, 255))
        self.level_text_rect = self.level_text.get_rect(topleft=(20, 20))
        
        # Hide cursor for game
        pygame.mouse.set_visible(False)
        
    def update(self, dt):
        if self.pause_modal:
            self.pause_modal.update(dt)
        else:
            self.all_sprites.update(dt, self.world_rect)
        
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        
        # Draw level number
        self.screen.blit(self.level_text, self.level_text_rect)
        
        # Draw pause modal if active
        if self.pause_modal:
            self.pause_modal.draw(self.screen)
        
    def handle_event(self, event):
        if self.pause_modal:
            action = self.pause_modal.handle_event(event)
            if action:
                if action == "resume":
                    self.pause_modal = None
                    pygame.mouse.set_visible(False)
                elif action == "settings":
                    from .settings_screen import SettingsScreen
                    self.game.change_screen(SettingsScreen(self.game))
                elif action == "select_level":
                    from .level_selection_screen import LevelSelectionScreen
                    self.game.change_screen(LevelSelectionScreen(self.game))
                elif action == "exit":
                    pygame.quit()
                    import sys
                    sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_modal = PauseModal(self.game.WIDTH // 2, self.game.HEIGHT // 2)
            pygame.mouse.set_visible(True)