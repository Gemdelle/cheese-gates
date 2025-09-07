import math
import pygame

SPEED = 260.0  # px/s
PLAYER_SIZE = (100, 105)  # (w, h) for both standing/moving sprites - 50% del tamaño original


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Animation variables
        self.animation_time = 0
        self.y_scale = 1.0
        self.moving_animation_scale_range = 0.1
        self.moving_animation_speed = 4.0

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
        self.last_dir = pygame.Vector2(1, 0)

        # If your art's default orientation isn't RIGHT, tweak this:
        self.angle_offset_deg = 0

        # Stone interaction
        self.carried_stone = None
        self.interaction_radius = 30

        # Este es el nivel de la piedrita (no esta terminado pero funciona)
        self.carry_gap = 24            # lower than top of head (más baja al cargar)
        self.carry_front_dist = 24     # forward along facing direction
        self.carry_move_raise = 6      # raise a bit while moving
        self.carry_move_side_shift = 8 # shift to player's left while moving
        self.drop_y_offset = 16        # al soltar en el piso, caer un poco más abajo

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
            self.y_scale = 1.0 + self.moving_animation_scale_range * math.sin(
                self.animation_time * self.moving_animation_speed * 2 * math.pi
            )
        else:
            # Reset animation when not moving
            self.animation_time = 0
            self.y_scale = 1.0

        # Switch base image depending on movement state
        self.base_image = self.original_moving if moved else self.original_standing

        # Keep on screen using current rotated frame size
        half_w, half_h = self.rect.width / 2, self.rect.height / 2
        self.pos.x = max(bounds_rect.left + half_w, min(self.pos.x, bounds_rect.right - half_w))
        self.pos.y = max(bounds_rect.top + half_h, min(self.pos.y, bounds_rect.bottom - half_h))

        # Si mira estrictamente a la izquierda (A), flip horizontal
        flip_only_left = (self.last_dir.x < 0) and (abs(self.last_dir.y) < 1e-6)

        frame = self.base_image
        if flip_only_left:
            # Flip horizontal sin rotación
            frame = pygame.transform.flip(frame, True, False)
            # Escala vertical (squash & stretch)
            scaled = pygame.transform.smoothscale(
                frame, (frame.get_width(), int(frame.get_height() * self.y_scale))
            )
            rotated = scaled
        else:
            # Rotación normal según la dirección
            angle_deg = -math.degrees(math.atan2(self.last_dir.y, self.last_dir.x)) + self.angle_offset_deg
            scaled = pygame.transform.smoothscale(
                frame, (frame.get_width(), int(frame.get_height() * self.y_scale))
            )
            rotated = pygame.transform.rotozoom(scaled, angle_deg, 1.0)

        old_center = self.rect.center
        self.image = rotated
        self.rect = self.image.get_rect(center=old_center)
        self.rect.center = (self.pos.x, self.pos.y)

        # La piedrita al cargarse cambia de posicion:
        if self.carried_stone is not None:
            p_half_h = self.rect.height / 2
            s_half_h = self.carried_stone.rect.height / 2

            base_x = self.pos.x
            base_y = self.pos.y - p_half_h - s_half_h + self.carry_gap

            fwd = self.last_dir
            x = base_x + fwd.x * self.carry_front_dist
            y = base_y + fwd.y * self.carry_front_dist

            if moved:
                y -= self.carry_move_raise
                left_vec = pygame.Vector2(fwd.y, -fwd.x)
                x += left_vec.x * self.carry_move_side_shift
                y += left_vec.y * self.carry_move_side_shift

            self.carried_stone.pos.x = x
            self.carried_stone.pos.y = y

    def can_pickup_stone(self, stone):
        if self.carried_stone is not None:
            return False
        if stone.is_carried:
            return False
        distance = pygame.Vector2(self.pos).distance_to(stone.pos)
        return distance <= self.interaction_radius

    def pickup_stone(self, stone):
        if self.can_pickup_stone(stone):
            self.carried_stone = stone
            stone.pickup()
            p_half_h = self.rect.height / 2
            s_half_h = stone.rect.height / 2
            base_x = self.pos.x
            base_y = self.pos.y - p_half_h - s_half_h + self.carry_gap
            fwd = self.last_dir
            x = base_x + fwd.x * self.carry_front_dist
            y = base_y + fwd.y * self.carry_front_dist
            stone.pos.x = x
            stone.pos.y = y
            return True
        return False

    def can_drop_stone(self):
        return self.carried_stone is not None

    def drop_stone(self, drop_zone=None):
        if not self.can_drop_stone():
            return False
        stone = self.carried_stone
        self.carried_stone = None
        if drop_zone and drop_zone.can_accept_stone():
            drop_zone.add_stone(stone)
        else:
                stone.place_at((self.pos.x, self.pos.y + self.drop_y_offset))
        return True

    def get_interaction_rect(self):
        return pygame.Rect(
            self.pos.x - self.interaction_radius,
            self.pos.y - self.interaction_radius,
            self.interaction_radius * 2,
            self.interaction_radius * 2,
        )
