import sys
import os
import pygame
from settings_store import load_settings
from audio.sound_manager import SoundManager


class Game:
    # Resolución lógica fija del juego (no cambia). Todo el contenido se dibuja aquí.
    WIDTH, HEIGHT = 1920, 1080

    def __init__(self):
        pygame.init()
        # Inicializar mixer con configuración segura
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
        except Exception:
            pass
        try:
            pygame.mixer.init()
        except Exception:
            # Continuar sin audio si falla
            pass
        pygame.display.set_caption("Cheese Gates")

        # Cargar ajustes previos (si existen)
        saved = load_settings() or {}

        # Ventana inicial por defecto: Pantalla Completa
        # Si hay ajustes guardados, aplicarlos; si no, iniciar en FULLSCREEN.
        self.last_windowed_size = (1280, 720)
        try:
            if saved.get("window_mode") == "Ventana":
                os.environ["SDL_VIDEO_CENTERED"] = "1"
                self.screen = pygame.display.set_mode(self.last_windowed_size, pygame.RESIZABLE)
            elif saved.get("window_mode") == "Ventana Sin bordes":
                # Usar resolución guardada si existe; si coincide con el escritorio, ocuparlo
                res = saved.get("resolution", "1920x1080")
                try:
                    w, h = map(int, res.split("x"))
                except Exception:
                    w, h = self.last_windowed_size
                info = pygame.display.Info()
                if w == info.current_w and h == info.current_h:
                    os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
                    self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
                else:
                    os.environ["SDL_VIDEO_CENTERED"] = "1"
                    self.screen = pygame.display.set_mode((w, h), pygame.NOFRAME)
            else:
                # Default FULLSCREEN
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except Exception:
            # Fallback seguro
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # Superficie lógica (canvas) donde se dibuja todo a 1920x1080.
        self.canvas = pygame.Surface((self.WIDTH, self.HEIGHT)).convert_alpha()

        self.clock = pygame.time.Clock()
        self.current_screen = None
        self.render_scale = 1.0
        self.render_offset = (0, 0)
        # Gestor de sonido
        self.audio = SoundManager()

    def change_screen(self, screen):
        # Stop any ongoing audio to avoid overlaps when switching screens
        try:
            if getattr(self, "audio", None):
                self.audio.stop_all(fade_ms_music=250, fade_ms_sfx=120)
        except Exception:
            pass
        self.current_screen = screen
        # Start scene music for the new screen if declared
        try:
            if getattr(self, "audio", None):
                # Prefer explicit music name if provided
                if hasattr(screen, "scene_music_name") and screen.scene_music_name:
                    self.audio.play_music_name(screen.scene_music_name)
                elif hasattr(screen, "scene_key") and screen.scene_key:
                    self.audio.enter_scene(screen.scene_key)
        except Exception:
            pass

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(120) / 1000.0

            # Calcular escala y offset (letterboxing) ANTES de manejar eventos
            window_w, window_h = self.screen.get_size()
            scale = min(window_w / self.WIDTH, window_h / self.HEIGHT)
            scaled_w = max(1, int(self.WIDTH * scale))
            scaled_h = max(1, int(self.HEIGHT * scale))
            x_off = (window_w - scaled_w) // 2
            y_off = (window_h - scaled_h) // 2
            self.render_scale = scale
            self.render_offset = (x_off, y_off)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Atajo global: F11 alterna entre pantalla completa y ventana
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                elif self.current_screen:
                    # Transformar eventos de mouse a coordenadas lógicas del canvas
                    if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                        wx, wy = event.pos
                        lx = (wx - x_off) / scale if scale > 0 else wx
                        ly = (wy - y_off) / scale if scale > 0 else wy
                        if event.type == pygame.MOUSEMOTION:
                            rx, ry = event.rel if hasattr(event, 'rel') else (0, 0)
                            rx_l = rx / scale if scale > 0 else rx
                            ry_l = ry / scale if scale > 0 else ry
                            event = pygame.event.Event(event.type, {
                                'pos': (int(lx), int(ly)),
                                'rel': (int(rx_l), int(ry_l)),
                                'buttons': event.buttons
                            })
                        else:
                            event = pygame.event.Event(event.type, {
                                'pos': (int(lx), int(ly)),
                                'button': event.button
                            })
                    self.current_screen.handle_event(event)

            if self.current_screen:
                self.current_screen.update(dt)
                # Dibujar en el canvas lógico
                self.current_screen.draw()

            # Escalar con letterboxing al tamaño de la ventana para evitar deformaciones
            # Fondo negro (bandas) y blit centrado
            self.screen.fill((0, 0, 0))
            if scaled_w > 0 and scaled_h > 0:
                scaled = pygame.transform.smoothscale(self.canvas, (scaled_w, scaled_h))
                self.screen.blit(scaled, (x_off, y_off))

            pygame.display.set_caption(
                f"Cheese Gates  |  FPS: {int(self.clock.get_fps()):>3}"
            )
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _toggle_fullscreen(self):
        """Alternar entre modo pantalla completa (FULLSCREEN) y ventana (RESIZABLE).
        - Si no estamos en FULLSCREEN: guardar tamaño actual y pasar a FULLSCREEN.
        - Si estamos en FULLSCREEN: volver a ventana con el último tamaño recordado.
        """
        surf = pygame.display.get_surface()
        if not surf:
            return
        flags = surf.get_flags()
        if flags & pygame.FULLSCREEN:
            # Volver a ventana
            os.environ["SDL_VIDEO_CENTERED"] = "1"
            try:
                self.screen = pygame.display.set_mode(self.last_windowed_size, pygame.RESIZABLE)
            except Exception:
                self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        else:
            # Guardar tamaño actual de ventana (en ventana o borderless)
            self.last_windowed_size = self.screen.get_size()
            try:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            except Exception:
                # Fallback a fullscreen a la resolución actual de escritorio
                info = pygame.display.Info()
                self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
