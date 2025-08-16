import pygame
import math

class Cheese(pygame.sprite.Sprite):
    """
    El queso que el jugador debe alcanzar para completar el nivel.
    Solo es accesible cuando el circuito lógico está completo.
    """
    def __init__(self, pos):
        super().__init__()
        self.original_pos = pygame.Vector2(pos)
        self.pos = pygame.Vector2(pos)
        self.is_accessible = False
        self.collected = False
        
        # Animación del queso
        self.animation_time = 0
        self.float_amplitude = 10  # Amplitud del movimiento flotante
        self.float_speed = 2.0     # Velocidad de la animación
        self.glow_time = 0
        
        # Crear imagen del queso
        self.size = 60
        self.create_cheese_image()
        
        self.rect = self.image.get_rect(center=pos)
        
        # Zona de acceso (área donde el jugador puede recoger el queso)
        self.access_radius = 40
        
    def create_cheese_image(self):
        """Crear la imagen del queso"""
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Color del queso
        cheese_color = (255, 255, 0) if self.is_accessible else (150, 150, 150)
        hole_color = (200, 200, 0) if self.is_accessible else (100, 100, 100)
        
        # Dibujar el queso (forma de triángulo/cuña)
        points = [
            (self.size // 4, self.size - 5),           # Esquina inferior izquierda
            (self.size - 5, self.size - 5),            # Esquina inferior derecha
            (self.size // 2, 5)                        # Punto superior
        ]
        pygame.draw.polygon(self.image, cheese_color, points)
        pygame.draw.polygon(self.image, (0, 0, 0), points, 2)
        
        # Agregar agujeros del queso
        holes = [
            (self.size // 2 - 8, self.size // 2),
            (self.size // 2 + 8, self.size // 2 + 5),
            (self.size // 2, self.size // 2 + 15)
        ]
        
        for hole_pos in holes:
            pygame.draw.circle(self.image, hole_color, hole_pos, 4)
            pygame.draw.circle(self.image, (0, 0, 0), hole_pos, 4, 1)
            
    def update(self, dt, bounds_rect=None, circuit_complete=False):
        """Actualizar el estado del queso"""
        self.is_accessible = circuit_complete
        
        if not self.collected:
            # Animación flotante
            self.animation_time += dt
            float_offset = math.sin(self.animation_time * self.float_speed) * self.float_amplitude
            self.pos.y = self.original_pos.y + float_offset
            
            # Actualizar imagen si cambió la accesibilidad
            self.create_cheese_image()
            
            # Efecto de brillo cuando es accesible
            if self.is_accessible:
                self.glow_time += dt
                
        self.rect.center = (self.pos.x, self.pos.y)
        
    def can_be_collected_by(self, player_pos):
        """Verificar si el jugador puede recoger el queso"""
        if not self.is_accessible or self.collected:
            return False
            
        distance = pygame.Vector2(player_pos).distance_to(self.pos)
        return distance <= self.access_radius
        
    def collect(self):
        """Marcar el queso como recolectado"""
        if self.is_accessible and not self.collected:
            self.collected = True
            return True
        return False
        
    def draw(self, screen):
        """Dibujar el queso con efectos especiales"""
        if self.collected:
            return
            
        # Dibujar efecto de brillo si es accesible
        if self.is_accessible:
            glow_radius = int(self.access_radius + 10 * math.sin(self.glow_time * 3))
            glow_color = (255, 255, 0, 50)  # Amarillo semi-transparente
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.pos.x - glow_radius, self.pos.y - glow_radius))
            
        # Dibujar el queso
        screen.blit(self.image, self.rect)
        
        # Dibujar texto de estado si no es accesible
        if not self.is_accessible:
            font = pygame.font.Font(None, 24)
            text = font.render("Complete circuit to access", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.pos.x, self.pos.y + self.size))
            
            # Fondo para el texto
            bg_rect = text_rect.inflate(10, 5)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            screen.blit(text, text_rect)
            
    def get_access_rect(self):
        """Obtener el rectángulo de acceso para detección de colisiones"""
        return pygame.Rect(
            self.pos.x - self.access_radius,
            self.pos.y - self.access_radius,
            self.access_radius * 2,
            self.access_radius * 2
        )
