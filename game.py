import sys
import pygame

class Game:
    WIDTH, HEIGHT = 1920, 1080
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cheese Gates")
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.current_screen = None
        
    def change_screen(self, screen):
        self.current_screen = screen
        
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(120) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.current_screen:
                    self.current_screen.handle_event(event)
            
            if self.current_screen:
                self.current_screen.update(dt)
                self.current_screen.draw()
            
            pygame.display.set_caption(f"Cheese Gates  |  FPS: {int(self.clock.get_fps()):>3}")
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()
