import pygame

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
        
        # Dimensiones de la zona
        self.width = 100
        self.height = 60
        self.rect = pygame.Rect(
            pos[0] - self.width // 2,
            pos[1] - self.height // 2,
            self.width,
            self.height
        )
        
        # Posiciones para las piedras dentro de la zona
        self.stone_positions = [
            (pos[0] - 20, pos[1]),  # Posición izquierda
            (pos[0] + 20, pos[1])   # Posición derecha
        ]
        
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
        # Color de fondo de la zona
        zone_color = (70, 130, 180) if self.can_accept_stone() else (105, 105, 105)
        border_color = (255, 255, 255)
        
        # Dibujar el rectángulo de la zona
        pygame.draw.rect(screen, zone_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Dibujar el número del input
        font = pygame.font.Font(None, 24)
        text = font.render(f"Input {self.input_number}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.top - 15))
        screen.blit(text, text_rect)
        
        # Dibujar el peso total
        weight_text = font.render(f"Weight: {self.get_total_weight()}", True, (255, 255, 255))
        weight_rect = weight_text.get_rect(center=(self.rect.centerx, self.rect.bottom + 15))
        screen.blit(weight_text, weight_rect)
        
        # Dibujar indicadores de posición para las piedras
        for i, stone_pos in enumerate(self.stone_positions):
            if i >= len(self.stones):  # Solo mostrar posiciones vacías
                pygame.draw.circle(screen, (200, 200, 200), 
                                 (int(stone_pos[0]), int(stone_pos[1])), 15, 1)
                                 
    def contains_point(self, point):
        """Verificar si un punto está dentro de la zona"""
        return self.rect.collidepoint(point)
