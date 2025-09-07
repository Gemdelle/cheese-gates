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
        self.float_speed = 1     # Velocidad de la animación
        self.glow_time = 0

        # Crear imagen del queso
        self.size = 70
        self.create_cheese_image()

        self.rect = self.cage_img.get_rect(center=pos)  # El rect sigue la jaula (fija)

        # Zona de acceso (área donde el jugador puede recoger el queso)
        self.access_radius = 40

        # Fuente del cartel (podés cambiar por tu .ttf si querés)
        self._ui_font = pygame.font.Font("font/BlackCastleMF.ttf", 30)

    def create_cheese_image(self):
        """Crear las imágenes del queso y la jaula"""
        # Cargar imágenes desde el mismo directorio
        cheese_raw = pygame.image.load("cheese.png").convert_alpha()
        cage_raw   = pygame.image.load("cage.png").convert_alpha()

        # --- Tamaños fijos para cada sprite ---
        cheese_size = (130, 100)   # Tamaño del queso
        cage_size   = (200, 220) # Tamaño de la jaula

        # Escalar a esos tamaños
        self.cheese_img = pygame.transform.smoothscale(cheese_raw, cheese_size)
        self.cage_img   = pygame.transform.smoothscale(cage_raw, cage_size)

        # Superficie base solo para dimensiones; el dibujado real se hace en draw()
        self.image = pygame.Surface(cage_size, pygame.SRCALPHA)


    def update(self, dt, bounds_rect=None, circuit_complete=False):
        """Actualizar el estado del queso"""
        self.is_accessible = circuit_complete

        if not self.collected:
            # Animación flotante (solo el queso se mueve, la jaula queda fija)
            self.animation_time += dt
            float_offset = math.sin(self.animation_time * self.float_speed) * self.float_amplitude
            # La posición lógica del objeto (rect) sigue a la jaula, fija:
            self.pos.update(self.original_pos.x, self.original_pos.y - float_offset + 20)

            # Efecto de brillo cuando es accesible
            if self.is_accessible:
                self.glow_time += dt

        # El rect queda centrado en la jaula (fija)
        self.rect.center = (self.original_pos.x, self.original_pos.y)

    def can_be_collected_by(self, player_pos):
        """Verificar si el jugador puede recoger el queso"""
        if not self.is_accessible or self.collected:
            return False

        # Distancia al centro de la jaula (estático)
        distance = pygame.Vector2(player_pos).distance_to(self.original_pos)
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

        # Dibujar efecto de brillo si es accesible (alrededor de la jaula)
        if self.is_accessible:
            glow_radius = int(self.access_radius + 10 * math.sin(self.glow_time * 3))
            glow_color = (255, 255, 0, 50)  # Amarillo semi-transparente
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.original_pos.x - glow_radius, self.original_pos.y - glow_radius))

        # --- Orden de dibujado: primero el queso (detrás), luego la jaula (adelante) ---
        # Posición del queso: sube y baja (self.pos.y); centrado bajo la jaula
        cheese_rect = self.cheese_img.get_rect(center=(self.original_pos.x, self.pos.y))
        screen.blit(self.cheese_img, cheese_rect)

        # Jaula fija al frente
        cage_rect = self.cage_img.get_rect(center=(self.original_pos.x, self.original_pos.y))
        screen.blit(self.cage_img, cage_rect)

        # Dibujar texto de estado si no es accesible — QUIETO debajo de la jaula y queso
        if not self.is_accessible:
            text = self._ui_font.render("Complete circuit", True, (255, 255, 255))
            text_rect = text.get_rect(midtop=(self.original_pos.x, cage_rect.bottom + 8))
            screen.blit(text, text_rect)

    def get_access_rect(self):
        """Obtener el rectángulo de acceso para detección de colisiones"""
        return pygame.Rect(
            self.original_pos.x - self.access_radius,
            self.original_pos.y - self.access_radius,
            self.access_radius * 2,
            self.access_radius * 2
        )
