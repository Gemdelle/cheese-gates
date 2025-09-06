import pygame
import random  # Para variar el tamaño un poquito

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

        # Crear imagen de la piedra (según el peso: rock-big o rock-small)
        if self.weight > 6:
            image_name = "rock-big.png"   # la imagen sigue en el mismo lugar
            base_size = (70, 60)   # Tamaño base para piedra grande
            # Variar tamaño dentro de un rango ±5 píxeles
            size = (
                base_size[0] + random.randint(-5, 5),
                base_size[1] + random.randint(-5, 5)
            )
        else:
            image_name = "rock-small.png" # la imagen sigue en el mismo lugar
            base_size = (60, 50)   # Tamaño base para piedra chica
            # Variar tamaño dentro de un rango ±4 píxeles
            size = (
                base_size[0] + random.randint(-4, 4),
                base_size[1] + random.randint(-4, 4)
            )

        # Cargar la imagen, redimensionarla y asignar posición
        self.image = pygame.image.load(image_name).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, size)

        # --- Agregar el número del peso encima con fuente BlackCastle ---
        font = pygame.font.Font("font/BlackCastleMF.ttf", 24)
        text = font.render(str(self.weight), True, (255, 255, 255))  # Blanco
        text_rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
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
        pickup_size = max(self.rect.width, self.rect.height) + 10
        return pygame.Rect(
            self.pos.x - pickup_size // 2,
            self.pos.y - pickup_size // 2,
            pickup_size,
            pickup_size
        )
