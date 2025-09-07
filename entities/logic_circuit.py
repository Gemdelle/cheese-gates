# entities/logic_circuit.py
import pygame

class LogicCircuit:
    """
    Dibuja el fondo del circuito (opcional) dentro de un rect dado.
    NO muestra texto/estado: la evaluación se hace fuera (GameScreen al pisar TEST).
    """
    def __init__(self, rect: pygame.Rect, circuit_bg_path: str | None = None):
        self.rect = rect.copy()
        self.input_zones = []
        self.is_complete = False

        self.img = None
        if circuit_bg_path:
            try:
                raw = pygame.image.load(circuit_bg_path).convert_alpha()
                self.img = pygame.transform.smoothscale(raw, self.rect.size)
            except Exception:
                self.img = None  # si falta la imagen, simplemente no dibuja

    def add_input_zone(self, zone):
        self.input_zones.append(zone)

    def update(self, dt):
        # Nada: la lógica se evalúa al pisar el botón TEST en GameScreen
        pass

    def draw(self, screen):
        if self.img:
            screen.blit(self.img, self.rect.topleft)
        # si querés ver el contorno para debug, descomentá:
        # else:
        #     pygame.draw.rect(screen, (255,255,255), self.rect, 2)
