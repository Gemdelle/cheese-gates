import pygame
from .base_screen import Screen
from ui.button import Button

class LevelSelectionScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # ===== Fondo =====
        self.bg_raw = pygame.image.load("level-selection-bg.png").convert()
        self.bg = pygame.transform.smoothscale(self.bg_raw, (game.WIDTH, game.HEIGHT))
        # ===== Tamaños por botón (W, H) =====
        self.level_sizes = [(220, 180), (280, 250), (350, 280)]  # 1, 2, 3
        # ===== Botón de instrucciones con fondo button.png y fuente/color custom =====
        button_bg = pygame.image.load("button.png").convert_alpha()
        self.instructions_button = Button(
            game.WIDTH // 2, 200, 260, 80,
            text="Instructions",
            image=button_bg,
            scale=1.0
        )
        # Personalizar fuente y color del texto del botón de instrucciones
        self.instructions_button.font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        self.instructions_button.text_color = (255, 246, 170)  # amarillo claro
        self.instructions_button.text_surface = self.instructions_button.font.render(
            self.instructions_button.text, True, self.instructions_button.text_color
        )
        self.instructions_button.text_rect = self.instructions_button.text_surface.get_rect(
            center=self.instructions_button.rect.center
        )
        # ===== Imágenes de niveles =====
        self.level_imgs = [
            pygame.image.load("cheese.png").convert_alpha(),   # Nivel 1
            pygame.image.load("level-2.png").convert_alpha(),  # Nivel 2
            pygame.image.load("level-3.png").convert_alpha(),  # Nivel 3
        ]
        # ===== Crear botones de niveles =====
        self.level_buttons = []
        self._layout_buttons()
        # Mostrar cursor en esta pantalla
        pygame.mouse.set_visible(True)

    def update(self, dt):
    # No relayout continuo: evita que se pierda la animación de hover.
    # Solo relayout en __init__ y en VIDEORESIZE.
    # Posición de mouse transformada a coordenadas lógicas del canvas
        wx, wy = pygame.mouse.get_pos()
        scale = getattr(self.game, "render_scale", 1.0) or 1.0
        x_off, y_off = getattr(self.game, "render_offset", (0, 0))
        if scale > 0:
            lx = int((wx - x_off) / scale)
            ly = int((wy - y_off) / scale)
        else:
            lx, ly = wx, wy
        mouse_pos = (lx, ly)
        self.instructions_button.update(dt, mouse_pos)
        for button in self.level_buttons:
            button.update(dt, mouse_pos)

    def draw(self):
        # Fondo
        self.screen.blit(self.bg, (0, 0))
        # Botón de instrucciones
        self.instructions_button.draw(self.screen)
        # Botones de nivel
        for button in self.level_buttons:
            button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.instructions_button.is_hovered:
                from .instructions_screen import InstructionsScreen
                self.game.change_screen(InstructionsScreen(self.game))
            for i, button in enumerate(self.level_buttons):
                if button.is_hovered:
                    from .game_screen import GameScreen
                    self.game.change_screen(GameScreen(self.game, level=i + 1))
                    pygame.mouse.set_visible(False)
                    break
        elif event.type == pygame.VIDEORESIZE:
            # Re-layout ante cambios de ventana (el canvas sigue siendo fijo)
            self._layout_buttons()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # ESC en niveles: regresar a la pantalla inicial (splash)
            from .splash_screen import SplashScreen
            self.game.change_screen(SplashScreen(self.game))

    def _layout_buttons(self):
        """Posicionar botones centrados horizontalmente con sus tamaños propios."""
        game = self.game
        # Fondo reescalado a tamaño lógico
        self.bg = pygame.transform.smoothscale(self.bg_raw, (game.WIDTH, game.HEIGHT))
        edge_gap = 150
        center_y = game.HEIGHT // 2
        total_w = sum(w for (w, h) in self.level_sizes) + edge_gap * (len(self.level_sizes) - 1)
        left_x = game.WIDTH // 2 - total_w // 2
        if not self.level_buttons:
            x_cursor = left_x
            for i, (w, h) in enumerate(self.level_sizes):
                cx = x_cursor + w // 2
                btn = Button(
                    cx, center_y,
                    w, h,
                    text="",
                    image=self.level_imgs[i],
                    scale=1.0
                )
                self.level_buttons.append(btn)
                x_cursor += w + edge_gap
        else:
            x_cursor = left_x
            for btn, (w, h) in zip(self.level_buttons, self.level_sizes):
                # Actualizar tamaño y posición
                btn.rect.size = (w, h)
                if hasattr(btn, 'original_rect') and btn.original_rect:
                    btn.original_rect.size = (w, h)
                btn.rect.center = (x_cursor + w // 2, center_y)
                if hasattr(btn, 'original_rect') and btn.original_rect:
                    btn.original_rect.center = btn.rect.center
                # Re-escalar imagen base a su nuevo tamaño
                if hasattr(btn, 'original_image') and btn.original_image is not None:
                    btn.image = pygame.transform.scale(btn.original_image, (w, h))
                x_cursor += w + edge_gap
