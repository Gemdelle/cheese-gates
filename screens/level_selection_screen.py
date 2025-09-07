import pygame
from .base_screen import Screen
from ui.button import Button

class LevelSelectionScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # ===== Fondo =====
        self.bg_raw = pygame.image.load("level-selection-bg.png").convert()
        self.bg = pygame.transform.smoothscale(self.bg_raw, (game.WIDTH, game.HEIGHT))

        # ===== Botón de instrucciones con fondo button.png y fuente/color custom =====
        button_bg = pygame.image.load("button.png").convert_alpha()
        self.instructions_button = Button(
            game.WIDTH // 2, 160, 260, 80,  # posición un poco más arriba
            text="Instructions",
            image=button_bg,
            scale=1.0
        )
        # Fuente/color del botón de instrucciones
        self.instructions_button.font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        self.instructions_button.text_color = (255, 246, 170)  # amarillo claro
        self.instructions_button.text_surface = self.instructions_button.font.render(
            self.instructions_button.text, True, self.instructions_button.text_color
        )
        self.instructions_button.text_rect = self.instructions_button.text_surface.get_rect(
            center=self.instructions_button.rect.center
        )

        # ===== Imágenes de niveles (robusto: usar fallback si falta alguna) =====
        self.level_imgs = []
        level_files = [
            "cheese.png",   # Nivel 1
            "level-2.png",  # Nivel 2
            "level-3.png",  # Nivel 3
            "level-4.png",  # Nivel 4 (opcional)
            "level-5.png",  # Nivel 5 (opcional)
        ]
        fallback_surface = None
        for fn in level_files:
            try:
                img = pygame.image.load(fn).convert_alpha()
                self.level_imgs.append(img)
                fallback_surface = img
            except Exception:
                if fallback_surface is None:
                    ph = pygame.Surface((200, 200), pygame.SRCALPHA)
                    ph.fill((80, 80, 120, 255))
                    self.level_imgs.append(ph)
                    fallback_surface = ph
                else:
                    self.level_imgs.append(fallback_surface)

        # ===== Tamaños por botón (W, H) — achicados para no superponer en hover =====
        row1_sizes = [(180, 150), (210, 200), (290, 240)]   # Fila 1 (niveles 1-2-3)
        row2_sizes = [(320, 260), (410, 280)]               # Fila 2 (niveles 4-5)
        self.row1_sizes = row1_sizes
        self.row2_sizes = row2_sizes

        # ===== Layout =====
        center_y = game.HEIGHT // 2
        row1_y = center_y - 100
        row2_y = center_y + 230
        self.edge_gap_row1 = 140
        self.edge_gap_row2 = 160

        self.level_buttons = []

        # Helper para distribuir una fila centrada
        def layout_row(sizes, y, gap_x):
            total_w = sum(w for (w, h) in sizes) + gap_x * (len(sizes) - 1)
            left_x = game.WIDTH // 2 - total_w // 2
            x_cursor = left_x
            buttons = []
            for i, (w, h) in enumerate(sizes):
                cx = x_cursor + w // 2
                btn = Button(
                    cx, y,
                    w, h,
                    text="",
                    image=self.level_imgs[len(self.level_buttons) + i],
                    scale=1.0
                )
                buttons.append(btn)
                x_cursor += w + gap_x
            return buttons

        # Crear filas
        self.level_buttons.extend(layout_row(row1_sizes, row1_y, self.edge_gap_row1))  # niveles 1..3
        self.level_buttons.extend(layout_row(row2_sizes, row2_y, self.edge_gap_row2))  # niveles 4..5

        # Mostrar cursor
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
            # Instrucciones
            if self.instructions_button.is_hovered:
                from .instructions_screen import InstructionsScreen
                self.game.change_screen(InstructionsScreen(self.game))
                return

            # Niveles (ahora 5)
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
        """Posicionar botones en 2 filas centradas, respetando tamaños por fila."""
        game = self.game
        # Reescalar fondo a tamaño lógico
        self.bg = pygame.transform.smoothscale(self.bg_raw, (game.WIDTH, game.HEIGHT))

        # Recalcular posiciones base de filas
        center_y = game.HEIGHT // 2
        row1_y = center_y - 100
        row2_y = center_y + 230

        # Distribución Fila 1
        total_w1 = sum(w for (w, h) in self.row1_sizes) + self.edge_gap_row1 * (len(self.row1_sizes) - 1)
        left_x1 = game.WIDTH // 2 - total_w1 // 2
        x_cursor = left_x1
        for i, (w, h) in enumerate(self.row1_sizes):
            idx = i
            if idx >= len(self.level_buttons):
                break
            btn = self.level_buttons[idx]
            btn.rect.size = (w, h)
            if hasattr(btn, 'original_rect') and btn.original_rect:
                btn.original_rect.size = (w, h)
            btn.rect.center = (x_cursor + w // 2, row1_y)
            if hasattr(btn, 'original_rect') and btn.original_rect:
                btn.original_rect.center = btn.rect.center
            if hasattr(btn, 'original_image') and btn.original_image is not None:
                btn.image = pygame.transform.scale(btn.original_image, (w, h))
            x_cursor += w + self.edge_gap_row1

        # Distribución Fila 2
        start_idx = len(self.row1_sizes)
        total_w2 = sum(w for (w, h) in self.row2_sizes) + self.edge_gap_row2 * (len(self.row2_sizes) - 1)
        left_x2 = game.WIDTH // 2 - total_w2 // 2
        x_cursor = left_x2
        for i, (w, h) in enumerate(self.row2_sizes):
            idx = start_idx + i
            if idx >= len(self.level_buttons):
                break
            btn = self.level_buttons[idx]
            btn.rect.size = (w, h)
            if hasattr(btn, 'original_rect') and btn.original_rect:
                btn.original_rect.size = (w, h)
            btn.rect.center = (x_cursor + w // 2, row2_y)
            if hasattr(btn, 'original_rect') and btn.original_rect:
                btn.original_rect.center = btn.rect.center
            if hasattr(btn, 'original_image') and btn.original_image is not None:
                btn.image = pygame.transform.scale(btn.original_image, (w, h))
            x_cursor += w + self.edge_gap_row2
