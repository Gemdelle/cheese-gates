import pygame

class PauseModal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, 400, 300)
        self.rect.center = (x, y)
        
        # Create font and options
        self.font = pygame.font.Font(None, 36)
        self.options = [
            {"text": "Settings", "action": "settings"},
            {"text": "Select Level", "action": "select_level"},
            {"text": "Exit to Desktop", "action": "exit"}
        ]
        
        # Calculate option positions
        self.option_rects = []
        spacing = 50
        total_height = spacing * (len(self.options) - 1)
        start_y = self.rect.centery - total_height // 2
        
        for i, option in enumerate(self.options):
            text_surface = self.font.render(option["text"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.rect.centerx, start_y + i * spacing))
            self.option_rects.append((text_rect, text_surface))
            
        self.selected = 0  # Index of currently selected option
        
        # Show cursor for menu
        pygame.mouse.set_visible(True)
        
    def update(self, dt):
        # Update hover state based on mouse position
        mouse_pos = pygame.mouse.get_pos()
        for i, (rect, _) in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = i
                break
        
    def draw(self, screen):
        # Draw semi-transparent dark overlay for the entire screen
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw modal background
        s = pygame.Surface(self.rect.size)
        s.fill((0, 0, 0))
        s.set_alpha(200)
        screen.blit(s, self.rect)
        
        # Draw border
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        # Draw options
        for i, (rect, surface) in enumerate(self.option_rects):
            if i == self.selected:
                # Draw selection indicator
                pygame.draw.rect(screen, (100, 100, 255), rect.inflate(20, 10), 2)
            screen.blit(surface, rect)
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked on an option
            mouse_pos = pygame.mouse.get_pos()
            for i, (rect, _) in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    return self.options[i]["action"]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected]["action"]
            elif event.key == pygame.K_ESCAPE:
                return "resume"  # Opción especial para cerrar el modal
        return None
