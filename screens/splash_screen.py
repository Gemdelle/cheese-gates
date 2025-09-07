import pygame
from .base_screen import Screen
from ui.menu_modal import MenuModal

class SplashScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.background = pygame.image.load("splash.png").convert()
        self.original_bg = pygame.transform.scale(self.background, (game.WIDTH, game.HEIGHT))

        # Sin zoom: mostramos el mensaje enseguida
        self.show_press_enter = True

        self.menu_modal = None
        self.text_visible = True

        # Texto "Press Enter to Start" con fade
        self.font = pygame.font.Font("font/BlackCastleMF.ttf", 48)
        self.text_opacity = 255
        self.opacity_direction = -1  # -1 fade out, 1 fade in
        self.opacity_speed = 120
        self.min_opacity = 100
        self.max_opacity = 255
        self.text_rect = self.text = None
        self.update_text()

        # Mostrar cursor en el splash
        pygame.mouse.set_visible(True)

    def update_text(self):
        """Recrear superficie del texto con la opacidad actual"""
        self.text = self.font.render("Press Enter to Start", True, (255, 255, 255))
        alpha_surface = pygame.Surface(self.text.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, int(self.text_opacity)))
        self.text.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if not self.text_rect:
            self.text_rect = self.text.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT - 100))

    def update(self, dt):
        if self.show_press_enter and self.text_visible and not self.menu_modal:
            # Animación de fade del texto
            self.text_opacity += self.opacity_direction * self.opacity_speed * dt
            if self.text_opacity <= self.min_opacity:
                self.text_opacity = self.min_opacity
                self.opacity_direction = 1
            elif self.text_opacity >= self.max_opacity:
                self.text_opacity = self.max_opacity
                self.opacity_direction = -1
            self.update_text()

        if self.menu_modal:
            self.menu_modal.update(dt)

    def draw(self):
        # Fondo normal sin zoom
        self.screen.blit(self.original_bg, (0, 0))

        # Texto "Press Enter to Start"
        if self.show_press_enter and self.text_visible and not self.menu_modal:
            self.screen.blit(self.text, self.text_rect)

        # Menú
        if self.menu_modal:
            self.menu_modal.draw(self.screen)

    def handle_event(self, event):
        if self.menu_modal:
            option = self.menu_modal.handle_event(event)
            if option:
                if option == "start_game":
                    from .level_selection_screen import LevelSelectionScreen
                    self.game.change_screen(LevelSelectionScreen(self.game))
                elif option == "settings":
                    from .settings_screen import SettingsScreen
                    self.game.change_screen(SettingsScreen(self.game))
                elif option == "tutorial":  # <-- NUEVO
                    from .tutorial_screen import TutorialScreen
                    self.game.change_screen(TutorialScreen(self.game, bg_path="tutorial-bg.png"))
                elif option == "exit":
                    pygame.quit()
                    import sys
                    sys.exit()

        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.show_press_enter:
                self.text_visible = False
                self.menu_modal = MenuModal(self.game.WIDTH // 2, self.game.HEIGHT // 2)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.show_press_enter:
                self.text_visible = False
                self.menu_modal = MenuModal(self.game.WIDTH // 2, self.game.HEIGHT // 2)
