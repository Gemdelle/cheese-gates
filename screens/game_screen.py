import pygame
from .base_screen import Screen
from entities.player import Player
from entities.stone import Stone
from entities.input_zone import InputZone
from entities.logic_circuit import LogicCircuit
from entities.cheese import Cheese
from ui.pause_modal import PauseModal
from ui.settings_modal import SettingsModal
from ui.button import Button
from logic.level_logic import get_stone_weights

# Lógica de niveles (AND/OR/NOT)
from logic.level_logic import LEVELS, evaluate_level


class GameScreen(Screen):
    def __init__(self, game, level=1):
        super().__init__(game)
        self.level = level
        self.pause_modal = None
        self.settings_modal = None
        self.level_complete = False
        self.scene_key = "level"
        # Background
        background_raw = pygame.image.load("level-bg.png").convert()
        if background_raw.get_width() != self.game.WIDTH or background_raw.get_height() != self.game.HEIGHT:
            self.background = pygame.transform.smoothscale(background_raw, (self.game.WIDTH, self.game.HEIGHT))
        else:
            self.background = background_raw

        # Zonas
        self.setup_game_zones()

        # Player
        player_start_x = self.playable_area.centerx
        player_start_y = self.playable_area.centery
        self.player = Player((player_start_x, player_start_y))

        # Sprites
        self.all_sprites = pygame.sprite.Group(self.player)
        self.stone_sprites = pygame.sprite.Group()

        # Objetos
        self.setup_stones()
        self.setup_input_zones()   # dinámico según LEVELS
        self.setup_circuit()
        self.setup_cheese()

        # Añadir piedras a grupos
        for stone in self.stones:
            self.stone_sprites.add(stone)
            self.all_sprites.add(stone)

        # Texto de nivel
        self.font = pygame.font.Font("font/BlackCastleMF.ttf", 50)
        self.level_text = self.font.render(f"Level {level}", True, (255, 255, 255))
        self.level_text_rect = self.level_text.get_rect(topleft=(120, 45))

        # Badges (0/1) para inputs y salida
        self.badge_font = pygame.font.Font("font/BlackCastleMF.ttf", 56)
        self.output_font = pygame.font.Font("font/BlackCastleMF.ttf", 72)
        self.color_bit_one = (255, 246, 170)  # amarillito
        self.color_bit_zero = (120, 0, 0)      # rojo oscuro


        # ======= TIMER BAR =======
        cfg_level = LEVELS.get(self.level, {})
        self.time_limit = float(cfg_level.get("time_limit", 60.0))  # ⬅️ toma del config (fallback 60s)
        self.time_left  = self.time_limit

        self.bar_size       = (580, 50)
        self.bar_padding    = 15
        self.bar_bg_color   = (40, 40, 40)
        self.bar_fill_color = (255, 246, 170)

        self.bar_rect = pygame.Rect(0, 0, *self.bar_size)
        self.bar_rect.center = (self.game.WIDTH // 2, 100)
        self.bar_rect.centerx -= 100

        bar_frame_raw = pygame.image.load("bar.png").convert_alpha()
        self.bar_frame = pygame.transform.smoothscale(bar_frame_raw, self.bar_size)

        self.time_font  = pygame.font.Font("font/BlackCastleMF.ttf", 28)
        self.time_color = (255, 246, 170)
        # =========================


        # ======= Botón Solve (trampa) =======
        self.force_solved = False
        btn_skin = pygame.image.load("button.png").convert_alpha()
        btn_w, btn_h = 160, 60
        margin = 20
        self.solve_button = Button(
            self.game.WIDTH - margin - btn_w // 2,
            margin + btn_h // 2,
            btn_w, btn_h,
            text="Solve",
            image=btn_skin,
            scale=1.0
        )
        self.solve_button.font = pygame.font.Font("font/BlackCastleMF.ttf", 28)
        self.solve_button.text_color = (255, 246, 170)
        self.solve_button.text_surface = self.solve_button.font.render("Solve", True, self.solve_button.text_color)
        self.solve_button.text_rect = self.solve_button.text_surface.get_rect(center=self.solve_button.rect.center)
        # ====================================

        # ======= TEST ZONE (evalúa al pisarla) =======
        self.test_zone_size = (160, 160)
        self.test_zone_rect = pygame.Rect(0, 0, *self.test_zone_size)
        self.test_zone_rect.center = (self.playable_area.centerx -80, self.playable_area.top +80)

        # Fondo con imagen (platform.png) en lugar de color/borde
        self.test_img_raw = pygame.image.load("platform.png").convert_alpha()
        self.test_img = pygame.transform.smoothscale(self.test_img_raw, self.test_zone_size)

        # Texto
        self.test_label_font = pygame.font.Font("font/BlackCastleMF.ttf", 28)
        self.test_label_color = (100, 50, 0)

        self._was_in_test_zone = False
        # Mouse hover over TEST zone state (to play SFX once on enter)
        self._mouse_in_test_zone = False

        # ======= Resultado cacheado (SOLO tras testear) =======
        # Robustez ante niveles sin configurar: fallback a 2 inputs
        try:
            num_inputs_cfg = len(LEVELS[self.level].get("inputs", []))
            if num_inputs_cfg == 0:
                raise KeyError("inputs")
        except Exception:
            num_inputs_cfg = 2
        self.current_bits = [0] * num_inputs_cfg
        self.last_eval_complete = False
        self.has_tested = False           # <-- CLAVE: hasta que no pise TEST, no mostramos nada
        # =======================================================

        # Máscara de inversión de display para los inputs (solo después de TEST)
        cfg = LEVELS.get(self.level, {})
        mask = cfg.get("display_invert", [])
        # Normalizamos al largo de inputs
        if len(mask) < len(self.current_bits):
            mask = list(mask) + [False] * (len(self.current_bits) - len(mask))
        elif len(mask) > len(self.current_bits):
            mask = mask[:len(self.current_bits)]
        self.display_invert = mask

    # Cursor visible en el nivel
    pygame.mouse.set_visible(True)

    def setup_game_zones(self):
        self.playable_area = pygame.Rect(120, 170, 1680, 850)
        self.stones_area   = pygame.Rect(120, 170, 600, 150)
        self.input_area    = pygame.Rect(120, 320, 300, 650)
        self.circuit_area  = pygame.Rect(500, 370, 1100, 600)
        self.reward_area   = pygame.Rect(1600, 520, 200, 200)

    def setup_stones(self):
        self.stones = []
        stone_weights = get_stone_weights(self.level)
        stones_per_row = 6
        num_rows = 2
        stone_spacing_x = self.stones_area.width // stones_per_row
        stone_spacing_y = self.stones_area.height // num_rows
        for i, weight in enumerate(stone_weights):
            row = i // stones_per_row
            col = i % stones_per_row
            x = self.stones_area.left + stone_spacing_x * col + stone_spacing_x // 2
            y = self.stones_area.top + stone_spacing_y * row + stone_spacing_y // 2
            stone = Stone(weight, (x, y))
            self.stones.append(stone)

    def setup_input_zones(self):
        """Crea las zonas de input según la cantidad en LEVELS[level]."""
        self.input_zones = []
        cfg_inputs = LEVELS.get(self.level, {}).get("inputs")
        if not cfg_inputs:
            # Fallback seguro: 2 inputs estándar
            cfg_inputs = [
                {"threshold": 1, "invert": False},
                {"threshold": 1, "invert": False},
            ]
        num_inputs = len(cfg_inputs)

        # Espaciado vertical uniforme dentro del área de inputs
        input_spacing = self.input_area.height // (num_inputs + 1 if num_inputs > 0 else 1)

        for i, rule in enumerate(cfg_inputs):
            x = self.input_area.centerx
            y = self.input_area.top + input_spacing * (i + 1)

            # Si es NOT (invert=True), el requerido para UI es 0; si no, el threshold real
            required = 0 if rule.get("invert", False) else int(rule.get("threshold", 0))

            input_zone = InputZone((x, y), i + 1, required=required)
            self.input_zones.append(input_zone)

    def setup_circuit(self):
        """Crear el circuito lógico con fondo por nivel."""
        cfg = LEVELS.get(self.level, {})
        bg_path = cfg.get("circuit_bg")  # e.g., "level_1.png"

        # Pasamos el rect completo (posición y tamaño) + el fondo
        self.logic_circuit = LogicCircuit(self.circuit_area, circuit_bg_path=bg_path)

        # Conectar las zonas de input al circuito
        for input_zone in self.input_zones:
            self.logic_circuit.add_input_zone(input_zone)

    def setup_cheese(self):
        cheese_pos = (self.reward_area.centerx, self.reward_area.centery)
        self.cheese = Cheese(cheese_pos)
        self.all_sprites.add(self.cheese)

    def constrain_player_movement(self):
        half_w, half_h = self.player.rect.width / 2, self.player.rect.height / 2
        self.player.pos.x = max(self.playable_area.left + half_w,
                                min(self.player.pos.x, self.playable_area.right - half_w))
        self.player.pos.y = max(self.playable_area.top + half_h,
                                min(self.player.pos.y, self.playable_area.bottom - half_h))
        player_rect = pygame.Rect(self.player.pos.x - half_w, self.player.pos.y - half_h,
                                  self.player.rect.width, self.player.rect.height)
        if player_rect.colliderect(self.circuit_area):
            if self.player.pos.x < self.circuit_area.centerx:
                self.player.pos.x = self.circuit_area.left - half_w
            else:
                self.player.pos.x = self.circuit_area.right + half_w

    def handle_stone_interactions(self):
        player_pos = self.player.pos
        if not self.player.carried_stone:
            for stone in self.stones:
                if not stone.is_carried and not stone.is_placed:
                    if self.player.can_pickup_stone(stone):
                        pass
        if self.player.carried_stone:
            for input_zone in self.input_zones:
                if input_zone.contains_point(player_pos) and input_zone.can_accept_stone():
                    pass

    def handle_cheese_collection(self):
        if self.cheese.can_be_collected_by(self.player.pos):
            if self.cheese.collect():
                self.level_complete = True

    def _maybe_run_test(self):
        """Evalúa el nivel SOLO cuando el jugador entra a la zona de test."""
        half_w, half_h = self.player.rect.width / 2, self.player.rect.height / 2
        player_rect = pygame.Rect(self.player.pos.x - half_w, self.player.pos.y - half_h,
                                  self.player.rect.width, self.player.rect.height)
        inside_now = player_rect.colliderect(self.test_zone_rect)

        if inside_now and not self._was_in_test_zone:
            # Entró recién → evaluar
            try:
                is_complete, bits = evaluate_level(self.level, self.input_zones)
            except Exception:
                # Fallback si el nivel no está bien definido
                # Equivalente a OR simple entre primeros dos bits calculados a partir de threshold 1
                weights = [z.get_total_weight() for z in self.input_zones]
                bits = [1 if w >= 1 else 0 for w in weights[:2]]
                is_complete = any(bits)
            self.current_bits = bits
            self.last_eval_complete = is_complete
            self.logic_circuit.is_complete = self.last_eval_complete
            self.has_tested = True   # <-- ahora SÍ podemos mostrar el resultado/bits
            # Reproducir SFX según resultado al ENTRAR el personaje a la plataforma TEST
            if getattr(self.game, "audio", None):
                if is_complete:
                    self.game.audio.play_event_name("test_success", volume=1.0)
                else:
                    self.game.audio.play_event_name("test_fail", volume=1.0)

        self._was_in_test_zone = inside_now

    def update(self, dt):
        if self.pause_modal or self.settings_modal:
            if self.settings_modal:
                self.settings_modal.update(dt)
            elif self.pause_modal:
                self.pause_modal.update(dt)
            return

        # Timer
        if self.time_left > 0.0:
            self.time_left = max(0.0, self.time_left - dt)

        # Lose
        if self.time_left <= 0.0 and not self.level_complete:
            from .lose_screen import LoseScreen
            self.game.change_screen(LoseScreen(self.game, level=self.level, bg_path="lose-bg.png"))
            return

        # Sprites
        self.all_sprites.update(dt, self.playable_area)
        self.constrain_player_movement()

        # Circuit (animación interna)
        self.logic_circuit.update(dt)

        # Solve forzado
        if self.force_solved:
            self.last_eval_complete = True
        self.logic_circuit.is_complete = self.last_eval_complete

        # >>> DESBLOQUEAR JAULA CUANDO EL TEST DA 1 <<<
        # Si tu clase Cheese tiene un setter, lo usamos (opcional, no rompe si no existe).
        if hasattr(self.cheese, "set_caged"):
            self.cheese.set_caged(not self.last_eval_complete)

        # Cheese según estado del circuito (esto ya hace que la jaula se abra si circuit_complete=True)
        self.cheese.update(dt, self.playable_area, self.logic_circuit.is_complete)

        # Interacciones
        self.handle_stone_interactions()
        self.handle_cheese_collection()

        # Walking loop SFX (assets/sounds/walking.*)
        if getattr(self.game, "audio", None):
            if self.player.is_moving:
                self.game.audio.start_loop_sfx("walking", volume=0.45, fade_ms=60)
            else:
                self.game.audio.stop_loop_sfx("walking", fade_ms=120)

        # Win
        if self.level_complete:
            from .win_screen import WinScreen
            if getattr(self.game, "audio", None):
                self.game.audio.play_event_name("win", volume=0.9)
            self.game.change_screen(WinScreen(self.game, level=self.level, bg_path="win-bg.png", max_level=4))
            return

        # Botón Solve (coords lógicas por si usás escalado)
        wx, wy = pygame.mouse.get_pos()
        scale = getattr(self.game, "render_scale", 1.0) or 1.0
        x_off, y_off = getattr(self.game, "render_offset", (0, 0))
        if scale > 0:
            lx = int((wx - x_off) / scale)
            ly = int((wy - y_off) / scale)
        else:
            lx, ly = wx, wy
        try:
            self.solve_button.update(dt, (lx, ly))
        except TypeError:
            self.solve_button.update(dt)

        # TEST zone
        self._maybe_run_test()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        # pygame.draw.rect(self.screen, (0, 0, 255), self.circuit_area, 2)
        # pygame.draw.rect(self.screen, (0, 255, 255), self.playable_area, 2)
        # pygame.draw.rect(self.screen, (255, 255, 0), self.stones_area, 2)
        # pygame.draw.rect(self.screen, (0, 255, 0), self.input_area, 2)
        # pygame.draw.rect(self.screen, (255, 0, 255), self.reward_area, 2)


        # Input zones
        for input_zone in self.input_zones:
            input_zone.draw(self.screen)

        # Circuit
        self.logic_circuit.draw(self.screen)

        # ====== TEST zone con imagen (DEBAJO DEL PERSONAJE) ======
        self.screen.blit(self.test_img, self.test_zone_rect.topleft)
        label = self.test_label_font.render("TEST", True, self.test_label_color)
        label_rect = label.get_rect(center=self.test_zone_rect.center)
        self.screen.blit(label, label_rect)
        # =========================================================

        # Sprites (personaje y piedras) --> se dibujan ENCIMA del botón TEST
        self.all_sprites.draw(self.screen)
        if self.player.carried_stone:
            self.screen.blit(self.player.carried_stone.image, self.player.carried_stone.rect)

        # Cheese FX
        self.cheese.draw(self.screen)


        # ===== Timer bar =====
        inner = self.bar_rect.inflate(-2*self.bar_padding, -2*self.bar_padding)
        pygame.draw.rect(self.screen, self.bar_bg_color, inner, border_radius=10)
        self.screen.blit(self.bar_frame, self.bar_rect.topleft)
        pct = max(0.0, min(1.0, self.time_left / self.time_limit)) if self.time_limit > 0 else 0.0
        fill_w = int(inner.width * pct)
        if fill_w > 0:
            prev_clip = self.screen.get_clip()
            self.screen.set_clip(inner)
            fill_rect = pygame.Rect(inner.left, inner.top, fill_w, inner.height)
            pygame.draw.rect(self.screen, self.bar_fill_color, fill_rect, border_radius=8)
            self.screen.set_clip(prev_clip)
        seconds = int(self.time_left)
        mm, ss = divmod(seconds, 60)
        time_str = f"{mm:02d}:{ss:02d}"
        time_surf = self.time_font.render(time_str, True, self.time_color)
        time_rect = time_surf.get_rect(midleft=(self.bar_rect.right + 12, self.bar_rect.centery))
        self.screen.blit(time_surf, time_rect)
        # =====================

        # Texto “Level X”
        self.screen.blit(self.level_text, self.level_text_rect)

        # Info jugador
        self.draw_player_info()

        # ====== Mostrar resultado SOLO si se testeó ======
        # Badges de cada input (a la izquierda de cada box)
        self.draw_input_bit_badges()

        # Badge del resultado final (sobre la salida del circuito)
        self.draw_output_bit_badge()
        # ==================================================

        # Pause modal
        if self.pause_modal:
            self.pause_modal.draw(self.screen)
        if self.settings_modal:
            self.settings_modal.draw(self.screen)

        # Solve al frente
        self.solve_button.draw(self.screen)

    def draw_player_info(self):
        info_font = pygame.font.Font("font/BlackCastleMF.ttf", 26)
        y_offset = 100
        if self.player.carried_stone:
            carried_text = f"Carrying stone: {self.player.carried_stone.weight}"
            text = info_font.render(carried_text, True, (90, 90, 90))
            self.screen.blit(text, (120, y_offset))
        else:
            instructions = "Press SPACE near a stone to pick it up"
            text = info_font.render(instructions, True, (255, 246, 170))
            self.screen.blit(text, (120, y_offset))

    def _zone_center_y(self, zone):
        # Intenta usar rect; si no existe, usa .pos o .center
        if hasattr(zone, "rect") and zone.rect:
            return zone.rect.centery
        if hasattr(zone, "pos"):
            try:
                return int(zone.pos[1])
            except Exception:
                return int(getattr(zone.pos, "y", self.input_area.centery))
        return self.input_area.centery

    def draw_input_bit_badges(self):
        # Muestra 0/1 a la izquierda de cada InputZone con color por bit.
        # Si el nivel define display_invert[i] == True, invertimos SOLO si ya se presionó TEST.
        x_left = self.input_area.left - 40
        for i, zone in enumerate(self.input_zones):
            raw_bit = self.current_bits[i] if i < len(self.current_bits) else 0
            bit = (1 - raw_bit) if (self.has_tested and i < len(self.display_invert) and self.display_invert[i]) else raw_bit
            color = self.color_bit_one if bit == 1 else self.color_bit_zero
            y = self._zone_center_y(zone)
            surf = self.badge_font.render(str(bit), True, color)
            rect = surf.get_rect(center=(x_left, y))
            self.screen.blit(surf, rect)

    def draw_output_bit_badge(self):
        # 1 si el circuito quedó completo en el último test, si no 0
        out_bit = 1 if self.last_eval_complete else 0
        color = self.color_bit_one if out_bit == 1 else self.color_bit_zero
        cx = self.circuit_area.right - 90
        cy = self.circuit_area.centery
        surf = self.output_font.render(str(out_bit), True, color)
        rect = surf.get_rect(center=(cx, cy))
        self.screen.blit(surf, rect)

    def handle_event(self, event):
        if self.settings_modal:
            action = self.settings_modal.handle_event(event)
            if action == "close":
                self.settings_modal = None
            return

        if self.pause_modal:
            action = self.pause_modal.handle_event(event)
            if action:
                if action == "resume":
                    self.pause_modal = None
                    pygame.mouse.set_visible(True)
                elif action == "settings":
                    # Open in-level settings modal (overlay)
                    self.settings_modal = SettingsModal(self.game, self.game.WIDTH // 2, self.game.HEIGHT // 2)
                elif action == "select_level":
                    from .level_selection_screen import LevelSelectionScreen
                    self.game.change_screen(LevelSelectionScreen(self.game))
                elif action == "tutorial":
                    from .tutorial_screen import TutorialScreen
                    self.game.change_screen(TutorialScreen(self.game, bg_path="tutorial-bg.png"))
                elif action == "exit":
                    pygame.quit()
                    import sys
                    sys.exit()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.pause_modal = PauseModal(self.game, self.game.WIDTH // 2, self.game.HEIGHT // 2)
                pygame.mouse.set_visible(True)
            elif event.key == pygame.K_SPACE:
                self.handle_space_interaction()

    # Ya no usamos hover/cursor para TEST; el disparo es con el personaje al entrar en la plataforma

        # Click “Solve” (fuera del pause)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click en TEST: no hace nada (la evaluación sucede al pisar con el personaje)
            if self.test_zone_rect.collidepoint(event.pos):
                return

            if self.solve_button.rect.collidepoint(event.pos):
                if getattr(self.game, "audio", None):
                    # Play a click and the win stinger before transitioning
                    self.game.audio.play_event_name("ui_click", volume=0.7)
                    self.game.audio.play_event_name("win", volume=0.9)
                self.force_solved = True
                self.level_complete = True
                from .win_screen import WinScreen
                self.game.change_screen(WinScreen(self.game,
                                                  level=self.level,
                                                  bg_path="win-bg.png",
                                                  max_level=4))
                return

    def handle_space_interaction(self):
        if self.player.carried_stone:
            drop_zone = None
            player_pos = self.player.pos
            for input_zone in self.input_zones:
                if input_zone.contains_point(player_pos):
                    drop_zone = input_zone
                    break
            if self.player.drop_stone(drop_zone):
                if getattr(self.game, "audio", None):
                    self.game.audio.play_event_name("drop", volume=0.8)
        else:
            for stone in self.stones:
                if not stone.is_carried and self.player.can_pickup_stone(stone):
                    if self.player.pickup_stone(stone):
                        if getattr(self.game, "audio", None):
                            self.game.audio.play_event_name("pickup", volume=0.8)
                    break
