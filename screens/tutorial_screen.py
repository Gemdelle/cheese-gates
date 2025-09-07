import pygame
import math
import random
from .base_screen import Screen

class TutorialScreen(Screen):
    def __init__(self, game, bg_path="tutorial-bg.png"):
        super().__init__(game)

        # Fullscreen background
        bg_raw = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.smoothscale(bg_raw, (game.WIDTH, game.HEIGHT))

        # Text (animated like splash)
        self.font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        self.text_color = (255, 246, 170)  # pastel yellow
        self.text_string = "Press ESC to return"

        # Fade/pulse params (same vibe as splash)
        self.text_opacity = 255
        self.opacity_direction = -1   # -1 fading out, 1 fading in
        self.opacity_speed = 120      # opacity units per second
        self.min_opacity = 100
        self.max_opacity = 255

        # Build first text surface
        self.text_surface = None
        self.text_rect = None
        self._rebuild_text()  # creates text_surface + text_rect

        # Fireflies around the text (positioned off self.text_rect)
        self.fireflies = []
        self._init_fireflies(n=14)
        self.time = 0.0

        pygame.mouse.set_visible(True)

    def _rebuild_text(self):
        """(Re)create the text surface with current opacity."""
        # Render base
        base = self.font.render(self.text_string, True, self.text_color)

        # Apply opacity via multiplicative alpha
        surf = base.copy()
        alpha_layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        alpha_layer.fill((255, 255, 255, int(self.text_opacity)))
        surf.blit(alpha_layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # First-time rect placement
        if not self.text_rect:
            # Original was (H - 60). Raise by 50px ⇒ H - 110.
            y_baseline = self.game.HEIGHT - 60
            raise_by = 50
            center_y = y_baseline - raise_by
            self.text_rect = surf.get_rect(center=(self.game.WIDTH // 2, center_y))

        self.text_surface = surf

    def _init_fireflies(self, n=12):
        """Create small moving glow dots orbiting around the text area."""
        # An ellipse slightly bigger than the text area
        area = self.text_rect.inflate(260, 80)
        cx, cy = area.center

        self.fireflies.clear()
        for _ in range(n):
            self.fireflies.append({
                "cx": cx,
                "cy": cy,
                "a": area.width * 0.45 + random.uniform(-10, 10),   # horizontal radius
                "b": area.height * 0.35 + random.uniform(-8, 8),    # vertical radius
                "angle": random.uniform(0, math.tau),
                "speed": random.uniform(0.5, 1.2),                  # radians per second
                "size": random.randint(2, 4),
                "phase": random.uniform(0, math.tau),
                "alpha_base": random.randint(140, 200),
                "alpha_amp": random.randint(40, 70)
            })

    def update(self, dt):
        # Fade animation for the text (like splash)
        self.text_opacity += self.opacity_direction * self.opacity_speed * dt
        if self.text_opacity <= self.min_opacity:
            self.text_opacity = self.min_opacity
            self.opacity_direction = 1
        elif self.text_opacity >= self.max_opacity:
            self.text_opacity = self.max_opacity
            self.opacity_direction = -1
        self._rebuild_text()

        # Fireflies move & flicker
        self.time += dt
        for f in self.fireflies:
            f["angle"] = (f["angle"] + f["speed"] * dt) % math.tau
            # mild breathing of radii for organic motion
            a_breathe = 1.0 + 0.06 * math.sin(self.time * 0.9 + f["phase"])
            b_breathe = 1.0 + 0.06 * math.cos(self.time * 0.8 + f["phase"] * 0.7)
            f["x"] = f["cx"] + f["a"] * a_breathe * math.cos(f["angle"])
            f["y"] = f["cy"] + f["b"] * b_breathe * math.sin(f["angle"])
            f["alpha"] = f["alpha_base"] + f["alpha_amp"] * math.sin(self.time * 3.0 + f["phase"])

    def draw(self):
        # Background
        self.screen.blit(self.background, (0, 0))

        # Fireflies (draw before text so text sits on top)
        for f in self.fireflies:
            alpha = max(0, min(255, int(f["alpha"])))
            glow = pygame.Surface((f["size"]*4, f["size"]*4), pygame.SRCALPHA)
            center = (glow.get_width()//2, glow.get_height()//2)

            # soft outer glow
            pygame.draw.circle(glow, (255, 246, 170, alpha//6), center, f["size"]*2)
            # mid glow
            pygame.draw.circle(glow, (255, 246, 170, alpha//3), center, int(f["size"]*1.3))
            # bright core
            pygame.draw.circle(glow, (255, 246, 170, alpha), center, f["size"])

            self.screen.blit(glow, (f["x"] - center[0], f["y"] - center[1]))

        # Text on top
        self.screen.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from .splash_screen import SplashScreen
            self.game.change_screen(SplashScreen(self.game))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click also returns
            from .splash_screen import SplashScreen
            self.game.change_screen(SplashScreen(self.game))
