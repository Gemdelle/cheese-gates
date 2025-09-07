import pygame
from settings_store import load_settings, save_settings
from .base_screen import Screen


class SettingsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)

        # Fuente para textos (simple y legible)
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)

        # Opciones de configuración (indices y listas)
        # Nota: el juego dibuja en un canvas lógico; cambiamos solo la ventana física
        self.settings = {
            "resolution": {
                "options": ["1920x1080", "1280x720", "800x600"],
                "current": 0,
            },
            "window_mode": {
                # 3 modos: Pantalla Completa, Ventana Sin bordes (borderless), Ventana (redimensionable)
                # Nota: "Pantalla completa sin bordes" se unifica dentro de "Ventana Sin bordes"
                # usando el tamaño del escritorio cuando coincide la resolución seleccionada.
                "options": ["Pantalla Completa", "Ventana Sin bordes", "Ventana"],
                "current": 0,
            },
            # Extras (placeholders)
            "audio": {"options": ["On", "Off"], "current": 0},
            "colorblind_mode": {"options": ["Off", "On"], "current": 0},
        }

        # Cargar valores guardados si existen
        self._load_saved_into_state()

        # Estado de selección del menú
        self.selected = 0

        # Cache de rects renderizados
        self.option_rects = []
        self.update_option_positions()

        # Toast de confirmación (mensaje pequeño en la parte inferior)
        self.info_message = None
        self.info_timer = 0.0

        # Estado del menú desplegable (dropdown) para mouse/teclado
        self.dropdown_open = False
        self.dropdown_index = None
        self.dropdown_item_rects = []
        self.dropdown_box_rect = None
        self.dropdown_hover = -1

        # Mostrar cursor en la pantalla de Settings
        pygame.mouse.set_visible(True)

    # ============================
    # Layout
    # ============================
    def update_option_positions(self):
        """Calcular y cachear rects de todas las opciones y del botón Back."""
        self.option_rects = []

        # Título centrado
        title = self.title_font.render("Settings", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.game.WIDTH // 2, 100))
        self.title = (title, title_rect)

        # Opciones (en dos columnas: nombre a la izquierda, valor a la derecha)
        spacing = 80
        start_y = 200
        for i, (key, setting) in enumerate(self.settings.items()):
            name = key.replace("_", " ").title()
            name_surface = self.font.render(name, True, (200, 200, 255))
            name_rect = name_surface.get_rect(
                right=self.game.WIDTH // 2 - 20, centery=start_y + i * spacing
            )

            value = setting["options"][setting["current"]]
            value_surface = self.font.render(value, True, (255, 255, 255))
            value_rect = value_surface.get_rect(
                left=self.game.WIDTH // 2 + 20, centery=start_y + i * spacing
            )

            self.option_rects.append({"name": (name_surface, name_rect), "value": (value_surface, value_rect)})

        # Botón Back centrado
        back = self.font.render("Back", True, (255, 255, 255))
        back_rect = back.get_rect(center=(self.game.WIDTH // 2, start_y + len(self.settings) * spacing))
        self.back_button = (back, back_rect)

    # ============================
    # Dibujo
    # ============================
    def draw(self):
        # Limpiar fondo
        self.screen.fill((0, 0, 0))

        # Título
        self.screen.blit(*self.title)

        # Opciones
        for i, option in enumerate(self.option_rects):
            self.screen.blit(*option["name"])    # Etiqueta
            self.screen.blit(*option["value"])   # Valor actual

            # Indicador de selección (marco alrededor del valor)
            if i == self.selected:
                rect = option["value"][1]
                pygame.draw.rect(self.screen, (100, 100, 255), rect.inflate(20, 10), 2)

        # Botón Back (resaltar si está seleccionado)
        if self.selected == len(self.settings):
            pygame.draw.rect(self.screen, (100, 100, 255), self.back_button[1].inflate(20, 10), 2)
        self.screen.blit(*self.back_button)

        # Dibujar dropdown si está abierto
        if self.dropdown_open and self.dropdown_box_rect:
            pygame.draw.rect(self.screen, (30, 30, 30), self.dropdown_box_rect, border_radius=6)
            pygame.draw.rect(self.screen, (200, 200, 255), self.dropdown_box_rect, 2, border_radius=6)
            items = list(self.settings.values())[self.dropdown_index]["options"]
            for i, rect in enumerate(self.dropdown_item_rects):
                if i == self.dropdown_hover:
                    pygame.draw.rect(self.screen, (60, 60, 100), rect, border_radius=4)
                text = self.font.render(items[i], True, (255, 255, 255))
                text_rect = text.get_rect(midleft=(rect.left + 12, rect.centery))
                self.screen.blit(text, text_rect)

        # Toast informativo
        if self.info_message and self.info_timer > 0:
            info_surf = self.font.render(self.info_message, True, (255, 255, 0))  # Mensaje en amarillo
            info_rect = info_surf.get_rect(midbottom=(self.game.WIDTH // 2, self.game.HEIGHT - 30))
            bg_rect = info_rect.inflate(20, 10)
            s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            s.fill((0, 0, 0, 160))  # Fondo semitransparente para legibilidad
            self.screen.blit(s, bg_rect.topleft)
            self.screen.blit(info_surf, info_rect)

    # ============================
    # Lógica
    # ============================
    def handle_event(self, event):
        # Interacción con teclado
        if event.type == pygame.KEYDOWN:
            # Si el dropdown está abierto, navegamos dentro de él
            if self.dropdown_open:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.dropdown_hover = (self.dropdown_hover - 1) % len(self.dropdown_item_rects)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.dropdown_hover = (self.dropdown_hover + 1) % len(self.dropdown_item_rects)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._select_dropdown_index(self.dropdown_hover)
                elif event.key == pygame.K_ESCAPE:
                    self._close_dropdown()
                return

            # Navegación normal del menú
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % (len(self.settings) + 1)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % (len(self.settings) + 1)
            elif event.key == pygame.K_LEFT and self.selected < len(self.settings):
                setting = list(self.settings.values())[self.selected]
                setting["current"] = (setting["current"] - 1) % len(setting["options"])
                self.apply_settings()  # Aplicar inmediatamente
                self.update_option_positions()
            elif event.key == pygame.K_RIGHT and self.selected < len(self.settings):
                setting = list(self.settings.values())[self.selected]
                setting["current"] = (setting["current"] + 1) % len(setting["options"])
                self.apply_settings()
                self.update_option_positions()
            elif event.key == pygame.K_RETURN:
                # Enter sobre Back -> salir
                if self.selected == len(self.settings):
                    from .splash_screen import SplashScreen
                    self.game.change_screen(SplashScreen(self.game))
                else:
                    # Enter sobre una opción -> abrir dropdown
                    self._open_dropdown(self.selected)

        # Redimensionamiento: el juego escala el canvas lógicamente, no hay que tocar layout
        elif event.type == pygame.VIDEORESIZE:
            pass

        # Mouse hover dentro del dropdown
        elif event.type == pygame.MOUSEMOTION:
            if self.dropdown_open and self.dropdown_item_rects:
                self.dropdown_hover = -1
                for i, r in enumerate(self.dropdown_item_rects):
                    if r.collidepoint(event.pos):
                        self.dropdown_hover = i
                        break

        # Click de mouse (abrir/cerrar dropdown y seleccionar)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.dropdown_open:
                # Click dentro del dropdown -> seleccionar
                if self.dropdown_box_rect and self.dropdown_box_rect.collidepoint((mx, my)):
                    for i, r in enumerate(self.dropdown_item_rects):
                        if r.collidepoint((mx, my)):
                            self._select_dropdown_index(i)
                            return
                # Click fuera -> cerrar
                self._close_dropdown()
                return

            # Click en los valores/nombres de opciones -> abrir dropdown
            for i, option in enumerate(self.option_rects):
                value_rect = option["value"][1]
                name_rect = option["name"][1]
                if value_rect.collidepoint((mx, my)) or name_rect.collidepoint((mx, my)):
                    if i < len(self.settings):
                        self.selected = i
                        self._open_dropdown(i)
                        return

            # Click en Back
            if self.back_button[1].collidepoint((mx, my)):
                from .splash_screen import SplashScreen
                self.game.change_screen(SplashScreen(self.game))
                return

    def update(self, dt):
        # Reducir el temporizador del toast
        if self.info_timer > 0:
            self.info_timer = max(0.0, self.info_timer - dt)

    # ============================
    # Aplicación de ajustes de ventana
    # ============================
    def apply_settings(self):
        """
        Aplicar tamaño de ventana y modo, manteniendo la resolución lógica fija (canvas 1920x1080):
        - Pantalla Completa: FULLSCREEN.
        - Ventana Sin bordes: NOFRAME usando la resolución seleccionada (como ventana sin bordes).
        - Ventana: RESIZABLE (centrada) con la resolución elegida.
        """
        import os  # Usamos variables de entorno SDL para posicionar la ventana

        # Obtener modo de ventana
        mode = self.settings["window_mode"]["options"][self.settings["window_mode"]["current"]]

        # Obtener resolución seleccionada (física de la ventana)
        resolution_options = self.settings["resolution"]["options"]
        cur_idx = self.settings["resolution"]["current"]
        width, height = map(int, resolution_options[cur_idx].split("x"))

        # Si el usuario cambia a "Ventana", podemos forzar una más pequeña para notar el cambio
        if mode == "Ventana":
            sizes = [tuple(map(int, opt.split("x"))) for opt in resolution_options]
            min_idx = min(range(len(sizes)), key=lambda i: sizes[i][0] * sizes[i][1])
            if cur_idx != min_idx:
                self.settings["resolution"]["current"] = min_idx
                width, height = sizes[min_idx]

        # Flags de ventana y posicionamiento
        if mode == "Pantalla Completa":
            flags = pygame.FULLSCREEN
            os.environ.pop("SDL_VIDEO_CENTERED", None)
            os.environ.pop("SDL_VIDEO_WINDOW_POS", None)
        elif mode == "Ventana Sin bordes":
            flags = pygame.NOFRAME
            # Borderless: si la resolución seleccionada coincide con el escritorio -> ocupar toda la pantalla (0,0)
            # de lo contrario, usar tamaño custom centrado.
            info = pygame.display.Info()
            if width == info.current_w and height == info.current_h:
                os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
                os.environ.pop("SDL_VIDEO_CENTERED", None)
            else:
                os.environ["SDL_VIDEO_CENTERED"] = "1"
                os.environ.pop("SDL_VIDEO_WINDOW_POS", None)
        else:  # Ventana
            flags = pygame.RESIZABLE
            os.environ["SDL_VIDEO_CENTERED"] = "1"
            os.environ.pop("SDL_VIDEO_WINDOW_POS", None)

        # Aplicar modo y tamaño reales (NO cambiar la resolución lógica del canvas)
        try:
            size = (width, height)
            if mode == "Pantalla Completa":
                size = (0, 0)  # delegar a SDL la resolución actual
            elif mode == "Ventana Sin bordes":
                # Si coincide con escritorio -> borderless fullscreen
                info = pygame.display.Info()
                if width == info.current_w and height == info.current_h:
                    size = (info.current_w, info.current_h)
            # En Ventana Sin bordes (custom): usar size seleccionado
            self.game.screen = pygame.display.set_mode(size, flags)
        except Exception:
            pygame.display.quit()
            pygame.display.init()
            self.game.screen = pygame.display.set_mode((width, height), flags)

        # Persistir ajustes
        try:
            save_settings({
                "resolution": f"{width}x{height}",
                "window_mode": mode,
                "audio": self.settings["audio"]["options"][self.settings["audio"]["current"]],
                "colorblind_mode": self.settings["colorblind_mode"]["options"][self.settings["colorblind_mode"]["current"]],
            })
        except Exception:
            pass

        # Mensaje informativo (toast)
        self.info_message = f"Modo de ventana: {mode}"
        self.info_timer = 2.0

        # Título de la ventana con tamaño real
        real_w, real_h = self.game.screen.get_size()
        pygame.display.set_caption(f"Cheese Gates - {mode} - {real_w}x{real_h}")

        # Re-render de textos (por si cambió el valor mostrado)
        self.update_option_positions()

    # ============================
    # Persistencia helpers
    # ============================
    def _load_saved_into_state(self):
        data = load_settings() or {}
        # window_mode
        wm = data.get("window_mode")
        if wm in self.settings["window_mode"]["options"]:
            self.settings["window_mode"]["current"] = self.settings["window_mode"]["options"].index(wm)
        # resolution
        res = data.get("resolution")
        if res in self.settings["resolution"]["options"]:
            self.settings["resolution"]["current"] = self.settings["resolution"]["options"].index(res)
        # audio
        audio = data.get("audio")
        if audio in self.settings["audio"]["options"]:
            self.settings["audio"]["current"] = self.settings["audio"]["options"].index(audio)
        # colorblind
        cb = data.get("colorblind_mode")
        if cb in self.settings["colorblind_mode"]["options"]:
            self.settings["colorblind_mode"]["current"] = self.settings["colorblind_mode"]["options"].index(cb)

    # ============================
    # Dropdown helpers
    # ============================
    def _open_dropdown(self, index):
        """Abrir el menú desplegable para la opción en 'index'."""
        self.dropdown_open = True
        self.dropdown_index = index
        self.dropdown_hover = -1
        self.dropdown_item_rects = []

        # Caja del dropdown: debajo del valor actual
        value_rect = self.option_rects[index]["value"][1]
        items = list(self.settings.values())[index]["options"]
        item_h = max(36, value_rect.height + 10)  # Altura por item
        item_w = max(value_rect.width + 80, 260)  # Ancho mínimo
        total_h = item_h * len(items) + 12
        x = value_rect.left
        y = value_rect.bottom + 6

        # Si se sale por abajo, abrir hacia arriba
        if y + total_h > self.game.HEIGHT - 10:
            y = max(10, value_rect.top - 6 - total_h)

        self.dropdown_box_rect = pygame.Rect(x, y, item_w, total_h)

        # Crear rects para cada item
        cur_y = y + 6
        for _ in items:
            self.dropdown_item_rects.append(pygame.Rect(x + 6, cur_y, item_w - 12, item_h - 4))
            cur_y += item_h

    def _close_dropdown(self):
        """Cerrar el menú desplegable."""
        self.dropdown_open = False
        self.dropdown_index = None
        self.dropdown_item_rects = []
        self.dropdown_box_rect = None
        self.dropdown_hover = -1

    def _select_dropdown_index(self, item_idx):
        """Seleccionar el item del dropdown y aplicar los cambios."""
        if not self.dropdown_open or self.dropdown_index is None:
            return
        setting = list(self.settings.values())[self.dropdown_index]
        setting["current"] = item_idx % len(setting["options"])  # Asignar nuevo valor
        self._close_dropdown()
        self.apply_settings()
        self.update_option_positions()
