import pygame

class PauseModal:
    def __init__(self, x, y):
        # Contenedor del modal
        self.rect = pygame.Rect(0, 0, 400, 700)
        self.rect.center = (x, y)

        # Fuente y opciones (mismo estilo que MenuModal)
        self.font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        self.text_color = (255, 246, 170)  # amarillo clarito
        self.options = [
            {"text": "Settings",       "action": "settings"},
            {"text": "Select Level",   "action": "select_level"},
            {"text": "Exit to Desktop","action": "exit"},
        ]

        # Botones (dimensiones dentro del modal)
        self.button_w = self.rect.width - 80    # margen lateral 40 px por lado
        self.button_h = 130
        self.button_spacing = 40
        total_h = len(self.options) * self.button_h + (len(self.options) - 1) * self.button_spacing
        top_y = self.rect.centery - total_h // 2

        # Prepara rects de botones y textos
        self.button_rects = []
        self.text_surfaces = []
        self.text_rects = []
        for i, opt in enumerate(self.options):
            rect = pygame.Rect(0, 0, self.button_w, self.button_h)
            rect.centerx = self.rect.centerx
            rect.y = top_y + i * (self.button_h + self.button_spacing)
            self.button_rects.append(rect)

            text_surf = self.font.render(opt["text"], True, self.text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.text_surfaces.append(text_surf)
            self.text_rects.append(text_rect)

        # Cargar skin de botón y cachear escalados por rect (button.png)
        self.button_skin_raw = pygame.image.load("button.png").convert_alpha()
        self.button_skins = [
            pygame.transform.smoothscale(self.button_skin_raw, (r.width, r.height))
            for r in self.button_rects
        ]

        # Estado de selección (hover)
        self.selected = 0

        # Mostrar cursor para el menú
        pygame.mouse.set_visible(True)

    def update(self, dt):
        # Hover por posición del mouse
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                self.selected = i
                break

    def draw(self, screen):
        # Fondo semitransparente tipo overlay: usar tamaño actual de la ventana
        s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        s.fill((0, 0, 0, 100))
        screen.blit(s, (0, 0))

        # Botones con skin + texto
        for i, rect in enumerate(self.button_rects):
            screen.blit(self.button_skins[i], rect.topleft)

            # Re-centrar texto por si cambia el layout
            self.text_rects[i].center = rect.center
            screen.blit(self.text_surfaces[i], self.text_rects[i])

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Actualiza seleccionado por hover
            self.selected = -1
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click sobre botón completo
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(event.pos):
                    return self.options[i]["action"]

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if 0 <= self.selected < len(self.options):
                    return self.options[self.selected]["action"]
            elif event.key == pygame.K_ESCAPE:
                return "resume"  # cerrar el modal y volver al juego

        return None
