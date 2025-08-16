import pygame
from .base_screen import Screen
from ui.menu_modal import MenuModal

class SplashScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.background = pygame.image.load("splash.png").convert()
        self.original_bg = pygame.transform.scale(self.background, (game.WIDTH, game.HEIGHT))
        self.zoom_duration = 3.0  # seconds
        self.time_elapsed = 0
        self.show_press_enter = False
        self.menu_modal = None
        self.text_visible = True  # New variable to control text visibility
        
        # Create font for "Press Enter to Start"
        self.font = pygame.font.Font(None, 48)  # None uses default system font
        self.text_opacity = 255  # Full opacity
        self.opacity_direction = -1  # -1 fading out, 1 fading in
        self.opacity_speed = 120  # Speed of the fade animation (opacity units per second)
        self.min_opacity = 100  # Minimum opacity value
        self.max_opacity = 255  # Maximum opacity value
        self.text_rect = self.text = None
        self.update_text()
        
        # Show cursor
        pygame.mouse.set_visible(True)
        
    def update_text(self):
        """Update the text surface with current opacity"""
        self.text = self.font.render("Press Enter to Start", True, (255, 255, 255))
        # Create a surface with alpha channel
        alpha_surface = pygame.Surface(self.text.get_size(), pygame.SRCALPHA)
        # Fill with transparent color using current opacity
        alpha_surface.fill((255, 255, 255, self.text_opacity))
        # Blit using blend mode
        self.text.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if not self.text_rect:
            self.text_rect = self.text.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT - 100))

    def update(self, dt):
        if not self.show_press_enter:
            self.time_elapsed += dt
            if self.time_elapsed >= self.zoom_duration:
                self.show_press_enter = True
        
        if self.show_press_enter:
            # Update text opacity
            self.text_opacity += self.opacity_direction * self.opacity_speed * dt
            
            # Check bounds and reverse direction if needed
            if self.text_opacity <= self.min_opacity:
                self.text_opacity = self.min_opacity
                self.opacity_direction = 1
            elif self.text_opacity >= self.max_opacity:
                self.text_opacity = self.max_opacity
                self.opacity_direction = -1
            
            # Update text surface with new opacity
            self.update_text()
                
        if self.menu_modal:
            self.menu_modal.update(dt)
                
    def draw(self):
        # Calculate zoom factor
        if not self.show_press_enter:
            zoom_progress = min(self.time_elapsed / self.zoom_duration, 1.0)
            zoom_factor = 1.0 + (zoom_progress * 0.2)  # Zoom in by 20%
            
            # Calculate new size
            new_width = int(self.game.WIDTH * zoom_factor)
            new_height = int(self.game.HEIGHT * zoom_factor)
            
            # Create zoomed surface
            zoomed = pygame.transform.smoothscale(self.original_bg, (new_width, new_height))
            
            # Calculate position to keep centered
            x = (self.game.WIDTH - new_width) // 2
            y = (self.game.HEIGHT - new_height) // 2
            
            self.screen.blit(zoomed, (x, y))
        else:
            # Draw fully zoomed background
            zoomed = pygame.transform.smoothscale(self.original_bg, 
                (int(self.game.WIDTH * 1.2), int(self.game.HEIGHT * 1.2)))
            x = (self.game.WIDTH - zoomed.get_width()) // 2
            y = (self.game.HEIGHT - zoomed.get_height()) // 2
            self.screen.blit(zoomed, (x, y))
            
            # Draw "Press Enter to Start" only if visible
            if self.text_visible:
                self.screen.blit(self.text, self.text_rect)
            
        if self.menu_modal:
            self.menu_modal.draw(self.screen)
            
    def handle_event(self, event):
        if self.menu_modal:
            option = self.menu_modal.handle_event(event)
            if option:
                if option == "start_game":
                    from .level_selection_screen import LevelSelectionScreen
                    self.game.change_screen(LevelSelectionScreen(self.game))
                elif option == "settings":
                    from .settings_screen import SettingsScreen
                    self.game.change_screen(SettingsScreen(self.game))
                elif option == "exit":
                    pygame.quit()
                    import sys
                    sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.show_press_enter:
            self.text_visible = False  # Hide the text
            self.menu_modal = MenuModal(self.game.WIDTH // 2, self.game.HEIGHT // 2)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.show_press_enter:
            # Also allow clicking to show menu
            self.text_visible = False  # Hide the text
            self.menu_modal = MenuModal(self.game.WIDTH // 2, self.game.HEIGHT // 2)