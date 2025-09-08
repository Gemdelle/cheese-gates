import pygame
from .base_screen import Screen
from ui.button import Button

class LoseScreen(Screen):
    def __init__(self, game, level=1, bg_path="lose-bg.png"):
        super().__init__(game)
        self.level = level
        # Scene music will be started by Game.change_screen
        self.scene_music_name = "lose"

        # Fondo a pantalla completa
        bg_raw = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.smoothscale(bg_raw, (self.game.WIDTH, self.game.HEIGHT))

        # Botón skin
        button_skin = pygame.image.load("button.png").convert_alpha()

        # Fuente y color pedidos
        custom_font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        text_color = (255, 246, 170)  # amarillo clarito

        # Botones
        btn_w, btn_h = 300, 100
        center_x = self.game.WIDTH // 2
        y1 = int(self.game.HEIGHT * 0.70)
        y2 = int(self.game.HEIGHT * 0.83)

        self.retry_button = Button(center_x, y1, btn_w, btn_h,
                                   text="Retry", image=button_skin, scale=1.0)
        self.menu_button  = Button(center_x, y2, btn_w, btn_h,
                                   text="Return to Menu", image=button_skin, scale=1.0)

        # Aplicar fuente y color
        for b in (self.retry_button, self.menu_button):
            b.font = custom_font
            b.text_color = text_color
            b.text_surface = b.font.render(b.text, True, b.text_color)
            b.text_rect = b.text_surface.get_rect(center=b.rect.center)

        # Mostrar cursor en la pantalla de derrota
        pygame.mouse.set_visible(True)

    # Música de derrota: se inicia una sola vez al entrar (Game.change_screen)

    def update(self, dt):
        # Usar coordenadas lógicas del canvas para que el hover funcione con el escalado
        wx, wy = pygame.mouse.get_pos()
        scale = getattr(self.game, "render_scale", 1.0) or 1.0
        x_off, y_off = getattr(self.game, "render_offset", (0, 0))
        if scale > 0:
            lx = int((wx - x_off) / scale)
            ly = int((wy - y_off) / scale)
        else:
            lx, ly = wx, wy
        mouse_pos = (lx, ly)

        self.retry_button.update(dt, mouse_pos)
        self.menu_button.update(dt, mouse_pos)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.retry_button.draw(self.screen)
        self.menu_button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Usar hover o colisión directa con la posición del evento (ya transformada a lógica por Game)
            if self.retry_button.is_hovered or self.retry_button.rect.collidepoint(event.pos):
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click", volume=0.7)
                # Reinicia el mismo nivel
                from .game_screen import GameScreen  # <-- import correcto
                self.game.change_screen(GameScreen(self.game, level=self.level))
            elif self.menu_button.is_hovered or self.menu_button.rect.collidepoint(event.pos):
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click", volume=0.7)
                from .level_selection_screen import LevelSelectionScreen
                self.game.change_screen(LevelSelectionScreen(self.game))

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Retry con Enter/Espacio
                from .game_screen import GameScreen  # <-- import correcto
                self.game.change_screen(GameScreen(self.game, level=self.level))
            elif event.key == pygame.K_ESCAPE:
                # Volver al menú con ESC
                from .level_selection_screen import LevelSelectionScreen
                self.game.change_screen(LevelSelectionScreen(self.game))
