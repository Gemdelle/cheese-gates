# Win Screen
import pygame
from .base_screen import Screen
from ui.button import Button

class WinScreen(Screen):
    def __init__(self, game, level=1, bg_path="win-bg.png", max_level=None):
        super().__init__(game)
        self.level = level

        # Detectar max_level si no viene dado
        if max_level is None:
            try:
                from logic.level_logic import LEVELS as _LEVELS
                self.max_level = max(_LEVELS.keys()) if _LEVELS else 3
            except Exception:
                self.max_level = 3
        else:
            self.max_level = max_level

        self.has_next = (self.level < self.max_level)

        # Fondo a pantalla completa
        bg_raw = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.smoothscale(bg_raw, (game.WIDTH, game.HEIGHT))

        # Skin, fuente y color
        button_skin = pygame.image.load("button.png").convert_alpha()
        custom_font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        text_color = (255, 246, 170)

        # Geometría base
        btn_w, btn_h = 300, 100
        center_x = game.WIDTH // 2
        y_next = int(game.HEIGHT * 0.70)
        # Si es el último nivel, bajamos un poco el menú para que quede lindo
        y_menu = int(game.HEIGHT * 0.83) if self.has_next else (int(game.HEIGHT * 0.84) + 50)

        # Botón de menú SIEMPRE
        self.menu_button = Button(center_x, y_menu, btn_w, btn_h,
                                  text="Return to Menu", image=button_skin, scale=1.0)
        self.menu_button.font = custom_font
        self.menu_button.text_color = text_color
        self.menu_button.text_surface = self.menu_button.font.render(self.menu_button.text, True, self.menu_button.text_color)
        self.menu_button.text_rect = self.menu_button.text_surface.get_rect(center=self.menu_button.rect.center)

        # Botón Next solo si hay próximo nivel
        self.next_level_btn = None
        if self.has_next:
            self.next_level_btn = Button(center_x, y_next, btn_w, btn_h,
                                         text="Next Level", image=button_skin, scale=1.0)
            self.next_level_btn.font = custom_font
            self.next_level_btn.text_color = text_color
            self.next_level_btn.text_surface = self.next_level_btn.font.render(self.next_level_btn.text, True, self.next_level_btn.text_color)
            self.next_level_btn.text_rect = self.next_level_btn.text_surface.get_rect(center=self.next_level_btn.rect.center)

        # Mostrar cursor en la pantalla de victoria
        pygame.mouse.set_visible(True)

    def update(self, dt):
        # Coordenadas lógicas para hover con escalado
        wx, wy = pygame.mouse.get_pos()
        scale = getattr(self.game, "render_scale", 1.0) or 1.0
        x_off, y_off = getattr(self.game, "render_offset", (0, 0))
        if scale > 0:
            lx = int((wx - x_off) / scale)
            ly = int((wy - y_off) / scale)
        else:
            lx, ly = wx, wy
        mouse_pos = (lx, ly)

        if self.next_level_btn is not None:
            self.next_level_btn.update(dt, mouse_pos)
        self.menu_button.update(dt, mouse_pos)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        if self.next_level_btn is not None:
            self.next_level_btn.draw(self.screen)
        self.menu_button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Next Level (solo si existe el botón)
            if self.next_level_btn is not None and self.next_level_btn.is_hovered:
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click", volume=0.7)
                from .game_screen import GameScreen
                self.game.change_screen(GameScreen(self.game, level=self.level + 1))
                return

            # Return to Menu
            if self.menu_button.is_hovered:
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click", volume=0.7)
                from .level_selection_screen import LevelSelectionScreen
                self.game.change_screen(LevelSelectionScreen(self.game))
                return

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Si hay próximo nivel: avanzar; si no, volver al menú
                if self.has_next:
                    from .game_screen import GameScreen
                    self.game.change_screen(GameScreen(self.game, level=self.level + 1))
                else:
                    from .level_selection_screen import LevelSelectionScreen
                    self.game.change_screen(LevelSelectionScreen(self.game))
                return
            elif event.key == pygame.K_ESCAPE:
                from .level_selection_screen import LevelSelectionScreen
                self.game.change_screen(LevelSelectionScreen(self.game))
                return
