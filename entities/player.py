import math
import pygame

SPEED = 260.0  # px/s
PLAYER_SIZE = (70, 75)  # (w, h) for both standing/moving sprites - 50% del tamaño original

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Animation variables
        self.animation_time = 0
        self.y_scale = 1.0
        self.moving_animation_scale_range = 0.1  # Scale will oscillate between 0.9 and 1.1
        self.moving_animation_speed = 4.0  # Oscillations per second

        # Load base images (assumed to face RIGHT by default)
        standing = pygame.image.load("character-standing.png").convert_alpha()
        moving = pygame.image.load("character-moving.png").convert_alpha()

        # Normalize size
        self.original_standing = pygame.transform.smoothscale(standing, PLAYER_SIZE)
        self.original_moving = pygame.transform.smoothscale(moving, PLAYER_SIZE)

        # Start with standing pose
        self.base_image = self.original_standing
        self.image = self.base_image
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.last_dir = pygame.Vector2(1, 0)  # facing direction (preserved when idle)

        # If your art's default orientation isn't RIGHT, tweak this:
        # e.g., looks UP by default → set to -90; DOWN → +90; LEFT → 180
        self.angle_offset_deg = 0
        
        # Stone interaction
        self.carried_stone = None
        self.interaction_radius = 30

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dir = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dir.x += 1
        return dir

    def update(self, dt, bounds_rect):
        dir = self.handle_input()
        moved = dir.length_squared() > 0

        if moved:
            dir = dir.normalize()
            self.last_dir = dir
            self.pos += dir * SPEED * dt
            
            # Update animation time and calculate Y scale
            self.animation_time += dt
            self.y_scale = 1.0 + self.moving_animation_scale_range * math.sin(self.animation_time * self.moving_animation_speed * 2 * math.pi)
        else:
            # Reset animation when not moving
            self.animation_time = 0
            self.y_scale = 1.0

        # Switch base image depending on movement state
        self.base_image = self.original_moving if moved else self.original_standing

        # Keep on screen using current rotated frame size
        half_w, half_h = self.rect.width / 2, self.rect.height / 2
        self.pos.x = max(bounds_rect.left + half_w, min(self.pos.x, bounds_rect.right - half_w))
        self.pos.y = max(bounds_rect.top + half_h,  min(self.pos.y, bounds_rect.bottom - half_h))

        # Rotate to face last_dir and apply Y-scale
        angle_deg = -math.degrees(math.atan2(self.last_dir.y, self.last_dir.x)) + self.angle_offset_deg
        
        # First scale the image in Y direction
        scaled = pygame.transform.smoothscale(self.base_image, 
            (self.base_image.get_width(), int(self.base_image.get_height() * self.y_scale)))
        
        # Then rotate the scaled image
        rotated = pygame.transform.rotozoom(scaled, angle_deg, 1.0)

        old_center = self.rect.center
        self.image = rotated
        self.rect = self.image.get_rect(center=old_center)
        self.rect.center = (self.pos.x, self.pos.y)
        
        # Update carried stone position
        if self.carried_stone:
            # Offset the stone slightly in front of the player
            offset = self.last_dir * 30
            self.carried_stone.pos = self.pos + offset
            
    def can_pickup_stone(self, stone):
        """Verificar si el jugador puede recoger una piedra"""
        if self.carried_stone is not None:
            return False  # Ya lleva una piedra
        if stone.is_carried:
            return False  # La piedra ya está siendo llevada
            
        distance = pygame.Vector2(self.pos).distance_to(stone.pos)
        return distance <= self.interaction_radius
        
    def pickup_stone(self, stone):
        """Recoger una piedra"""
        if self.can_pickup_stone(stone):
            self.carried_stone = stone
            stone.pickup()
            return True
        return False
        
    def can_drop_stone(self):
        """Verificar si el jugador puede soltar la piedra que lleva"""
        return self.carried_stone is not None
        
    def drop_stone(self, drop_zone=None):
        """Soltar la piedra que lleva"""
        if not self.can_drop_stone():
            return False
            
        stone = self.carried_stone
        self.carried_stone = None
        
        if drop_zone and drop_zone.can_accept_stone():
            # Colocar en la zona de drop
            drop_zone.add_stone(stone)
        else:
            # Soltar en el lugar actual
            stone.place_at(self.pos)
            
        return True
        
    def get_interaction_rect(self):
        """Obtener el rectángulo de interacción del jugador"""
        return pygame.Rect(
            self.pos.x - self.interaction_radius,
            self.pos.y - self.interaction_radius,
            self.interaction_radius * 2,
            self.interaction_radius * 2
        )
