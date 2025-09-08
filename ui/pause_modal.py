import pygame
from ui.button import Button

class PauseModal:
    def __init__(self, game, x, y):
        self.game = game

        # Contenedor del modal
        self.rect = pygame.Rect(0, 0, 400, 700)
        self.rect.center = (x, y)

        # Fuente y opciones
        self.font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        self.text_color = (255, 246, 170)  # amarillo clarito
        self.options = [
            {"text": "Tutorial",        "action": "tutorial"},
            {"text": "Settings",        "action": "settings"},
            {"text": "Restart",         "action": "restart"},   # <-- cambiado aquí
            {"text": "Exit to Desktop", "action": "exit"},
        ]

        # Botones
        self.button_w = self.rect.width - 80
        self.button_h = 130
        self.button_spacing = 40
        total_h = len(self.options) * self.button_h + (len(self.options) - 1) * self.button_spacing
        top_y = self.rect.centery - total_h // 2

        self.button_skin_raw = pygame.image.load("button.png").convert_alpha()
        self.buttons = []
        for i, opt in enumerate(self.options):
            cx = self.rect.centerx
            cy = top_y + i * (self.button_h + self.button_spacing) + self.button_h // 2
            btn = Button(cx, cy, self.button_w, self.button_h,
                         text=opt["text"], image=self.button_skin_raw, scale=1.0)
            btn.font = self.font
            btn.text_color = self.text_color
            btn.text_surface = btn.font.render(btn.text, True, btn.text_color)
            btn.text_rect = btn.text_surface.get_rect(center=btn.rect.center)
            self.buttons.append(btn)

        self.selected = 0
        pygame.mouse.set_visible(True)

    def update(self, dt):
        wx, wy = pygame.mouse.get_pos()
        scale = getattr(self.game, "render_scale", 1.0) or 1.0
        x_off, y_off = getattr(self.game, "render_offset", (0, 0))
        if scale > 0:
            lx = int((wx - x_off) / scale)
            ly = int((wy - y_off) / scale)
        else:
            lx, ly = wx, wy
        mouse_pos = (lx, ly)

        hovered = -1
        for i, btn in enumerate(self.buttons):
            prev = getattr(btn, "is_hovered", False)
            btn.update(dt, mouse_pos)
            if not prev and getattr(btn, "is_hovered", False):
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_hover")
            if btn.rect.collidepoint(mouse_pos):
                hovered = i
        if hovered != -1:
            self.selected = hovered

    def draw(self, screen):
        s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        s.fill((0, 0, 0, 100))
        screen.blit(s, (0, 0))
        for btn in self.buttons:
            btn.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.selected = -1
            for i, btn in enumerate(self.buttons):
                if btn.rect.collidepoint(event.pos):
                    self.selected = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self.buttons):
                if btn.rect.collidepoint(event.pos):
                    if getattr(self.game, "audio", None):
                        self.game.audio.play_event_name("ui_click", volume=0.7)
                    return self.options[i]["action"]

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if 0 <= self.selected < len(self.options):
                    if getattr(self.game, "audio", None):
                        self.game.audio.play_event_name("ui_click", volume=0.7)
                    return self.options[self.selected]["action"]
            elif event.key == pygame.K_ESCAPE:
                return "resume"

        return None
