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
        self.instructions_button.text_color = (255, 246, 170)  # amarillo clarito
        self.instructions_button.text_surface = self.instructions_button.font.render(
            self.instructions_button.text, True, self.instructions_button.text_color
        )
        self.instructions_button.text_rect = self.instructions_button.text_surface.get_rect(
            center=self.instructions_button.rect.center
        )

        # ===== Imágenes de niveles =====
        level_imgs = [
            pygame.image.load("cheese.png").convert_alpha(),   # Nivel 1
            pygame.image.load("level-2.png").convert_alpha(),  # Nivel 2
            pygame.image.load("level-3.png").convert_alpha(),  # Nivel 3
            pygame.image.load("level-4.png").convert_alpha(),  # Nivel 4
            pygame.image.load("level-5.png").convert_alpha(),  # Nivel 5
        ]

        # ===== Tamaños por botón (W, H) — achicados para no superponer en hover =====
        # Fila 1 (niveles 1-2-3)
        row1_sizes = [(180, 150), (210, 200), (290, 240)]
        # Fila 2 (niveles 4-5)
        row2_sizes = [(320, 260), (410, 280)]

        # ===== Layout =====
        center_y = game.HEIGHT // 2
        row_gap_y = 500         # separación vertical entre filas
        row1_y = center_y - 100
        row2_y = center_y + 230

        edge_gap_row1 = 140     # separación horizontal en fila 1
        edge_gap_row2 = 160     # separación horizontal en fila 2

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
                    text="",                # sin texto, la imagen manda
                    image=level_imgs[len(self.level_buttons) + i],  # la imagen correspondiente
                    scale=1.0
                )
                buttons.append(btn)
                x_cursor += w + gap_x
            return buttons

        # Crear filas
        self.level_buttons.extend(layout_row(row1_sizes, row1_y, edge_gap_row1))  # niveles 1..3
        self.level_buttons.extend(layout_row(row2_sizes, row2_y, edge_gap_row2))  # niveles 4..5

        # Mostrar cursor
        pygame.mouse.set_visible(True)

    def update(self, dt):
        self.instructions_button.update(dt)
        for button in self.level_buttons:
            button.update(dt)

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
                    self.game.change_screen(GameScreen(self.game, level=i+1))
                    pygame.mouse.set_visible(False)
                    break
