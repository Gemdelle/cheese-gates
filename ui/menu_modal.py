import pygame
from ui.button import Button

class MenuModal:
    def __init__(self, x, y):
        # Contenedor del modal
        self.rect = pygame.Rect(0, 0, 400, 700)
        self.rect.center = (x, y)

        # Fuente y opciones
        self.font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        self.text_color = (255, 246, 170)  # amarillo clarito
        self.options = [
            {"text": "Tutorial",        "action": "tutorial"},   # <-- NUEVO
            {"text": "Start Game",      "action": "start_game"},
            {"text": "Settings",        "action": "settings"},
            {"text": "Exit to Desktop", "action": "exit"},
        ]

        # Botones (dimensiones dentro del modal)
        self.button_w = self.rect.width - 80    # margen lateral de 40 px por lado
        self.button_h = 130
        self.button_spacing = 40
        total_h = len(self.options) * self.button_h + (len(self.options) - 1) * self.button_spacing
        top_y = self.rect.centery - total_h // 2

        # Cargar skin de botón
        self.button_skin_raw = pygame.image.load("button.png").convert_alpha()

        # Crear botones como instancias Button con animación de hover
        self.buttons = []
        for i, opt in enumerate(self.options):
            cx = self.rect.centerx
            cy = top_y + i * (self.button_h + self.button_spacing) + self.button_h // 2
            btn = Button(cx, cy, self.button_w, self.button_h,
                         text=opt["text"], image=self.button_skin_raw, scale=1.0)
            # Aplicar fuente y color custom
            btn.font = self.font
            btn.text_color = self.text_color
            btn.text_surface = btn.font.render(btn.text, True, btn.text_color)
            btn.text_rect = btn.text_surface.get_rect(center=btn.rect.center)
            self.buttons.append(btn)

        # Estado de selección (hover)
        self.selected = 0

        # Mostrar cursor para el menú
        pygame.mouse.set_visible(True)

    def update(self, dt):
        # Hover por posición del mouse (transformar a coords lógicas del canvas)
        wx, wy = pygame.mouse.get_pos()
        scale = getattr(self, "game", None)
        if scale is not None:
            scale = getattr(self.game, "render_scale", 1.0) or 1.0
            x_off, y_off = getattr(self.game, "render_offset", (0, 0))
            if scale > 0:
                lx = int((wx - x_off) / scale)
                ly = int((wy - y_off) / scale)
            else:
                lx, ly = wx, wy
            mouse_pos = (lx, ly)
        else:
            mouse_pos = (wx, wy)

        hovered_index = -1
        for i, btn in enumerate(self.buttons):
            btn.update(dt, mouse_pos)
            if btn.rect.collidepoint(mouse_pos):
                hovered_index = i
        if hovered_index != -1:
            self.selected = hovered_index

    def draw(self, screen):
        # Fondo semitransparente del modal
        # Usar el tamaño actual de la ventana para que el overlay se ajuste al cambiar modo/tamaño
        s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)  # <-- se adapta al tamaño actual
        s.fill((0, 0, 0, 100))
        screen.blit(s, (0, 0))

        # Botones (con animación de hover propia)
        for btn in self.buttons:
            btn.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Actualiza seleccionado por hover (event.pos ya está en coords lógicas)
            self.selected = -1
            for i, btn in enumerate(self.buttons):
                if btn.rect.collidepoint(event.pos):
                    self.selected = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click sobre botón completo
            for i, btn in enumerate(self.buttons):
                if btn.rect.collidepoint(event.pos):
                    return self.options[i]["action"]

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if 0 <= self.selected < len(self.options):
                    return self.options[self.selected]["action"]

        return None
