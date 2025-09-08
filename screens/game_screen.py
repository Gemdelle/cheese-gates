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

        # ------ Objetos base ------
        self.setup_stones()
        self.setup_input_zones()   # dinámico según LEVELS

        # ⬇️ Pre-colocar piedra en cada input NOT (solo niveles 3 y 4) — ahora que ya hay stones & input_zones
        self._preplace_not_stones_simple()

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
        self.color_bit_zero = (120, 0, 0)     # rojo oscuro

        # ======= TIMER BAR =======
        cfg_level = LEVELS.get(self.level, {})
        self.time_limit = float(cfg_level.get("time_limit", 60.0))
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

        # ======= TEST ZONE (evalúa al pisarla) =======
        self.test_zone_size = (160, 160)
        self.test_zone_rect = pygame.Rect(0, 0, *self.test_zone_size)
        self.test_zone_rect.center = (self.playable_area.centerx - 80, self.playable_area.top + 80)

        # Fondo con imagen (platform.png)
        self.test_img_raw = pygame.image.load("platform.png").convert_alpha()
        self.test_img = pygame.transform.smoothscale(self.test_img_raw, self.test_zone_size)

        # Animation variables for platform - Faster and more responsive
        self.test_platform_scale = 1.0  # Current scale factor
        self.test_platform_target_scale = 1.0  # Target scale
        self.test_platform_velocity = 0.0  # Animation velocity for bounce
        self.test_platform_spring_strength = 25.0  # Much higher for faster response
        self.test_platform_damping = 0.75  # Lower damping for quicker animation
        self.test_platform_expand_scale = 1.12  # Slightly more expansion for visibility

        # Texto
        self.test_label_font = pygame.font.Font("font/BlackCastleMF.ttf", 28)
        self.test_label_color = (100, 50, 0)

        self._was_in_test_zone = False

        # ======= Resultado cacheado (SOLO tras testear) =======
        try:
            num_inputs_cfg = len(LEVELS[self.level].get("inputs", []))
            if num_inputs_cfg == 0:
                raise KeyError("inputs")
        except Exception:
            num_inputs_cfg = 2
        self.current_bits = [0] * num_inputs_cfg
        self.last_eval_complete = False
        self.has_tested = False
        # =======================================================

        # Máscara de inversión de display para los inputs (solo después de TEST)
        cfg = LEVELS.get(self.level, {})
        mask = cfg.get("display_invert", [])
        if len(mask) < len(self.current_bits):
            mask = list(mask) + [False] * (len(self.current_bits) - len(mask))
        elif len(mask) > len(self.current_bits):
            mask = mask[:len(self.current_bits)]
        self.display_invert = mask

        # Cursor visible en el nivel
        pygame.mouse.set_visible(True)

        # Estado audio de pasos
        self._walking_audio_on = False

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
            cfg_inputs = [
                {"threshold": 1, "invert": False},
                {"threshold": 1, "invert": False},
            ]
        num_inputs = len(cfg_inputs)

        input_spacing = self.input_area.height // (num_inputs + 1 if num_inputs > 0 else 1)

        for i, rule in enumerate(cfg_inputs):
            x = self.input_area.centerx
            y = self.input_area.top + input_spacing * (i + 1)

            required = 0 if rule.get("invert", False) else int(rule.get("threshold", 0))
            input_zone = InputZone((x, y), i + 1, required=required)
            self.input_zones.append(input_zone)

    def setup_circuit(self):
        """Crear el circuito lógico con fondo por nivel."""
        cfg = LEVELS.get(self.level, {})
        bg_path = cfg.get("circuit_bg")
        self.logic_circuit = LogicCircuit(self.circuit_area, circuit_bg_path=bg_path)

        for input_zone in self.input_zones:
            self.logic_circuit.add_input_zone(input_zone)

    def setup_cheese(self):
        cheese_pos = (self.reward_area.centerx, self.reward_area.centery)
        self.cheese = Cheese(cheese_pos)
        self.all_sprites.add(self.cheese)

    def _preplace_not_stones_simple(self):
        """
        Pre-coloca 1 piedra en cada input invertido (NOT) en niveles 3 y 4.
        - Busca índices NOT desde LEVELS[level]["inputs"] (invert=True) y, si no hay,
          usa LEVELS[level]["display_invert"] como fallback.
        - Coloca una piedra cuyo peso sea > requerido (required+1). Si no hay, usa la más pesada libre.
        - En LEVEL 4, el PRIMER NOT recibe específicamente la piedra de peso 12 (si existe)
          para que se vea 12/10.
        """
        if self.level not in (3, 4):
            return
        if not hasattr(self, "stones") or not hasattr(self, "input_zones"):
            return

        cfg = LEVELS.get(self.level, {})
        cfg_inputs = cfg.get("inputs", [])

        # 1) Detectar índices de NOT
        target_idxs = [i for i, rule in enumerate(cfg_inputs) if rule.get("invert", False)]
        if not target_idxs:
            disp = cfg.get("display_invert", [])
            target_idxs = [i for i, inv in enumerate(disp) if inv]

        target_idxs = [i for i in target_idxs if 0 <= i < len(self.input_zones)]
        if not target_idxs:
            return

        # ------- helpers -------
        def free_stones():
            return [s for s in self.stones
                    if not getattr(s, "is_carried", False) and not getattr(s, "is_placed", False)]

        def take_specific_weight(w):
            for s in free_stones():
                if getattr(s, "weight", 0) == w:
                    return s
            return None

        def take_stone_over(min_needed):
            fs = free_stones()
            if not fs:
                return None
            enough = [s for s in fs if getattr(s, "weight", 0) >= min_needed]
            if enough:
                return sorted(enough, key=lambda s: getattr(s, "weight", 9999))[0]
            # fallback: la más pesada disponible
            return sorted(fs, key=lambda s: getattr(s, "weight", 0), reverse=True)[0]

        def center_of_zone(zone):
            if hasattr(zone, "rect") and zone.rect:
                return zone.rect.center
            if hasattr(zone, "pos"):
                try:
                    return (int(zone.pos[0]), int(zone.pos[1]))
                except Exception:
                    pass
            return (self.input_area.centerx, self.input_area.centery)

        def place_in_zone(stone, zone):
            cx, cy = center_of_zone(zone)
            stone.is_carried = False
            stone.is_placed = True
            stone.rect.center = (cx, cy)

            placed = False
            if hasattr(zone, "add_stone") and callable(zone.add_stone):
                try:
                    zone.add_stone(stone); placed = True
                except Exception:
                    pass
            if not placed and hasattr(zone, "place_stone") and callable(zone.place_stone):
                try:
                    zone.place_stone(stone); placed = True
                except Exception:
                    pass
            if not placed and hasattr(zone, "stones"):
                try:
                    zone.stones.append(stone); placed = True
                except Exception:
                    pass
            if not placed and hasattr(zone, "base_weight"):
                try:
                    zone.base_weight = getattr(zone, "base_weight", 0) + getattr(stone, "weight", 1)
                except Exception:
                    pass

        def required_for_zone(i, zone):
            try:
                return int(getattr(zone, "required", cfg_inputs[i].get("threshold", 0)))
            except Exception:
                return int(cfg_inputs[i].get("threshold", 0))

        # 2) Level 4: asegurar 12/10 en el PRIMER NOT
        if self.level == 4:
            first_idx = target_idxs[0]
            zone = self.input_zones[first_idx]
            req = required_for_zone(first_idx, zone)
            min_needed = max(1, req + 1)
            stone = take_specific_weight(12) or take_stone_over(min_needed)
            if stone:
                place_in_zone(stone, zone)
            # procesar el resto luego
            target_idxs = target_idxs[1:]

        # 3) Resto de NOTs (lvl 3 y los restantes de lvl 4)
        for i in target_idxs:
            zone = self.input_zones[i]
            req = required_for_zone(i, zone)
            min_needed = max(1, req + 1)
            stone = take_stone_over(min_needed)
            if stone:
                place_in_zone(stone, zone)


    def constrain_player_movement(self):
        """Enhanced constraint system that works smoothly with velocity-based movement"""
        # Usar el radio de colisión estable del jugador
        r = self.player.collision_radius
        old_pos = self.player.pos.copy()
        
        # Clampear dentro del área jugable con mejor feedback
        clamped_x = max(self.playable_area.left + r,
                       min(self.player.pos.x, self.playable_area.right - r))
        clamped_y = max(self.playable_area.top + r,
                       min(self.player.pos.y, self.playable_area.bottom - r))
        
        # Si hubo clampeo, reducir velocidad suavemente para mantener fluidez
        if clamped_x != self.player.pos.x:
            self.player.velocity.x *= 0.3  # Less aggressive velocity reduction
            self.player.pos.x = clamped_x
            
        if clamped_y != self.player.pos.y:
            self.player.velocity.y *= 0.3  # Less aggressive velocity reduction
            self.player.pos.y = clamped_y
        
        # Verificar colisión con el área del circuito usando el radio estable
        circuit_collision_rect = pygame.Rect(
            self.player.pos.x - r, self.player.pos.y - r, r * 2, r * 2
        )
        
        if circuit_collision_rect.colliderect(self.circuit_area):
            # Calcular distancias a cada borde del circuit_area para empuje inteligente
            dist_left = abs(self.player.pos.x - self.circuit_area.left)
            dist_right = abs(self.player.pos.x - self.circuit_area.right)
            dist_top = abs(self.player.pos.y - self.circuit_area.top)
            dist_bottom = abs(self.player.pos.y - self.circuit_area.bottom)
            
            # Encontrar la distancia mínima para empujar hacia el borde más cercano
            min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
            
            # Empujar y permitir movimiento más fluido
            if min_dist == dist_left:
                self.player.pos.x = self.circuit_area.left - r
                if self.player.velocity.x > 0:  # Only reduce if moving into wall
                    self.player.velocity.x *= 0.2
            elif min_dist == dist_right:
                self.player.pos.x = self.circuit_area.right + r
                if self.player.velocity.x < 0:  # Only reduce if moving into wall
                    self.player.velocity.x *= 0.2
            elif min_dist == dist_top:
                self.player.pos.y = self.circuit_area.top - r
                if self.player.velocity.y > 0:  # Only reduce if moving into wall
                    self.player.velocity.y *= 0.2
            else:  # min_dist == dist_bottom
                self.player.pos.y = self.circuit_area.bottom + r
                if self.player.velocity.y < 0:  # Only reduce if moving into wall
                    self.player.velocity.y *= 0.2

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
            # Entró recién → evaluar y expandir plataforma
            self.test_platform_target_scale = self.test_platform_expand_scale
            
            try:
                is_complete, bits = evaluate_level(self.level, self.input_zones)
            except Exception:
                weights = [z.get_total_weight() for z in self.input_zones]
                bits = [1 if w >= 1 else 0 for w in weights[:2]]
                is_complete = any(bits)
            self.current_bits = bits
            self.last_eval_complete = is_complete
            self.logic_circuit.is_complete = self.last_eval_complete
            self.has_tested = True

            # SFX al entrar a TEST
            if getattr(self.game, "audio", None):
                if is_complete:
                    self.game.audio.play_event_name("test_success", volume=1.0)
                else:
                    self.game.audio.play_event_name("test_fail", volume=1.0)
        
        elif not inside_now and self._was_in_test_zone:
            # Salió → contraer plataforma
            self.test_platform_target_scale = 1.0

        self._was_in_test_zone = inside_now

    def _update_test_platform_animation(self, dt):
        """Fast and responsive spring-based animation for test platform"""
        # More aggressive spring physics for faster response
        scale_diff = self.test_platform_target_scale - self.test_platform_scale
        
        # Animate if there's any meaningful difference (lower threshold)
        if abs(scale_diff) > 0.002:
            spring_force = scale_diff * self.test_platform_spring_strength
            self.test_platform_velocity += spring_force * dt
            self.test_platform_velocity *= self.test_platform_damping
            
            # Update scale with velocity
            self.test_platform_scale += self.test_platform_velocity * dt
            
            # More aggressive snapping for faster settling (higher thresholds)
            if abs(scale_diff) < 0.01 and abs(self.test_platform_velocity) < 0.5:
                self.test_platform_scale = self.test_platform_target_scale
                self.test_platform_velocity = 0.0
        else:
            # Immediate snap for very small differences
            self.test_platform_scale = self.test_platform_target_scale
            self.test_platform_velocity = 0.0
        
        # Safety bounds
        self.test_platform_scale = max(0.9, min(self.test_platform_scale, 1.2))

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
            # Stop walking loop if active
            try:
                if getattr(self.game, "audio", None) and getattr(self, "_walking_audio_on", False):
                    self.game.audio.stop_loop_sfx("walking", fade_ms=120)
                    self._walking_audio_on = False
            except Exception:
                pass
            self.game.change_screen(LoseScreen(self.game, level=self.level, bg_path="lose-bg.png"))
            return

        # Sprites
        self.all_sprites.update(dt, self.playable_area)

        # Animate test platform with spring physics
        self._update_test_platform_animation(dt)

        # Audio de caminar: iniciar/parar loop según movimiento
        try:
            if getattr(self.game, "audio", None):
                moving = bool(getattr(self.player, "is_moving", False))
                if moving and not self._walking_audio_on:
                    self.game.audio.start_loop_sfx("walking", volume=0.5, fade_ms=120)
                    self._walking_audio_on = True
                elif not moving and self._walking_audio_on:
                    self.game.audio.stop_loop_sfx("walking", fade_ms=150)
                    self._walking_audio_on = False
        except Exception:
            pass
        self.constrain_player_movement()

        # Circuit (animación interna)
        self.logic_circuit.update(dt)

        # Abrir/cerrar jaula según el último test
        if hasattr(self.cheese, "set_caged"):
            self.cheese.set_caged(not self.last_eval_complete)

        # Cheese según estado del circuito (para animaciones internas)
        self.cheese.update(dt, self.playable_area, self.logic_circuit.is_complete)

        # Interacciones
        self.handle_stone_interactions()
        self.handle_cheese_collection()

        # Win
        if self.level_complete:
            from .win_screen import WinScreen
            if getattr(self.game, "audio", None):
                self.game.audio.play_event_name("win", volume=0.9)
                # Stop walking loop if active
                try:
                    if getattr(self, "_walking_audio_on", False):
                        self.game.audio.stop_loop_sfx("walking", fade_ms=120)
                        self._walking_audio_on = False
                except Exception:
                    pass

            # 👇 Fondo especial al ganar el nivel 4
            win_bg = "final-bg.png" if self.level == 4 else "win-bg.png"
            self.game.change_screen(
                WinScreen(self.game, level=self.level, bg_path=win_bg, max_level=4)
            )
            return

        # TEST zone
        self._maybe_run_test()

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Input zones
        for input_zone in self.input_zones:
            input_zone.draw(self.screen)

        # Circuit
        self.logic_circuit.draw(self.screen)

        # ====== TEST zone con imagen animada suave (DEBAJO DEL PERSONAJE) ======
        # Calculate smoothly scaled size and position
        original_size = self.test_zone_size
        scaled_size = (
            int(original_size[0] * self.test_platform_scale + 0.5),  # Round for pixel precision
            int(original_size[1] * self.test_platform_scale + 0.5)
        )
        
        # Scale the image (always create fresh to avoid cache issues)
        scaled_test_img = pygame.transform.smoothscale(self.test_img_raw, scaled_size)
        
        # Center the scaled image on the original position
        scaled_rect = scaled_test_img.get_rect(center=self.test_zone_rect.center)
        
        # Draw platform and label
        self.screen.blit(scaled_test_img, scaled_rect.topleft)
        label = self.test_label_font.render("TEST", True, self.test_label_color)
        label_rect = label.get_rect(center=self.test_zone_rect.center)
        self.screen.blit(label, label_rect)
        # ===================================================================

        # Sprites (personaje y piedras) --> ENCIMA del botón TEST
        self.all_sprites.draw(self.screen)
        if self.player.carried_stone:
            self.screen.blit(self.player.carried_stone.image, self.player.carried_stone.rect)

        # Cheese
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

        # ====== Badges (0/1) ======
        self.draw_input_bit_badges()
        self.draw_output_bit_badge()
        # ==========================

        # Overlays
        if self.pause_modal:
            self.pause_modal.draw(self.screen)
        if self.settings_modal:
            self.settings_modal.draw(self.screen)

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
                    self.settings_modal = SettingsModal(self.game, self.game.WIDTH // 2, self.game.HEIGHT // 2)
                elif action == "restart":
                    from .game_screen import GameScreen
                    self.game.change_screen(GameScreen(self.game, level=self.level))
                elif action == "tutorial":
                    from .tutorial_screen import TutorialScreen
                    self.game.change_screen(TutorialScreen(self.game, bg_path="tutorial-bg.png"))
                elif action == "main_menu":
                    from .splash_screen import SplashScreen
                    self.game.change_screen(SplashScreen(self.game))
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.pause_modal = PauseModal(self.game, self.game.WIDTH // 2, self.game.HEIGHT // 2)
                pygame.mouse.set_visible(True)
                # Asegurar que pare el loop de pasos al pausar
                try:
                    if getattr(self.game, "audio", None):
                        self.game.audio.stop_loop_sfx("walking", fade_ms=120)
                        self._walking_audio_on = False
                except Exception:
                    pass
            elif event.key == pygame.K_SPACE:
                self.handle_space_interaction()

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
                    # Reproducir específicamente stone.mp3 al soltar
                    self.game.audio.play_sfx("stone", volume=0.8)
        else:
            for stone in self.stones:
                if not stone.is_carried and self.player.can_pickup_stone(stone):
                    if self.player.pickup_stone(stone):
                        if getattr(self.game, "audio", None):
                            # Play specific stone pickup sound asset (stone.mp3)
                            self.game.audio.play_sfx("stone", volume=0.8)
                    break
