# main.py — Cheese Gates: standing vs moving sprites + rotation
import sys
import math
import pygame

# ---------- Config ----------
WIDTH, HEIGHT = 1920, 1080
SPEED = 260.0  # px/s
PLAYER_SIZE = (140, 150)  # (w, h) for both standing/moving sprites

# ---------- Player ----------
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
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

        # Switch base image depending on movement state
        self.base_image = self.original_moving if moved else self.original_standing

        # Keep on screen using current rotated frame size
        half_w, half_h = self.rect.width / 2, self.rect.height / 2
        self.pos.x = max(bounds_rect.left + half_w, min(self.pos.x, bounds_rect.right - half_w))
        self.pos.y = max(bounds_rect.top + half_h,  min(self.pos.y, bounds_rect.bottom - half_h))

        # Rotate to face last_dir
        angle_deg = -math.degrees(math.atan2(self.last_dir.y, self.last_dir.x)) + self.angle_offset_deg
        rotated = pygame.transform.rotozoom(self.base_image, angle_deg, 1.0)

        old_center = self.rect.center
        self.image = rotated
        self.rect = self.image.get_rect(center=old_center)
        self.rect.center = (self.pos.x, self.pos.y)

# ---------- Game ----------
def main():
    pygame.init()
    pygame.display.set_caption("Cheese Gates")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Background (scaled if needed)
    background_raw = pygame.image.load("background.jpg").convert()
    if background_raw.get_width() != WIDTH or background_raw.get_height() != HEIGHT:
        background = pygame.transform.smoothscale(background_raw, (WIDTH, HEIGHT))
    else:
        background = background_raw

    player = Player((WIDTH // 2, HEIGHT // 2))
    all_sprites = pygame.sprite.Group(player)
    world_rect = screen.get_rect()

    running = True
    while running:
        dt = clock.tick(120) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        all_sprites.update(dt, world_rect)

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        pygame.display.set_caption(f"Cheese Gates  |  FPS: {int(clock.get_fps()):>3}")
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
