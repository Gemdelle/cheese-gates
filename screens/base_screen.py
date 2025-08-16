import pygame

class Screen:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        
    def update(self, dt):
        """Update screen logic"""
        pass
        
    def draw(self):
        """Draw screen contents"""
        pass
        
    def handle_event(self, event):
        """Handle pygame events"""
        pass
