import pygame
from .base_screen import Screen
from ui.button import Button

class WinScreen(Screen):
    def __init__(self, game, level=1, bg_path="win-bg.png", max_level=None):
        super().__init__(game)
        self.level = level
        # Si no te pasan el máximo, asumimos 3 niveles (ajustá si necesitás)
        self.max_level = max_level if max_level is not None else 3
        self.has_next = (self.level < self.max_level)

        # Fondo a pantalla completa
        bg_raw = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.smoothscale(bg_raw, (game.WIDTH, game.HEIGHT))

        # Skin del botón
        button_skin = pygame.image.load("button.png").convert_alpha()

        # Fuente y color (amarillo pastel)
        custom_font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        text_color = (255, 246, 170)

        # Botones
        btn_w, btn_h = 300, 100
        center_x = game.WIDTH // 2
        y_next = int(game.HEIGHT * 0.70)
        y_menu = int(game.HEIGHT * 0.83)

        self.next_level_btn = Button(center_x, y_next, btn_w, btn_h,
                                     text="Next Level", image=button_skin, scale=1.0)
        self.menu_button    = Button(center_x, y_menu, btn_w, btn_h,
                                     text="Return to Menu", image=button_skin, scale=1.0)

        # Aplicar fuente y color
        for b in (self.next_level_btn, self.menu_button):
            b.font = custom_font
            b.text_color = text_color
            b.text_surface = b.font.render(b.text, True, b.text_color)
            b.text_rect = b.text_surface.get_rect(center=b.rect.center)

        # Si NO hay próximo nivel: deshabilitar visual y funcionalmente el "Next Level"
        if not self.has_next:
            # Atenuar botón e impedir efecto hover-zoom
            try:
                self.next_level_btn.image.set_alpha(130)
            except Exception:
                pass
            self.next_level_btn.hover_scale = 1.0  # no crecer al hacer hover
            # Atenuar texto
            disabled_color = (170, 170, 170)
            self.next_level_btn.text_color = disabled_color
            self.next_level_btn.text_surface = custom_font.render("Next Level", True, disabled_color)
            self.next_level_btn.text_rect = self.next_level_btn.text_surface.get_rect(center=self.next_level_btn.rect.center)

        # Mostrar cursor en la pantalla de victoria
        pygame.mouse.set_visible(True)

    def update(self, dt):
        # Igual actualizamos para hover del menú
        self.next_level_btn.update(dt)
        self.menu_button.update(dt)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.next_level_btn.draw(self.screen)
        self.menu_button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Next Level (solo si hay próximo)
            if self.next_level_btn.is_hovered and self.has_next:
                from .game_screen import GameScreen
                self.game.change_screen(GameScreen(self.game, level=self.level + 1))
                pygame.mouse.set_visible(False)
            # Return to Menu
            elif self.menu_button.is_hovered:
                from .level_selection_screen import LevelSelectionScreen
                self.game.change_screen(LevelSelectionScreen(self.game))

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Si hay próximo nivel: avanzar; si no, volver al menú
                if self.has_next:
                    from .game_screen import GameScreen
                    self.game.change_screen(GameScreen(self.game, level=self.level + 1))
                    pygame.mouse.set_visible(False)
                else:
                    from .level_selection_screen import LevelSelectionScreen
                    self.game.change_screen(LevelSelectionScreen(self.game))
            elif event.key == pygame.K_ESCAPE:
                # Volver al menú con ESC
                from .level_selection_screen import LevelSelectionScreen
                self.game.change_screen(LevelSelectionScreen(self.game))
