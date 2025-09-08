import math
import pygame

SPEED = 320.0  # px/s - Increased for more responsiveness
PLAYER_SIZE = (100, 105)  # (w, h) scaled sprite size

# Movement enhancements - More responsive values
ACCELERATION = 2000.0  # px/s² - Much faster acceleration
DECELERATION = 2800.0  # px/s² - Quick stopping
DIAGONAL_SPEED_FACTOR = 0.707  # sqrt(2)/2 for proper diagonal movement


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Animation state
        self.animation_time = 0.0
        self.y_scale = 1.0
        self.moving_animation_scale_range = 0.1
        self.moving_animation_speed = 4.0

        # Load and scale images
        standing = pygame.image.load("character-standing.png").convert_alpha()
        moving = pygame.image.load("character-moving.png").convert_alpha()
        self.original_standing = pygame.transform.smoothscale(standing, PLAYER_SIZE)
        self.original_moving = pygame.transform.smoothscale(moving, PLAYER_SIZE)

        # Initial frame
        self.base_image = self.original_standing
        self.image = self.base_image
        self.rect = self.image.get_rect(center=pos)

        # Enhanced kinematics
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(0, 0)  # Current velocity
        self.target_velocity = pygame.Vector2(0, 0)  # Desired velocity
        self.last_dir = pygame.Vector2(1, 0)
        
        # Stable, rotation-independent hit radius
        self.collision_radius = int(min(PLAYER_SIZE) * 0.4)

        # Movement state tracking
        self.was_moving = False
        self.direction_change_time = 0.0
        self.last_input_dir = pygame.Vector2(0, 0)

        # Facing tweak if art base not RIGHT
        self.angle_offset_deg = 0

        # Stone interaction
        self.carried_stone = None
        self.interaction_radius = 30

        # Carry offsets
        self.carry_gap = 24
        self.carry_front_dist = 24
        self.carry_move_raise = 6
        self.carry_move_side_shift = 8
        self.drop_y_offset = 16

        # Movement flag (for audio)
        self.is_moving = False

    def handle_input(self):
        """Enhanced input handling with better diagonal movement"""
        keys = pygame.key.get_pressed()
        input_dir = pygame.Vector2(0, 0)
        
        # Gather input
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            input_dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            input_dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            input_dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            input_dir.x += 1
        
        # Normalize diagonal movement to prevent speed boost
        if input_dir.length_squared() > 0:
            input_dir = input_dir.normalize()
            
        # Track direction changes for smoother transitions
        if input_dir != self.last_input_dir:
            self.direction_change_time = 0.0
        self.last_input_dir = input_dir
        
        return input_dir

    def update(self, dt, bounds_rect):
        """Enhanced update with smooth acceleration/deceleration and better animation"""
        input_direction = self.handle_input()
        self.direction_change_time += dt
        
        # Calculate target velocity based on input
        if input_direction.length_squared() > 0:
            self.target_velocity = input_direction * SPEED
            # Update facing direction only when actively moving
            self.last_dir = input_direction
        else:
            self.target_velocity = pygame.Vector2(0, 0)
        
        # Smooth acceleration/deceleration
        velocity_diff = self.target_velocity - self.velocity
        
        if velocity_diff.length_squared() > 0:
            # Choose acceleration or deceleration
            accel_rate = ACCELERATION if input_direction.length_squared() > 0 else DECELERATION
            
            # Apply acceleration with frame-rate independence
            max_change = accel_rate * dt
            if velocity_diff.length() <= max_change:
                self.velocity = self.target_velocity
            else:
                self.velocity += velocity_diff.normalize() * max_change
        
        # Update position with smooth velocity
        old_pos = self.pos.copy()
        self.pos += self.velocity * dt
        
        # Enhanced movement state tracking
        velocity_magnitude = self.velocity.length()
        self.is_moving = velocity_magnitude > 20.0  # Higher threshold for cleaner state
        
        # Cleaner animation without wobble on stop
        if self.is_moving:
            self.animation_time += dt
            self.y_scale = 1.0 + self.moving_animation_scale_range * math.sin(
                self.animation_time * self.moving_animation_speed * 2 * math.pi
            )
        else:
            # Immediate stop - no wobble/tambaleo
            self.animation_time = 0.0
            self.y_scale = 1.0

        # Instant image switching for cleaner feel
        self.base_image = self.original_moving if self.is_moving else self.original_standing
        self.was_moving = self.is_moving

        # Enhanced orientation and rendering
        flip_only_left = (self.last_dir.x < 0) and (abs(self.last_dir.y) < 1e-6)
        frame = self.base_image
        
        if flip_only_left:
            frame = pygame.transform.flip(frame, True, False)
            scaled = pygame.transform.smoothscale(
                frame, (frame.get_width(), int(frame.get_height() * self.y_scale))
            )
            rotated = scaled
        else:
            angle_deg = -math.degrees(math.atan2(self.last_dir.y, self.last_dir.x)) + self.angle_offset_deg
            scaled = pygame.transform.smoothscale(
                frame, (frame.get_width(), int(frame.get_height() * self.y_scale))
            )
            rotated = pygame.transform.rotozoom(scaled, angle_deg, 1.0)

        old_center = self.rect.center
        self.image = rotated
        self.rect = self.image.get_rect(center=old_center)
        self.rect.center = (self.pos.x, self.pos.y)

        # Enhanced carried stone physics
        if self.carried_stone is not None:
            self._update_carried_stone_position()

    def _update_carried_stone_position(self):
        """Smoother carried stone positioning"""
        p_half_h = self.rect.height / 2
        s_half_h = self.carried_stone.rect.height / 2
        base_x = self.pos.x
        base_y = self.pos.y - p_half_h - s_half_h + self.carry_gap
        fwd = self.last_dir
        
        # Base position
        x = base_x + fwd.x * self.carry_front_dist
        y = base_y + fwd.y * self.carry_front_dist
        
        # Moving adjustments with velocity-based smoothing
        if self.is_moving:
            # Smooth carry adjustments based on velocity
            velocity_factor = min(1.0, self.velocity.length() / SPEED)
            y -= self.carry_move_raise * velocity_factor
            
            left_vec = pygame.Vector2(fwd.y, -fwd.x)
            shift_amount = self.carry_move_side_shift * velocity_factor
            x += left_vec.x * shift_amount
            y += left_vec.y * shift_amount
            
        self.carried_stone.pos.x = x
        self.carried_stone.pos.y = y

    def can_pickup_stone(self, stone):
        if self.carried_stone is not None:
            return False
        if stone.is_carried:
            return False
        return pygame.Vector2(self.pos).distance_to(stone.pos) <= self.interaction_radius

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
