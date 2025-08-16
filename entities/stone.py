import pygame

class Stone(pygame.sprite.Sprite):
    """
    Piedra que el jugador puede recoger y colocar en las zonas de input.
    Cada piedra tiene un peso específico.
    """
    def __init__(self, weight, pos):
        super().__init__()
        self.weight = weight
        self.original_pos = pos
        self.is_carried = False
        self.is_placed = False
        self.drop_zone = None  # Referencia a la zona donde está colocada
        
        # Crear imagen de la piedra (círculo con el número del peso)
        self.size = 40
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Dibujar la piedra
        stone_color = (139, 69, 19)  # Color marrón para la piedra
        text_color = (255, 255, 255)  # Texto blanco
        
        pygame.draw.circle(self.image, stone_color, (self.size // 2, self.size // 2), self.size // 2)
        pygame.draw.circle(self.image, (0, 0, 0), (self.size // 2, self.size // 2), self.size // 2, 2)
        
        # Agregar el número del peso
        font = pygame.font.Font(None, 24)
        text = font.render(str(weight), True, text_color)
        text_rect = text.get_rect(center=(self.size // 2, self.size // 2))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        
    def update(self, dt, bounds_rect=None):
        """Actualizar posición de la piedra"""
        self.rect.center = (self.pos.x, self.pos.y)
        
    def pickup(self):
        """Marcar la piedra como recogida"""
        self.is_carried = True
        self.is_placed = False
        if self.drop_zone:
            self.drop_zone.remove_stone(self)
            self.drop_zone = None
            
    def place_at(self, pos, drop_zone=None):
        """Colocar la piedra en una posición específica"""
        self.pos = pygame.Vector2(pos)
        self.is_carried = False
        self.is_placed = True
        self.drop_zone = drop_zone
        
    def return_to_original(self):
        """Devolver la piedra a su posición original"""
        self.pos = pygame.Vector2(self.original_pos)
        self.is_carried = False
        self.is_placed = False
        if self.drop_zone:
            self.drop_zone.remove_stone(self)
            self.drop_zone = None
            
    def get_pickup_rect(self):
        """Obtener el rectángulo para detección de recogida"""
        # Área ligeramente más grande para facilitar la recogida
        pickup_size = self.size + 10
        return pygame.Rect(
            self.pos.x - pickup_size // 2,
            self.pos.y - pickup_size // 2,
            pickup_size,
            pickup_size
        )
