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
        edge_gap = 150  # separación ENTRE BORDES de botones

        # ===== Botón de instrucciones con fondo button.png y fuente/color custom =====
        button_bg = pygame.image.load("button.png").convert_alpha()
        self.instructions_button = Button(
            game.WIDTH // 2, 200, 260, 80,  # ajustá tamaño si querés
            text="Instructions",
            image=button_bg,
            scale=1.0
        )
        # Aplicar la fuente y color pedidos
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
        ]

        # ===== Crear botones con tamaños independientes =====
        self.level_buttons = []
        center_y = game.HEIGHT // 2

        total_w = sum(w for (w, h) in self.level_sizes) + edge_gap * (len(self.level_sizes) - 1)
        left_x = game.WIDTH // 2 - total_w // 2  # borde izquierdo del primer botón

        x_cursor = left_x
        for i, (w, h) in enumerate(self.level_sizes):
            cx = x_cursor + w // 2
            btn = Button(
                cx, center_y,
                w, h,
                text="",                # sin texto, la imagen manda
                image=level_imgs[i],    # Button lo escala a (w, h)
                scale=1.0
            )
            self.level_buttons.append(btn)
            x_cursor += w + edge_gap  # avanzar: ancho + gap

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
            if self.instructions_button.is_hovered:
                from .instructions_screen import InstructionsScreen
                self.game.change_screen(InstructionsScreen(self.game))

            for i, button in enumerate(self.level_buttons):
                if button.is_hovered:
                    from .game_screen import GameScreen
                    self.game.change_screen(GameScreen(self.game, level=i+1))
                    pygame.mouse.set_visible(False)
                    break
