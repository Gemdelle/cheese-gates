import math
import random
import pygame
from settings_store import load_settings, save_settings
from .base_screen import Screen


class SettingsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.scene_key = "settings"

        # Fonts
        try:
            self.title_font = pygame.font.Font("font/BlackCastleMF.ttf", 56)
            self.font = pygame.font.Font("font/BlackCastleMF.ttf", 30)
        except Exception:
            self.title_font = pygame.font.Font(None, 52)
            self.font = pygame.font.Font(None, 32)

        # Background
        try:
            bg_raw = pygame.image.load("background.jpg").convert()
            self.background = pygame.transform.smoothscale(bg_raw, (self.game.WIDTH, self.game.HEIGHT))
        except Exception:
            self.background = None
        # Build a warm orange gradient once (used regardless of bg image)
        self.grad_bg = self._build_orange_gradient(self.game.WIDTH, self.game.HEIGHT)

        # Settings model
        self.settings = {
            "resolution": {"options": ["1920x1080", "1280x720", "800x600"], "current": 0},
            "window_mode": {"options": ["Pantalla Completa", "Ventana Sin bordes", "Ventana"], "current": 0},
            "music": {"options": ["On", "Off"], "current": 0},
            "sfx": {"options": ["On", "Off"], "current": 0},
        }
        # Volume state (0.0 .. 1.0)
        self.music_volume = 0.8
        self.sfx_volume = 0.8
        # Slider UI state
        self.slider_music_rect = None   # track rect
        self.slider_sfx_rect = None     # track rect
        self.dragging_music = False
        self.dragging_sfx = False
        self._load_saved_into_state()

        # UI state
        self.selected = 0
        self.option_rects = []
        self.info_message = None
        self.info_timer = 0.0

        self.dropdown_open = False
        self.dropdown_index = None
        self.dropdown_item_rects = []
        self.dropdown_box_rect = None
        self.dropdown_hover = -1

        # Particles
        self._init_particles()

        # Cursor visible
        pygame.mouse.set_visible(True)

        # Apply saved audio flags immediately
        try:
            music_on = (self.settings["music"]["options"][self.settings["music"]["current"]] == "On")
            sfx_on = (self.settings["sfx"]["options"][self.settings["sfx"]["current"]] == "On")
            if getattr(self.game, "audio", None):
                self.game.audio.set_music_enabled(bool(music_on))
                self.game.audio.set_sfx_enabled(bool(sfx_on))
                self.game.audio.set_music_volume(float(self.music_volume))
                self.game.audio.set_sfx_volume(float(self.sfx_volume))
        except Exception:
            pass

        # Scene music starts in Game.change_screen

        # Layout cache
        self.update_option_positions()

    # Layout calculation
    def update_option_positions(self):
        self.option_rects = []

        title = self.title_font.render("Settings", True, (240, 240, 255))
        title_rect = title.get_rect(center=(self.game.WIDTH // 2, 120))
        self.title = (title, title_rect)

        spacing = 78
        start_y = 220
        for i, (key, setting) in enumerate(self.settings.items()):
            name = key.replace("_", " ").title()
            name_surface = self.font.render(name, True, (210, 215, 255))
            name_rect = name_surface.get_rect(right=self.game.WIDTH // 2 - 20, centery=start_y + i * spacing)

            value = setting["options"][setting["current"]]
            value_surface = self.font.render(value, True, (255, 255, 255))
            value_rect = value_surface.get_rect(left=self.game.WIDTH // 2 + 20, centery=start_y + i * spacing)

            self.option_rects.append({"name": (name_surface, name_rect), "value": (value_surface, value_rect)})

            # Prepare slider positions for Music and Sfx
            track_w, track_h = 260, 10
            track_margin = 16
            track_x = value_rect.left
            track_y = value_rect.centery + track_margin
            track_rect = pygame.Rect(track_x, track_y, track_w, track_h)
            if key == "music":
                self.slider_music_rect = track_rect
            elif key == "sfx":
                self.slider_sfx_rect = track_rect

        back = self.font.render("Back", True, (255, 255, 255))
        back_rect = back.get_rect(center=(self.game.WIDTH // 2, start_y + len(self.settings) * spacing))
        self.back_button = (back, back_rect)

    # Drawing
    def draw(self):
        # Background: warm orange gradient
        if self.grad_bg:
            self.screen.blit(self.grad_bg, (0, 0))
        else:
            self.screen.fill((34, 19, 6))

        # Particles
        self._draw_particles()

        # Panel
        panel_rect = pygame.Rect(0, 0, int(self.game.WIDTH * 0.66), int(self.game.HEIGHT * 0.70))
        panel_rect.center = (self.game.WIDTH // 2, self.game.HEIGHT // 2)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel.fill((22, 24, 36, 200))
        self.screen.blit(panel, panel_rect.topleft)
        pygame.draw.rect(self.screen, (80, 90, 140), panel_rect, 2, border_radius=16)

        # Title
        self.screen.blit(*self.title)

        # Options
        for i, option in enumerate(self.option_rects):
            self.screen.blit(*option["name"])
            self.screen.blit(*option["value"])
            if i == self.selected:
                rect = option["value"][1].inflate(20, 10)
                pygame.draw.rect(self.screen, (140, 150, 240), rect, 2, border_radius=8)
            name_r = option["name"][1]
            pygame.draw.line(self.screen, (40, 44, 66), (panel_rect.left + 40, name_r.bottom + 20), (panel_rect.right - 40, name_r.bottom + 20), 1)

        # Back
        if self.selected == len(self.settings):
            pygame.draw.rect(self.screen, (140, 150, 240), self.back_button[1].inflate(20, 10), 2, border_radius=8)
        self.screen.blit(*self.back_button)

        # Dropdown
        if self.dropdown_open and self.dropdown_box_rect:
            pygame.draw.rect(self.screen, (25, 28, 44), self.dropdown_box_rect, border_radius=8)
            pygame.draw.rect(self.screen, (140, 150, 240), self.dropdown_box_rect, 2, border_radius=8)
            items = list(self.settings.values())[self.dropdown_index]["options"]
            for i, rect in enumerate(self.dropdown_item_rects):
                if i == self.dropdown_hover:
                    pygame.draw.rect(self.screen, (60, 64, 110), rect, border_radius=6)
                text = self.font.render(items[i], True, (235, 238, 255))
                text_rect = text.get_rect(midleft=(rect.left + 12, rect.centery))
                self.screen.blit(text, text_rect)

        # Volume sliders (draw after options so they appear aligned under the value text)
        self._draw_slider(self.slider_music_rect, self.music_volume, label="Music Vol")
        self._draw_slider(self.slider_sfx_rect, self.sfx_volume, label="SFX Vol")

        # Toast
        if self.info_message and self.info_timer > 0:
            info_surf = self.font.render(self.info_message, True, (255, 246, 170))
            info_rect = info_surf.get_rect(midbottom=(self.game.WIDTH // 2, self.game.HEIGHT - 30))
            bg_rect = info_surf.get_rect(midbottom=(self.game.WIDTH // 2, self.game.HEIGHT - 30)).inflate(20, 10)
            s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            s.fill((10, 12, 20, 160))
            self.screen.blit(s, bg_rect.topleft)
            self.screen.blit(info_surf, info_rect)

    # Events
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.dropdown_open:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.dropdown_hover = (self.dropdown_hover - 1) % len(self.dropdown_item_rects)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.dropdown_hover = (self.dropdown_hover + 1) % len(self.dropdown_item_rects)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    try:
                        if getattr(self.game, "audio", None):
                            self.game.audio.play_event_name("ui_click")
                    except Exception:
                        pass
                    self._select_dropdown_index(self.dropdown_hover)
                elif event.key == pygame.K_ESCAPE:
                    self._close_dropdown()
                return

            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % (len(self.settings) + 1)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % (len(self.settings) + 1)
            elif event.key == pygame.K_LEFT and self.selected < len(self.settings):
                setting = list(self.settings.values())[self.selected]
                setting["current"] = (setting["current"] - 1) % len(setting["options"])
                try:
                    if getattr(self.game, "audio", None):
                        self.game.audio.play_event_name("ui_click")
                except Exception:
                    pass
                self.apply_settings()
                self.update_option_positions()
            elif event.key == pygame.K_RIGHT and self.selected < len(self.settings):
                setting = list(self.settings.values())[self.selected]
                setting["current"] = (setting["current"] + 1) % len(setting["options"])
                try:
                    if getattr(self.game, "audio", None):
                        self.game.audio.play_event_name("ui_click")
                except Exception:
                    pass
                self.apply_settings()
                self.update_option_positions()
            elif event.key == pygame.K_RETURN:
                if self.selected == len(self.settings):
                    try:
                        if getattr(self.game, "audio", None):
                            self.game.audio.play_event_name("ui_click")
                    except Exception:
                        pass
                    from .splash_screen import SplashScreen
                    self.game.change_screen(SplashScreen(self.game))
                else:
                    try:
                        if getattr(self.game, "audio", None):
                            self.game.audio.play_event_name("ui_click")
                    except Exception:
                        pass
                    self._open_dropdown(self.selected)

        elif event.type == pygame.MOUSEMOTION:
            # While dragging sliders, update values continuously
            if self.dragging_music or self.dragging_sfx:
                mx, my = event.pos
                self._handle_slider_mouse(mx, my, is_down=False)
                return
            # Dropdown hover feedback
            if self.dropdown_open and self.dropdown_item_rects:
                prev = self.dropdown_hover
                self.dropdown_hover = -1
                for i, r in enumerate(self.dropdown_item_rects):
                    if r.collidepoint(event.pos):
                        self.dropdown_hover = i
                        break
                if self.dropdown_hover != prev and self.dropdown_hover != -1:
                    try:
                        if getattr(self.game, "audio", None):
                            self.game.audio.play_event_name("ui_hover")
                    except Exception:
                        pass

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Check sliders first
            if self._handle_slider_mouse(mx, my, is_down=True):
                return
            if self.dropdown_open:
                if self.dropdown_box_rect and self.dropdown_box_rect.collidepoint((mx, my)):
                    for i, r in enumerate(self.dropdown_item_rects):
                        if r.collidepoint((mx, my)):
                            try:
                                if getattr(self.game, "audio", None):
                                    self.game.audio.play_event_name("ui_click")
                            except Exception:
                                pass
                            self._select_dropdown_index(i)
                            return
                self._close_dropdown()
                return

            for i, option in enumerate(self.option_rects):
                value_rect = option["value"][1]
                name_rect = option["name"][1]
                if value_rect.collidepoint((mx, my)) or name_rect.collidepoint((mx, my)):
                    if i < len(self.settings):
                        self.selected = i
                        try:
                            if getattr(self.game, "audio", None):
                                self.game.audio.play_event_name("ui_click")
                        except Exception:
                            pass
                        self._open_dropdown(i)
                        return

            if self.back_button[1].collidepoint((mx, my)):
                try:
                    if getattr(self.game, "audio", None):
                        self.game.audio.play_event_name("ui_click")
                except Exception:
                    pass
                from .splash_screen import SplashScreen
                self.game.change_screen(SplashScreen(self.game))
                return

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Stop dragging sliders
            self.dragging_music = False
            self.dragging_sfx = False

        

    def update(self, dt):
        if self.info_timer > 0:
            self.info_timer = max(0.0, self.info_timer - dt)
        self._update_particles(dt)

    # Apply
    def apply_settings(self):
        import os
        mode = self.settings["window_mode"]["options"][self.settings["window_mode"]["current"]]
        resolution_options = self.settings["resolution"]["options"]
        cur_idx = self.settings["resolution"]["current"]
        width, height = map(int, resolution_options[cur_idx].split("x"))

        if mode == "Ventana":
            sizes = [tuple(map(int, opt.split("x"))) for opt in resolution_options]
            min_idx = min(range(len(sizes)), key=lambda i: sizes[i][0] * sizes[i][1])
            if cur_idx != min_idx:
                self.settings["resolution"]["current"] = min_idx
                width, height = sizes[min_idx]

        if mode == "Pantalla Completa":
            flags = pygame.FULLSCREEN
            os.environ.pop("SDL_VIDEO_CENTERED", None)
            os.environ.pop("SDL_VIDEO_WINDOW_POS", None)
        elif mode == "Ventana Sin bordes":
            flags = pygame.NOFRAME
            info = pygame.display.Info()
            if width == info.current_w and height == info.current_h:
                os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
                os.environ.pop("SDL_VIDEO_CENTERED", None)
            else:
                os.environ["SDL_VIDEO_CENTERED"] = "1"
                os.environ.pop("SDL_VIDEO_WINDOW_POS", None)
        else:
            flags = pygame.RESIZABLE
            os.environ["SDL_VIDEO_CENTERED"] = "1"
            os.environ.pop("SDL_VIDEO_WINDOW_POS", None)

        try:
            size = (width, height)
            if mode == "Pantalla Completa":
                size = (0, 0)
            elif mode == "Ventana Sin bordes":
                info = pygame.display.Info()
                if width == info.current_w and height == info.current_h:
                    size = (info.current_w, info.current_h)
            self.game.screen = pygame.display.set_mode(size, flags)
        except Exception:
            pygame.display.quit()
            pygame.display.init()
            self.game.screen = pygame.display.set_mode((width, height), flags)

        # Audio toggles -> SoundManager
        music_on = (self.settings["music"]["options"][self.settings["music"]["current"]] == "On")
        sfx_on = (self.settings["sfx"]["options"][self.settings["sfx"]["current"]] == "On")
        try:
            if getattr(self.game, "audio", None):
                self.game.audio.set_music_enabled(bool(music_on))
                self.game.audio.set_sfx_enabled(bool(sfx_on))
                self.game.audio.set_music_volume(float(self.music_volume))
                self.game.audio.set_sfx_volume(float(self.sfx_volume))
        except Exception:
            pass

        # Persist
        try:
            save_settings({
                "resolution": f"{width}x{height}",
                "window_mode": mode,
                "music": self.settings["music"]["options"][self.settings["music"]["current"]],
                "sfx": self.settings["sfx"]["options"][self.settings["sfx"]["current"]],
                "music_volume": round(float(self.music_volume), 3),
                "sfx_volume": round(float(self.sfx_volume), 3),
            })
        except Exception:
            pass

        # Toast + caption
        self.info_message = f"Modo de ventana: {mode} | Música: {'On' if music_on else 'Off'} | SFX: {'On' if sfx_on else 'Off'}"
        self.info_timer = 2.0
        real_w, real_h = self.game.screen.get_size()
        pygame.display.set_caption(f"Cheese Gates - {mode} - {real_w}x{real_h}")
        self.update_option_positions()

    # Persistence
    def _load_saved_into_state(self):
        data = load_settings() or {}
        wm = data.get("window_mode")
        if wm in self.settings["window_mode"]["options"]:
            self.settings["window_mode"]["current"] = self.settings["window_mode"]["options"].index(wm)
        res = data.get("resolution")
        if res in self.settings["resolution"]["options"]:
            self.settings["resolution"]["current"] = self.settings["resolution"]["options"].index(res)
        audio = data.get("audio")
        music = data.get("music")
        sfx = data.get("sfx")
        if music in self.settings["music"]["options"]:
            self.settings["music"]["current"] = self.settings["music"]["options"].index(music)
        elif audio in ("On", "Off"):
            self.settings["music"]["current"] = self.settings["music"]["options"].index(audio)
        if sfx in self.settings["sfx"]["options"]:
            self.settings["sfx"]["current"] = self.settings["sfx"]["options"].index(sfx)
        elif audio in ("On", "Off"):
            self.settings["sfx"]["current"] = self.settings["sfx"]["options"].index(audio)
        # Volumes (0.0..1.0)
        mv = data.get("music_volume")
        sv = data.get("sfx_volume")
        try:
            if mv is not None:
                self.music_volume = max(0.0, min(1.0, float(mv)))
        except Exception:
            pass
        try:
            if sv is not None:
                self.sfx_volume = max(0.0, min(1.0, float(sv)))
        except Exception:
            pass
    # colorblind option removed

    # Dropdown helpers
    def _open_dropdown(self, index):
        self.dropdown_open = True
        self.dropdown_index = index
        self.dropdown_hover = -1
        self.dropdown_item_rects = []
        value_rect = self.option_rects[index]["value"][1]
        items = list(self.settings.values())[index]["options"]
        item_h = max(36, value_rect.height + 10)
        item_w = max(value_rect.width + 80, 260)
        total_h = item_h * len(items) + 12
        x = value_rect.left
        y = value_rect.bottom + 6
        if y + total_h > self.game.HEIGHT - 10:
            y = max(10, value_rect.top - 6 - total_h)
        self.dropdown_box_rect = pygame.Rect(x, y, item_w, total_h)
        cur_y = y + 6
        for _ in items:
            self.dropdown_item_rects.append(pygame.Rect(x + 6, cur_y, item_w - 12, item_h - 4))
            cur_y += item_h

    def _close_dropdown(self):
        self.dropdown_open = False
        self.dropdown_index = None
        self.dropdown_item_rects = []
        self.dropdown_box_rect = None
        self.dropdown_hover = -1

    def _select_dropdown_index(self, item_idx):
        if not self.dropdown_open or self.dropdown_index is None:
            return
        setting = list(self.settings.values())[self.dropdown_index]
        setting["current"] = item_idx % len(setting["options"])
        self._close_dropdown()
        self.apply_settings()
        self.update_option_positions()

    # Particles
    def _init_particles(self):
        self.particles = []
        for _ in range(50):
            self.particles.append(self._make_particle(spawn_bottom=True))

    def _make_particle(self, spawn_bottom=False):
        x = random.uniform(0, self.game.WIDTH)
        y = random.uniform(self.game.HEIGHT * 0.5, self.game.HEIGHT + 50) if spawn_bottom else random.uniform(-50, self.game.HEIGHT)
        speed = random.uniform(20, 50)
        radius = random.uniform(1.0, 2.5)
        phase = random.uniform(0, math.tau)
        return {"x": x, "y": y, "speed": speed, "r": radius, "phase": phase}

    def _update_particles(self, dt):
        for i, p in enumerate(self.particles):
            p["y"] -= p["speed"] * dt
            p["phase"] += dt * 2.0
            if p["y"] < -60:
                self.particles[i] = self._make_particle(spawn_bottom=True)

    def _draw_particles(self):
        for p in self.particles:
            pulse = 0.5 + 0.5 * math.sin(p["phase"])  # 0..1
            alpha = int(80 + 120 * pulse)              # 80..200
            r = p["r"]
            s = pygame.Surface((int(r*6), int(r*6)), pygame.SRCALPHA)
            center = (s.get_width()//2, s.get_height()//2)
            pygame.draw.circle(s, (255, 255, 255, alpha//3), center, int(r*3))
            pygame.draw.circle(s, (255, 255, 255, alpha), center, int(r))
            self.screen.blit(s, (p["x"] - center[0], p["y"] - center[1]))

    # Gradient builder
    def _build_orange_gradient(self, w: int, h: int) -> pygame.Surface:
        surf = pygame.Surface((w, h)).convert()
        # Colors: top -> mid -> bottom for a pleasant warm gradient
        top = (255, 176, 88)    # light orange
        mid = (255, 140, 60)    # richer orange
        bot = (120, 50, 12)     # deep brown-orange
        for y in range(h):
            t = y / max(1, h - 1)
            if t < 0.5:
                k = t / 0.5
                r = int(top[0] + (mid[0] - top[0]) * k)
                g = int(top[1] + (mid[1] - top[1]) * k)
                b = int(top[2] + (mid[2] - top[2]) * k)
            else:
                k = (t - 0.5) / 0.5
                r = int(mid[0] + (bot[0] - mid[0]) * k)
                g = int(mid[1] + (bot[1] - mid[1]) * k)
                b = int(mid[2] + (bot[2] - mid[2]) * k)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
        return surf

    # -------- Volume slider helpers --------
    def _draw_slider(self, track_rect: pygame.Rect | None, value: float, label: str = ""):
        if not track_rect:
            return
        # Track
        pygame.draw.rect(self.screen, (40, 44, 66), track_rect, border_radius=6)
        # Fill
        clamped = max(0.0, min(1.0, float(value)))
        fill_w = int(track_rect.width * clamped)
        fill_rect = pygame.Rect(track_rect.left, track_rect.top, fill_w, track_rect.height)
        pygame.draw.rect(self.screen, (140, 150, 240), fill_rect, border_radius=6)
        # Knob
        knob_x = track_rect.left + fill_w
        knob_y = track_rect.centery
        pygame.draw.circle(self.screen, (220, 225, 255), (knob_x, knob_y), 8)
        # Label + percent
        if label:
            percent = int(round(clamped * 100))
            txt = self.font.render(f"{label}: {percent}%", True, (215, 220, 255))
            txt_rect = txt.get_rect(left=track_rect.left, bottom=track_rect.top - 6)
            self.screen.blit(txt, txt_rect)

    def _handle_slider_mouse(self, mx: int, my: int, *, is_down: bool) -> bool:
        """Return True if a slider interaction was handled."""
        handled = False
        # Music slider
        if self.slider_music_rect and (self.dragging_music or self.slider_music_rect.collidepoint((mx, my))):
            if is_down:
                self.dragging_music = True
            if self.dragging_music:
                self.music_volume = self._pos_to_value(self.slider_music_rect, mx)
                try:
                    if getattr(self.game, "audio", None):
                        self.game.audio.set_music_volume(float(self.music_volume))
                except Exception:
                    pass
            handled = True
        # SFX slider
        if self.slider_sfx_rect and (self.dragging_sfx or self.slider_sfx_rect.collidepoint((mx, my))):
            if is_down:
                self.dragging_sfx = True
            if self.dragging_sfx:
                self.sfx_volume = self._pos_to_value(self.slider_sfx_rect, mx)
                try:
                    if getattr(self.game, "audio", None):
                        self.game.audio.set_sfx_volume(float(self.sfx_volume))
                except Exception:
                    pass
            handled = True or handled
        return handled

    @staticmethod
    def _pos_to_value(track_rect: pygame.Rect, mx: int) -> float:
        if not track_rect.width:
            return 0.0
        t = (mx - track_rect.left) / track_rect.width
        return max(0.0, min(1.0, float(t)))
