import pygame
from .base_screen import Screen
from ui.button import Button, CircularButton

class LevelSelectionScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        
        # Create placeholder level images - Colores brillantes normales
        self.level_images = []
        colors = [(255, 80, 80), (80, 255, 80), (80, 80, 255)]  # Rojo, Verde, Azul
        font = pygame.font.Font(None, 72)
        
        for i in range(3):
            # Create a surface for the level
            surface = pygame.Surface((200, 200), pygame.SRCALPHA)
            
            # Draw colored circle
            pygame.draw.circle(surface, colors[i], (100, 100), 100)
            
            # Add level number
            text = font.render(str(i + 1), True, (255, 255, 255))
            text_rect = text.get_rect(center=(100, 100))
            surface.blit(text, text_rect)
            
            self.level_images.append(surface)
        
        # Create instructions button
        self.instructions_button = Button(
            game.WIDTH // 2, 200, 200, 50,
            text="Instructions"
        )
        
        # Create level buttons
        self.level_buttons = []
        spacing = 300  # Space between buttons
        start_x = game.WIDTH // 2 - spacing
        y = game.HEIGHT // 2
        
        for i in range(3):
            button = CircularButton(
                start_x + i * spacing, y, 100,
                image=self.level_images[i],
                text=""  # Remove text since it's in the image
            )
            self.level_buttons.append(button)
            
        # Show cursor
        pygame.mouse.set_visible(True)
        
    def update(self, dt):
        self.instructions_button.update(dt)
        for button in self.level_buttons:
            button.update(dt)
            
    def draw(self):
        # Clear screen with normal background color
        self.screen.fill((30, 30, 40))
        
        # Draw instructions button
        self.instructions_button.draw(self.screen)
        
        # Draw level buttons
        for button in self.level_buttons:
            button.draw(self.screen)
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.instructions_button.is_hovered:
                from .instructions_screen import InstructionsScreen
                self.game.change_screen(InstructionsScreen(self.game))
                
            for i, button in enumerate(self.level_buttons):
                if button.is_hovered:
                    from .game_screen import GameScreen
                    self.game.change_screen(GameScreen(self.game, level=i+1))
                    pygame.mouse.set_visible(False)  # Hide cursor for game
                    break