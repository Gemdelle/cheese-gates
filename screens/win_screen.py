# win_screen.py
import pygame
from .base_screen import Screen
from ui.button import Button

class WinScreen(Screen):
    def __init__(self, game, level, bg_path="win-bg.png", max_level=4):
        super().__init__(game)
        self.level = level
        self.max_level = max_level

        # Fondo
        bg_raw = pygame.image.load(bg_path).convert()
        if bg_raw.get_width() != game.WIDTH or bg_raw.get_height() != game.HEIGHT:
            self.background = pygame.transform.smoothscale(bg_raw, (game.WIDTH, game.HEIGHT))
        else:
            self.background = bg_raw

        # Título
        self.title_font  = pygame.font.Font("font/BlackCastleMF.ttf", 72)
        self.title_color = (255, 246, 170)

        # ÚNICO botón: Main Menu (más abajo en Y)
        skin = pygame.image.load("button.png").convert_alpha()
        btn_w, btn_h = 340, 130
        btn_cy = int(self.game.HEIGHT * 0.84) + 50  # más bajo

        self.main_btn = Button(self.game.WIDTH // 2, btn_cy, btn_w, btn_h,
                               text="Main Menu", image=skin, scale=1)
        self.main_btn.font = pygame.font.Font("font/BlackCastleMF.ttf", 40)
        self.main_btn.text_color = (255, 246, 170)
        self.main_btn.text_surface = self.main_btn.font.render(self.main_btn.text, True, self.main_btn.text_color)
        self.main_btn.text_rect = self.main_btn.text_surface.get_rect(center=self.main_btn.rect.center)

        pygame.mouse.set_visible(True)

    def update(self, dt):
        # Hover con coords lógicas por si hay escalado
        wx, wy = pygame.mouse.get_pos()
        scale = getattr(self.game, "render_scale", 1.0) or 1.0
        x_off, y_off = getattr(self.game, "render_offset", (0, 0))
        if scale > 0:
            lx = int((wx - x_off) / scale)
            ly = int((wy - y_off) / scale)
        else:
            lx, ly = wx, wy
        try:
            self.main_btn.update(dt, (lx, ly))
        except TypeError:
            self.main_btn.update(dt)

    def draw(self):
        # <-- sin parámetro; usa self.screen
        self.screen.blit(self.background, (0, 0))
        self.main_btn.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.main_btn.rect.collidepoint(event.pos):
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click", volume=0.7)
                from .splash_screen import SplashScreen
                self.game.change_screen(SplashScreen(self.game))
                return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                from .splash_screen import SplashScreen
                self.game.change_screen(SplashScreen(self.game))
                return
