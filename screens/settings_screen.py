import pygame
from .base_screen import Screen

class SettingsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Settings options
        self.settings = {
            "resolution": {
                "options": ["1920x1080", "1280x720", "800x600"],
                "current": 0
            },
            "window_mode": {
                "options": ["Fullscreen", "Windowed"],
                "current": 0
            },
            "audio": {
                "options": ["On", "Off"],
                "current": 0
            },
            "colorblind_mode": {
                "options": ["Off", "On"],
                "current": 0
            }
        }
        
        # Calculate positions
        self.selected = 0
        self.option_rects = []
        self.update_option_positions()
        
    def update_option_positions(self):
        self.option_rects = []
        
        # Title
        title = self.title_font.render("Settings", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.game.WIDTH // 2, 100))
        self.title = (title, title_rect)
        
        # Options
        spacing = 80
        start_y = 200
        
        for i, (key, setting) in enumerate(self.settings.items()):
            # Option name
            name = key.replace("_", " ").title()
            name_surface = self.font.render(name + ":", True, (255, 255, 255))
            name_rect = name_surface.get_rect(right=self.game.WIDTH // 2 - 20, centery=start_y + i * spacing)
            
            # Option value
            value = setting["options"][setting["current"]]
            value_surface = self.font.render(value, True, (255, 255, 255))
            value_rect = value_surface.get_rect(left=self.game.WIDTH // 2 + 20, centery=start_y + i * spacing)
            
            self.option_rects.append({
                "name": (name_surface, name_rect),
                "value": (value_surface, value_rect)
            })
            
        # Back button
        back = self.font.render("Back", True, (255, 255, 255))
        back_rect = back.get_rect(center=(self.game.WIDTH // 2, start_y + len(self.settings) * spacing))
        self.back_button = (back, back_rect)
        
    def draw(self):
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw title
        self.screen.blit(*self.title)
        
        # Draw options
        for i, option in enumerate(self.option_rects):
            # Draw option name
            self.screen.blit(*option["name"])
            # Draw option value
            self.screen.blit(*option["value"])
            
            # Draw selection indicator
            if i == self.selected:
                if i < len(self.settings):  # Not back button
                    rect = option["value"][1]
                else:
                    rect = self.back_button[1]
                pygame.draw.rect(self.screen, (100, 100, 255), rect.inflate(20, 10), 2)
                
        # Draw back button
        self.screen.blit(*self.back_button)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % (len(self.settings) + 1)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % (len(self.settings) + 1)
            elif event.key == pygame.K_LEFT and self.selected < len(self.settings):
                setting = list(self.settings.values())[self.selected]
                setting["current"] = (setting["current"] - 1) % len(setting["options"])
                self.apply_settings()
                self.update_option_positions()
            elif event.key == pygame.K_RIGHT and self.selected < len(self.settings):
                setting = list(self.settings.values())[self.selected]
                setting["current"] = (setting["current"] + 1) % len(setting["options"])
                self.apply_settings()
                self.update_option_positions()
            elif event.key == pygame.K_RETURN:
                if self.selected == len(self.settings):  # Back button
                    from .splash_screen import SplashScreen
                    self.game.change_screen(SplashScreen(self.game))
                    
    def apply_settings(self):
        # Apply resolution
        resolution = self.settings["resolution"]["options"][self.settings["resolution"]["current"]]
        width, height = map(int, resolution.split("x"))
        
        # Apply window mode
        is_fullscreen = self.settings["window_mode"]["options"][self.settings["window_mode"]["current"]] == "Fullscreen"
        flags = pygame.FULLSCREEN if is_fullscreen else 0
        
        # Update screen
        self.game.WIDTH, self.game.HEIGHT = width, height
        self.game.screen = pygame.display.set_mode((width, height), flags)
        
        # Update positions after resolution change
        self.update_option_positions()
