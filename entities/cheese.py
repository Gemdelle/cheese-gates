import pygame
import math

class Cheese(pygame.sprite.Sprite):
    """
    Queso + jaula. La jaula desaparece cuando el circuito está completo.
    Compatible con GameScreen: set_caged(...) y update(..., circuit_complete=True/False).
    """
    # Ajustá si querés más chico/grande
    CHEESE_SIZE = (90, 70)
    CAGE_SIZE   = (160, 176)
    ACCESS_RADIUS = 40

    def __init__(self, pos):
        super().__init__()
        self.original_pos = pygame.Vector2(pos)
        self.pos = pygame.Vector2(pos)
        self.collected = False

        # Estado de jaula / acceso
        self.caged = True               # visible al inicio
        self.is_accessible = False      # True si se puede agarrar (circuit_complete o sin jaula)

        # Animaciones
        self.animation_time = 0.0
        self.float_amplitude = 10
        self.float_speed = 1.0
        self.glow_time = 0.0
        self._pop_timer = 0.0           # pequeño "pop" al abrir la jaula

        # Imágenes
        self._load_images()

        # El rect general (para groups)
        base = self.cage_img if self.cage_img is not None else self.cheese_img
        self.image = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.original_pos)

        # Fuente cartel
        self._ui_font = pygame.font.Font("font/BlackCastleMF.ttf", 30)

        # Área de acceso
        self.access_radius = self.ACCESS_RADIUS

    # ----------------------- assets -----------------------

    def _load_images(self):
        # Cargar con fallback y escalar a tamaños más chicos
        cheese_raw = pygame.image.load("cheese.png").convert_alpha()
        self.cheese_img = pygame.transform.smoothscale(cheese_raw, self.CHEESE_SIZE)

        self.cage_img = None
        try:
            cage_raw = pygame.image.load("cage.png").convert_alpha()
            self.cage_img = pygame.transform.smoothscale(cage_raw, self.CAGE_SIZE)
        except Exception:
            self.cage_img = None  # si no hay archivo, seguimos sin jaula

    # ----------------------- API pública -----------------------

    def set_caged(self, value: bool):
        """Forzar visual de jaula ON/OFF (GameScreen lo llama)."""
        was = self.caged
        self.caged = bool(value)
        if was and not self.caged:
            self._pop_timer = 0.18  # efecto leve al abrirse

    def can_be_collected_by(self, player_pos):
        """El jugador puede recoger si no hay jaula / circuito completo."""
        if not self.is_accessible or self.collected:
            return False
        distance = pygame.Vector2(player_pos).distance_to(self.original_pos)
        return distance <= self.access_radius

    def collect(self):
        if self.is_accessible and not self.collected:
            self.collected = True
            return True
        return False

    # ----------------------- ciclo -----------------------

    def update(self, dt, bounds_rect=None, circuit_complete=False):
        # Accesible si el circuito está completo o si la jaula ya fue ocultada
        self.is_accessible = circuit_complete or (not self.caged)

        if not self.collected:
            # Flotación del queso (la jaula NO se mueve)
            self.animation_time += dt
            float_offset = math.sin(self.animation_time * self.float_speed) * self.float_amplitude
            self.pos.update(self.original_pos.x, self.original_pos.y - float_offset + 20)

            if self.is_accessible:
                self.glow_time += dt

        # Pop al abrir
        if self._pop_timer > 0:
            self._pop_timer = max(0.0, self._pop_timer - dt)

        # Rect centrado en la posición base (la jaula sirve de referencia si existe)
        base = self.cage_img if (self.cage_img is not None) else self.cheese_img
        self.rect = base.get_rect(center=self.original_pos)

    def draw(self, screen):
        if self.collected:
            return

        # Queso (con un pop/scale suave al liberarse)
        scale = 1.0 + (0.08 * (self._pop_timer / 0.18)) if self._pop_timer > 0 else 1.0
        if abs(scale - 1.0) > 1e-3:
            w = int(self.cheese_img.get_width() * scale)
            h = int(self.cheese_img.get_height() * scale)
            cheese = pygame.transform.smoothscale(self.cheese_img, (w, h))
        else:
            cheese = self.cheese_img
        cheese_rect = cheese.get_rect(center=(self.original_pos.x, self.pos.y))
        screen.blit(cheese, cheese_rect)

        # Jaula al frente SOLO si sigue “caged”
        if self.caged and self.cage_img is not None:
            cage_rect = self.cage_img.get_rect(center=self.original_pos)
            screen.blit(self.cage_img, cage_rect)

        # Cartel cuando NO es accesible
        if not self.is_accessible:
            text = self._ui_font.render("Complete circuit", True, (255, 255, 255))
            text_rect = text.get_rect(midtop=(self.original_pos.x, self.rect.bottom + 8))
            screen.blit(text, text_rect)

    # (por si alguna lógica externa necesita el área de acceso)
    def get_access_rect(self):
        return pygame.Rect(
            self.original_pos.x - self.access_radius,
            self.original_pos.y - self.access_radius,
            self.access_radius * 2,
            self.access_radius * 2
        )
