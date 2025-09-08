import pygame
from .base_screen import Screen
from ui.button import Button

class LevelSelectionScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.scene_key = "level_select"
        # ===== Fondo =====
        self.bg_raw = pygame.image.load("level-selection-bg.png").convert()
        self.bg = pygame.transform.smoothscale(self.bg_raw, (self.game.WIDTH, self.game.HEIGHT))

        # ===== Botón TUTORIAL con fondo button.png y fuente/color custom =====
        button_bg = pygame.image.load("button.png").convert_alpha()
        self.instructions_button = Button(
            self.game.WIDTH // 2, 160, 260, 80,  # posición un poco más arriba
            text="Tutorial",
            image=button_bg,
            scale=1.0
        )
        # Fuente/color del botón
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
            "level-1.png",   # Nivel 1
            "level-2.png",  # Nivel 2
            "level-3.png",  # Nivel 3
            "level-4.png",  # Nivel 4
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

        # ===== Tamaños por botón (W, H) — mantenemos los que ya venías usando =====
        row1_sizes = [(160, 120), (220, 210)]   # Niveles 1-2
        row2_sizes = [(290, 240), (320, 260)]   # Niveles 3-4
        self.single_row_sizes = row1_sizes + row2_sizes  # 4 en una sola fila

        # ===== Layout en UNA SOLA FILA =====
        self.row_y = self.game.HEIGHT // 2 + 60  # posición vertical de la fila
        self.single_gap = 160                # separación horizontal entre botones

        self.level_buttons = []
        # Limitar la cantidad de botones al número de niveles definidos, si aplica
        try:
            from logic.level_logic import LEVELS as _LEVELS
            self.available_levels = sorted(list(_LEVELS.keys()))
        except Exception:
            self.available_levels = [1, 2, 3, 4]
        self._create_single_row_buttons()

        # Mostrar cursor
        pygame.mouse.set_visible(True)

    # Música de escena se inicia en Game.change_screen

    def _create_single_row_buttons(self):
        """Crear los 4 botones en una sola fila, centrados, manteniendo tamaños."""
        game = self.game
        sizes = self.single_row_sizes
        # Asegurar no crear más botones que niveles disponibles
        max_buttons = min(len(sizes), len(getattr(self, 'available_levels', sizes)))
        sizes_use = sizes[:max_buttons]

        total_w = sum(w for (w, h) in sizes_use) + self.single_gap * (len(sizes_use) - 1 if sizes_use else 0)
        left_x = game.WIDTH // 2 - total_w // 2
        x_cursor = left_x

        self.level_buttons.clear()
        for i, (w, h) in enumerate(sizes_use):
            cx = x_cursor + w // 2
            img = self.level_imgs[i]
            btn = Button(
                cx, self.row_y,
                w, h,
                text="",
                image=img,   # Button lo escala a (w, h)
                scale=1.0
            )
            self.level_buttons.append(btn)
            x_cursor += w + self.single_gap

    def update(self, dt):
        # Posición de mouse transformada a coordenadas lógicas del canvas (si usás escalado)
        wx, wy = pygame.mouse.get_pos()
        scale = getattr(self.game, "render_scale", 1.0) or 1.0
        x_off, y_off = getattr(self.game, "render_offset", (0, 0))
        if scale > 0:
            lx = int((wx - x_off) / scale)
            ly = int((wy - y_off) / scale)
        else:
            lx, ly = wx, wy
        mouse_pos = (lx, ly)

        # Si tu Button.update acepta mouse_pos, pasalo; si no, cambiá a update(dt)
        try:
            prev_h = getattr(self.instructions_button, "is_hovered", False)
            self.instructions_button.update(dt, mouse_pos)
            if not prev_h and getattr(self.instructions_button, "is_hovered", False):
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_hover", volume=0.6)
            for button in self.level_buttons:
                prev = getattr(button, "is_hovered", False)
                button.update(dt, mouse_pos)
                if not prev and getattr(button, "is_hovered", False):
                    if getattr(self.game, "audio", None):
                        self.game.audio.play_event_name("ui_hover")
        except TypeError:
            self.instructions_button.update(dt)
            for button in self.level_buttons:
                button.update(dt)

    def draw(self):
        # Fondo
        self.screen.blit(self.bg, (0, 0))
        # Botón de Tutorial
        self.instructions_button.draw(self.screen)
        # Botones de nivel (una fila)
        for button in self.level_buttons:
            button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Tutorial
            if getattr(self.instructions_button, "is_hovered", False):
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click", volume=0.7)
                from .tutorial_screen import TutorialScreen
                self.game.change_screen(TutorialScreen(self.game))  # muestra tutorial-bg.png
                return

            # Niveles (4 en una fila)
            for i, button in enumerate(self.level_buttons):
                if getattr(button, "is_hovered", False):
                    if getattr(self.game, "audio", None):
                        self.game.audio.play_event_name("ui_click", volume=0.7)
                    from .game_screen import GameScreen
                    # Mapear índice de botón al número de nivel disponible
                    level_num = getattr(self, 'available_levels', [1, 2, 3, 4])[i]
                    self.game.change_screen(GameScreen(self.game, level=level_num))
                    return

        elif event.type == pygame.VIDEORESIZE:
            # Reescalar fondo y reacomodar fila
            self.bg = pygame.transform.smoothscale(self.bg_raw, (self.game.WIDTH, self.game.HEIGHT))
            self._layout_buttons()

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # ESC en niveles: regresar a la pantalla inicial (splash)
            from .splash_screen import SplashScreen
            self.game.change_screen(SplashScreen(self.game))

    def _layout_buttons(self):
        """Reubicar los 4 botones en una sola fila (p.ej., si cambia el tamaño de ventana)."""
        self._create_single_row_buttons()
