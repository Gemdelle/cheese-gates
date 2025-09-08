import pygame
from settings_store import load_settings, save_settings


class SettingsModal:
    """Small in-level Settings window (overlay) to tweak audio quickly.

    Shows Music/SFX toggles and volume sliders. Persists to settings.json and
    applies immediately through game.audio. Intended to be opened from Pause.
    """

    def __init__(self, game, x: int, y: int):
        self.game = game

        # Container
        self.rect = pygame.Rect(0, 0, 560, 420)
        self.rect.center = (x, y)

        # Fonts/colors
        self.title_font = pygame.font.Font("font/BlackCastleMF.ttf", 40)
        self.font = pygame.font.Font("font/BlackCastleMF.ttf", 28)
        self.color_title = (255, 246, 170)
        self.color_text = (235, 238, 255)
        self.color_panel = (22, 24, 36, 230)
        self.color_border = (80, 90, 140)
        self.color_accent = (140, 150, 240)

        # Load persisted values
        data = load_settings() or {}
        music_opt = data.get("music", "On")
        sfx_opt = data.get("sfx", "On")
        self.music_on = (str(music_opt) == "On")
        self.sfx_on = (str(sfx_opt) == "On")
        try:
            self.music_volume = float(data.get("music_volume", 0.8))
        except Exception:
            self.music_volume = 0.8
        try:
            self.sfx_volume = float(data.get("sfx_volume", 0.8))
        except Exception:
            self.sfx_volume = 0.8

        # Sliders geometry
        self.slider_music_rect = pygame.Rect(0, 0, 320, 10)
        self.slider_sfx_rect = pygame.Rect(0, 0, 320, 10)
        self.drag_music = False
        self.drag_sfx = False

        # Buttons
        self.btn_close_rect = pygame.Rect(0, 0, 160, 52)
        # Window mode cycle button
        self.btn_mode_rect = pygame.Rect(0, 0, 260, 46)
        saved_mode = (load_settings() or {}).get("window_mode", "Pantalla Completa")
        self.window_mode = saved_mode if saved_mode in ("Pantalla Completa", "Ventana Sin bordes", "Ventana") else "Pantalla Completa"

        self._layout()
        self._apply_to_audio()

    def _layout(self):
        # Title position
        self.title_surf = self.title_font.render("Settings", True, self.color_title)
        self.title_rect = self.title_surf.get_rect(midtop=(self.rect.centerx, self.rect.top + 20))

        # Labels
        self.label_music = self.font.render("Music", True, self.color_text)
        self.label_sfx = self.font.render("SFX", True, self.color_text)

        # Toggle boxes
        self.toggle_music_rect = pygame.Rect(self.rect.left + 60, self.rect.top + 110, 32, 32)
        self.toggle_sfx_rect = pygame.Rect(self.rect.left + 60, self.rect.top + 170, 32, 32)

        # Slider tracks
        self.slider_music_rect.topleft = (self.rect.left + 160, self.rect.top + 118)
        self.slider_sfx_rect.topleft = (self.rect.left + 160, self.rect.top + 178)

        # Mode button and Close button
        self.btn_mode_rect.midtop = (self.rect.centerx, self.rect.top + 240)
        self.btn_close_rect.center = (self.rect.centerx, self.rect.bottom - 50)

    def _apply_to_audio(self):
        try:
            if getattr(self.game, "audio", None):
                self.game.audio.set_music_enabled(self.music_on)
                self.game.audio.set_sfx_enabled(self.sfx_on)
                self.game.audio.set_music_volume(max(0.0, min(1.0, float(self.music_volume))))
                self.game.audio.set_sfx_volume(max(0.0, min(1.0, float(self.sfx_volume))))
        except Exception:
            pass

    def _persist(self):
        data = load_settings() or {}
        data.update({
            "music": "On" if self.music_on else "Off",
            "sfx": "On" if self.sfx_on else "Off",
            "music_volume": round(float(self.music_volume), 3),
            "sfx_volume": round(float(self.sfx_volume), 3),
        })
        save_settings(data)

    def update(self, dt):
        # Nothing animated for now
        pass

    def draw(self, screen):
        # Dim background
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # Panel
        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        panel.fill(self.color_panel)
        screen.blit(panel, self.rect.topleft)
        pygame.draw.rect(screen, self.color_border, self.rect, 2, border_radius=12)

        # Title
        screen.blit(self.title_surf, self.title_rect)

        # Music row
        screen.blit(
            self.label_music,
            self.label_music.get_rect(
                midleft=(self.toggle_music_rect.right + 12, self.toggle_music_rect.centery)
            ),
        )
        self._draw_toggle(screen, self.toggle_music_rect, self.music_on)
        self._draw_slider(screen, self.slider_music_rect, self.music_volume)

        # SFX row
        screen.blit(
            self.label_sfx,
            self.label_sfx.get_rect(
                midleft=(self.toggle_sfx_rect.right + 12, self.toggle_sfx_rect.centery)
            ),
        )
        self._draw_toggle(screen, self.toggle_sfx_rect, self.sfx_on)
        self._draw_slider(screen, self.slider_sfx_rect, self.sfx_volume)

        # Window mode button
        pygame.draw.rect(screen, self.color_accent, self.btn_mode_rect, 2, border_radius=8)
        mode_txt = self.font.render(self.window_mode, True, self.color_text)
        mode_rect = mode_txt.get_rect(center=self.btn_mode_rect.center)
        screen.blit(mode_txt, mode_rect)

        # Close button
        pygame.draw.rect(screen, self.color_accent, self.btn_close_rect, 2, border_radius=8)
        btn_txt = self.font.render("Close", True, self.color_text)
        btn_rect = btn_txt.get_rect(center=self.btn_close_rect.center)
        screen.blit(btn_txt, btn_rect)

    def _draw_toggle(self, screen, rect: pygame.Rect, is_on: bool):
        base = (50, 55, 90)
        oncol = (120, 200, 120)
        offcol = (160, 80, 80)
        pygame.draw.rect(screen, base, rect, border_radius=6)
        inner = rect.inflate(-6, -6)
        pygame.draw.rect(screen, oncol if is_on else offcol, inner, border_radius=6)

    def _draw_slider(self, screen, track_rect: pygame.Rect, value: float):
        pygame.draw.rect(screen, (40, 44, 66), track_rect, border_radius=6)
        v = max(0.0, min(1.0, float(value)))
        fill_w = int(track_rect.width * v)
        fill_rect = pygame.Rect(track_rect.left, track_rect.top, fill_w, track_rect.height)
        pygame.draw.rect(screen, self.color_accent, fill_rect, border_radius=6)
        knob_x = track_rect.left + fill_w
        pygame.draw.circle(screen, (220, 225, 255), (knob_x, track_rect.centery), 7)

    def _slider_value_from_x(self, track_rect: pygame.Rect, mx: int) -> float:
        if track_rect.width <= 0:
            return 0.0
        return max(0.0, min(1.0, (mx - track_rect.left) / track_rect.width))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            return "close"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.toggle_music_rect.collidepoint((mx, my)):
                self.music_on = not self.music_on
                self._apply_to_audio()
                self._persist()
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click")
                return None
            if self.toggle_sfx_rect.collidepoint((mx, my)):
                self.sfx_on = not self.sfx_on
                self._apply_to_audio()
                self._persist()
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click")
                return None
            if self.slider_music_rect.collidepoint((mx, my)):
                self.drag_music = True
                self.music_volume = self._slider_value_from_x(self.slider_music_rect, mx)
                self._apply_to_audio()
                self._persist()
                return None
            if self.slider_sfx_rect.collidepoint((mx, my)):
                self.drag_sfx = True
                self.sfx_volume = self._slider_value_from_x(self.slider_sfx_rect, mx)
                self._apply_to_audio()
                self._persist()
                return None
            if self.btn_mode_rect.collidepoint((mx, my)):
                self._cycle_window_mode()
                return None
            if self.btn_close_rect.collidepoint((mx, my)):
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("ui_click")
                return "close"

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drag_music = False
            self.drag_sfx = False

        if event.type == pygame.MOUSEMOTION:
            if self.drag_music:
                mx, _ = event.pos
                self.music_volume = self._slider_value_from_x(self.slider_music_rect, mx)
                self._apply_to_audio()
                self._persist()
            elif self.drag_sfx:
                mx, _ = event.pos
                self.sfx_volume = self._slider_value_from_x(self.slider_sfx_rect, mx)
                self._apply_to_audio()
                self._persist()

        return None

    def _cycle_window_mode(self):
        modes = ["Pantalla Completa", "Ventana Sin bordes", "Ventana"]
        try:
            idx = modes.index(self.window_mode)
        except ValueError:
            idx = 0
        self.window_mode = modes[(idx + 1) % len(modes)]
        # Persist
        data = load_settings() or {}
        data["window_mode"] = self.window_mode
        save_settings(data)
        # Apply minimal switch using Game._toggle_fullscreen when toggling to/from fullscreen
        try:
            if self.window_mode == "Pantalla Completa":
                # Switch to fullscreen
                if not (pygame.display.get_surface().get_flags() & pygame.FULLSCREEN):
                    self.game._toggle_fullscreen()
            else:
                # Ensure we exit fullscreen when in a windowed mode
                if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                    self.game._toggle_fullscreen()
        except Exception:
            pass
