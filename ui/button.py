import pygame

class Button:
    def __init__(self, x, y, width, height, text="", image=None, scale=1.0):
        self.original_image = image
        self.scale = scale
        self.is_hovered = False
        self.hover_scale = 1.2  # Exactamente 20% más grande
        
        if image:
            self.image = pygame.transform.scale(image, 
                (int(width * scale), int(height * scale)))
            self.rect = self.image.get_rect(center=(x, y))
            self.original_rect = self.rect.copy()
        else:
            self.rect = pygame.Rect(0, 0, width, height)
            self.rect.center = (x, y)
            
        # Text setup
        self.font = pygame.font.Font(None, 36)
        self.text = text
        self.text_color = (255, 255, 255)
        self.text_surface = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        
    def update(self, dt, mouse_pos=None):
        # Usar posición de mouse lógica si se provee; fallback a coordenadas de ventana
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Solo actualizar si el estado de hover cambió
        if was_hovered != self.is_hovered:
            if self.is_hovered:
                # Aumentar tamaño al 120%
                if self.original_image:
                    new_width = int(self.original_rect.width * self.hover_scale)
                    new_height = int(self.original_rect.height * self.hover_scale)
                    self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
                    self.rect = self.image.get_rect(center=self.original_rect.center)
            else:
                # Volver al tamaño original
                if self.original_image:
                    self.image = pygame.transform.scale(self.original_image, 
                        (self.original_rect.width, self.original_rect.height))
                    self.rect = self.original_rect.copy()
            
        self.text_rect.center = self.rect.center
        
    def draw(self, screen):
        if self.original_image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, (100, 100, 255), self.rect, border_radius=10)
            
        screen.blit(self.text_surface, self.text_rect)
        
class CircularButton(Button):
    def __init__(self, x, y, radius, image=None, text=""):
        super().__init__(x, y, radius * 2, radius * 2, text, image)
        self.radius = radius
        self.original_radius = radius
        
    def draw(self, screen):
        if self.original_image:
            # Create a surface for the button with alpha channel
            button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
            # Create circular mask
            mask = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            
            # Opacidad base y hover
            alpha = 255 if self.is_hovered else 100
            
            # Aplicar la opacidad directamente a la imagen
            masked_image = self.image.copy()
            masked_image.set_alpha(alpha)
            
            # Dibujar la imagen con la opacidad aplicada
            button_surface.blit(masked_image, (0, 0))
            screen.blit(button_surface, self.rect)