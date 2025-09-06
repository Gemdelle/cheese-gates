import pygame
import random

class InputZone:
    """
    Zona donde se pueden colocar hasta 2 piedras.
    Calcula automáticamente la suma de los pesos de las piedras colocadas.
    """
    def __init__(self, pos, input_number):
        self.pos = pygame.Vector2(pos)
        self.input_number = input_number
        self.stones = []  # Lista de piedras colocadas (máximo 2)
        self.max_stones = 2

        # --- Dimensiones de la zona ---
        self.width = 300
        self.height = 110
        self.rect = pygame.Rect(
            pos[0] - self.width // 2,
            pos[1] - self.height // 2,
            self.width,
            self.height
        )

        # Posiciones para las piedras dentro de la zona
        self.stone_positions = [
            (pos[0] - 50, pos[1]),  # Posición izquierda
            (pos[0] + 50, pos[1])   # Posición derecha
        ]

        # --- Cargar imagen de fondo para la caja ---
        raw_box = pygame.image.load("box.png").convert_alpha()
        self.box_img = pygame.transform.smoothscale(raw_box, (self.width, self.height))

        # --- Número random fijo por caja para el rótulo lateral ---
        self.label_number = random.randint(1, 99)

    def can_accept_stone(self):
        """Verificar si la zona puede aceptar más piedras"""
        return len(self.stones) < self.max_stones

    def add_stone(self, stone):
        """Agregar una piedra a la zona"""
        if self.can_accept_stone():
            self.stones.append(stone)
            # Colocar la piedra en la siguiente posición disponible
            stone_pos = self.stone_positions[len(self.stones) - 1]
            stone.place_at(stone_pos, self)
            return True
        return False

    def remove_stone(self, stone):
        """Remover una piedra de la zona"""
        if stone in self.stones:
            self.stones.remove(stone)
            # Reorganizar las piedras restantes
            for i, remaining_stone in enumerate(self.stones):
                stone_pos = self.stone_positions[i]
                remaining_stone.place_at(stone_pos, self)

    def get_total_weight(self):
        """Calcular el peso total de las piedras en la zona"""
        return sum(stone.weight for stone in self.stones)

    def get_binary_value(self):
        """Convertir el peso total a valor binario (1 si > 0, 0 si = 0)"""
        return 1 if self.get_total_weight() > 0 else 0

    def draw(self, screen):
        """Dibujar la zona de input"""
        # --- Dibujar la imagen de la caja como fondo ---
        screen.blit(self.box_img, self.rect.topleft)

        # Dibujar el borde de la zona (lo dejaste comentado, lo mantengo así)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        # --- Dibujar los 2 círculos blancos (slots vacíos) ---
        for i, stone_pos in enumerate(self.stone_positions):
            if i >= len(self.stones):  # Solo mostrar si está vacío
                pygame.draw.circle(
                    screen, (255, 255, 255),
                    (int(stone_pos[0]), int(stone_pos[1])), 6  # radio chico
                )

        # --- Texto lateral: (suma_actual / número_random) ---
        font = pygame.font.Font("font/BlackCastleMF.ttf", 24)
        current_sum = self.get_total_weight()
        label_str = f"({current_sum} / {self.label_number})"
        side_text = font.render(label_str, True, (255, 255, 255))
        side_rect = side_text.get_rect(midleft=(self.rect.right + 12, self.rect.centery))
        screen.blit(side_text, side_rect)

    def contains_point(self, point):
        """Verificar si un punto está dentro de la zona"""
        return self.rect.collidepoint(point)
