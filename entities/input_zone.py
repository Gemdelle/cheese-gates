import pygame

class InputZone:
    """
    Zona donde se pueden colocar hasta 2 piedras.
    Calcula automáticamente la suma de los pesos de las piedras colocadas.
    Muestra al lado: "<total> / <requerido>" (sin paréntesis).
    """
    def __init__(self, pos, input_number, required=0):
        self.pos = pygame.Vector2(pos)
        self.input_number = input_number
        self.required = int(required)  # viene del level config
        self.stones = []              # Lista de piedras colocadas (máximo 2)
        self.max_stones = 2

        # Dimensiones de la zona (box)
        self.width = 300
        self.height = 110
        self.rect = pygame.Rect(
            pos[0] - self.width // 2,
            pos[1] - self.height // 2,
            self.width,
            self.height
        )

        # Posiciones para las 2 piedras dentro de la zona
        self.stone_positions = [
            (pos[0] - 50, pos[1]),  # izquierda
            (pos[0] + 50, pos[1])   # derecha
        ]

        # Imagen de fondo de la caja
        raw_box = pygame.image.load("box.png").convert_alpha()
        self.box_img = pygame.transform.smoothscale(raw_box, (self.width, self.height))

    def can_accept_stone(self):
        return len(self.stones) < self.max_stones

    def add_stone(self, stone):
        if self.can_accept_stone():
            self.stones.append(stone)
            # Colocar la piedra en la siguiente posición disponible
            stone_pos = self.stone_positions[len(self.stones) - 1]
            stone.place_at(stone_pos, self)
            return True
        return False

    def remove_stone(self, stone):
        if stone in self.stones:
            self.stones.remove(stone)
            # Reorganizar las piedras restantes
            for i, remaining_stone in enumerate(self.stones):
                stone_pos = self.stone_positions[i]
                remaining_stone.place_at(stone_pos, self)

    def get_total_weight(self):
        """Suma de los pesos de las piedras en la zona."""
        return sum(stone.weight for stone in self.stones)

    def get_binary_value(self):
        """1 si hay alguna piedra (>0), 0 si no hay (esto lo usa quien lo necesite)."""
        return 1 if self.get_total_weight() > 0 else 0

    def draw(self, screen):
        # Fondo de la caja
        screen.blit(self.box_img, self.rect.topleft)

        # (Opcional) borde sutil
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        # Dibujar los 2 slots vacíos como círculos pequeños
        for i, stone_pos in enumerate(self.stone_positions):
            if i >= len(self.stones):  # solo si el slot está vacío
                pygame.draw.circle(
                    screen, (255, 255, 255),
                    (int(stone_pos[0]), int(stone_pos[1])), 6
                )

        # Texto lateral: "<total> / <requerido>" SIN paréntesis
        font = pygame.font.Font("font/BlackCastleMF.ttf", 24)
        total = self.get_total_weight()
        side_text = font.render(f"{total} / {self.required}", True, (255, 255, 255))
        side_rect = side_text.get_rect(midleft=(self.rect.right + 12, self.rect.centery))
        screen.blit(side_text, side_rect)

    def contains_point(self, point):
        return self.rect.collidepoint(point)
