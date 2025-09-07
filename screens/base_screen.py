import pygame


class Screen:
    def __init__(self, game):
        self.game = game
        # Superficie lógica de dibujo (canvas) si existe; si no, la ventana.
        self.screen = getattr(game, "canvas", game.screen)
        # Referencia opcional a la ventana física
        self.window = game.screen

    def update(self, dt):
        """Update screen logic"""
        pass

    def draw(self):
        """Draw screen contents (dibujar en self.screen/canvas)"""
        pass

    def handle_event(self, event):
        """Handle pygame events"""
        pass
