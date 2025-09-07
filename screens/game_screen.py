import pygame
from .base_screen import Screen
from entities.player import Player
from entities.stone import Stone
from entities.input_zone import InputZone
from entities.logic_circuit import LogicCircuit
from entities.cheese import Cheese
from ui.pause_modal import PauseModal

class GameScreen(Screen):
    def __init__(self, game, level=1):
        super().__init__(game)
        self.level = level
        self.pause_modal = None
        self.level_complete = False

        # Background (scaled if needed)
        background_raw = pygame.image.load("level-bg.png").convert()
        if background_raw.get_width() != game.WIDTH or background_raw.get_height() != game.HEIGHT:
            self.background = pygame.transform.smoothscale(background_raw, (game.WIDTH, game.HEIGHT))
        else:
            self.background = background_raw

        # Define game zones based on the image description
        self.setup_game_zones()

        # Initialize player in the center of the playable area
        player_start_x = self.playable_area.centerx
        player_start_y = self.playable_area.centery
        self.player = Player((player_start_x, player_start_y))

        # Initialize sprite groups first
        self.all_sprites = pygame.sprite.Group(self.player)
        self.stone_sprites = pygame.sprite.Group()

        # Initialize game objects
        self.setup_stones()
        self.setup_input_zones()
        self.setup_circuit()
        self.setup_cheese()

        # Add stones to sprite groups
        for stone in self.stones:
            self.stone_sprites.add(stone)
            self.all_sprites.add(stone)

        # Create level text
        self.font = pygame.font.Font("font/BlackCastleMF.ttf", 36)
        self.level_text = self.font.render(f"Level {level}", True, (255, 255, 255))
        self.level_text_rect = self.level_text.get_rect(topleft=(20, 20))

        # ======= TIMER BAR (centrada, 1 minuto) =======
        self.time_limit = 60.0      # 1 minuto total
        self.time_left  = self.time_limit

        self.bar_size      = (580, 50)     # (ancho, alto) del marco de la barra
        self.bar_padding   = 15            # padding interno para el fill
        self.bar_bg_color  = (40, 40, 40)  # fondo del área vacía (dentro del marco)
        self.bar_fill_color = (255, 246, 170)  # amarillo pastel, a juego con el texto

        # Rect centrado para la barra
        self.bar_rect = pygame.Rect(0, 0, *self.bar_size)
        self.bar_rect.center = (self.game.WIDTH // 2, 100)

        # Imagen del marco
        bar_frame_raw = pygame.image.load("bar.png").convert_alpha()
        self.bar_frame = pygame.transform.smoothscale(bar_frame_raw, self.bar_size)

        # Texto mm:ss a la derecha
        self.time_font  = pygame.font.Font("font/BlackCastleMF.ttf", 28)
        self.time_color = (255, 246, 170)
        # ==============================================

        # Hide cursor for game
        pygame.mouse.set_visible(False)

    def setup_game_zones(self):
        """Definir las zonas del juego basadas en la descripción"""
        # Zona azul donde se puede mover el ratoncito (basada en la imagen)
        self.playable_area = pygame.Rect(120, 150, 1680, 800)

        # Zona superior izquierda para piedras (stones area)
        self.stones_area = pygame.Rect(120, 150, 600, 150)

        # Zona izquierda para inputs (input zones)
        self.input_area = pygame.Rect(120, 300, 300, 700)

        # Zona central para el circuito (no accesible al jugador)
        self.circuit_area = pygame.Rect(600, 300, 600, 400)

        # Zona derecha para el queso (reward area)
        self.reward_area = pygame.Rect(1400, 400, 200, 200)

    def setup_stones(self):
        """Crear las piedras con diferentes pesos"""
        self.stones = []
        stone_weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        # Ahora 6 columnas por fila, 2 filas
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
        """Crear las zonas de input para las piedras"""
        self.input_zones = []

        # Crear 6 zonas de input (basado en la imagen del circuito)
        num_inputs = 6
        input_spacing = 100

        for i in range(num_inputs):
            x = self.input_area.centerx
            y = self.input_area.top + input_spacing * (i + 1)

            input_zone = InputZone((x, y), i + 1)
            self.input_zones.append(input_zone)

    def setup_circuit(self):
        """Crear el circuito lógico"""
        circuit_center = (self.circuit_area.centerx, self.circuit_area.centery)
        self.logic_circuit = LogicCircuit(circuit_center)

        # Conectar las zonas de input al circuito
        for input_zone in self.input_zones:
            self.logic_circuit.add_input_zone(input_zone)

    def setup_cheese(self):
        """Crear el queso (recompensa)"""
        cheese_pos = (self.reward_area.centerx, self.reward_area.centery)
        self.cheese = Cheese(cheese_pos)
        self.all_sprites.add(self.cheese)

    def constrain_player_movement(self):
        """Restringir el movimiento del jugador a la zona azul"""
        # Mantener al jugador dentro del área de juego
        half_w, half_h = self.player.rect.width / 2, self.player.rect.height / 2

        self.player.pos.x = max(self.playable_area.left + half_w,
                                min(self.player.pos.x, self.playable_area.right - half_w))
        self.player.pos.y = max(self.playable_area.top + half_h,
                                min(self.player.pos.y, self.playable_area.bottom - half_h))

        # Evitar que entre en la zona del circuito
        player_rect = pygame.Rect(self.player.pos.x - half_w, self.player.pos.y - half_h,
                                  self.player.rect.width, self.player.rect.height)

        if player_rect.colliderect(self.circuit_area):
            # Empujar al jugador fuera de la zona del circuito
            if self.player.pos.x < self.circuit_area.centerx:
                self.player.pos.x = self.circuit_area.left - half_w
            else:
                self.player.pos.x = self.circuit_area.right + half_w

    def handle_stone_interactions(self):
        """Manejar las interacciones del jugador con las piedras"""
        player_pos = self.player.pos

        # Verificar si el jugador puede recoger piedras
        if not self.player.carried_stone:
            for stone in self.stones:
                if not stone.is_carried and not stone.is_placed:
                    if self.player.can_pickup_stone(stone):
                        # Mostrar indicador visual (opcional)
                        pass

        # Verificar si el jugador puede soltar piedras en zonas de input
        if self.player.carried_stone:
            for input_zone in self.input_zones:
                if input_zone.contains_point(player_pos) and input_zone.can_accept_stone():
                    # Mostrar indicador visual (opcional)
                    pass

    def handle_cheese_collection(self):
        """Manejar la recolección del queso"""
        if self.cheese.can_be_collected_by(self.player.pos):
            if self.cheese.collect():
                self.level_complete = True

    def update(self, dt):
        if self.pause_modal:
            self.pause_modal.update(dt)
        else:
            # === Timer (cuenta regresiva) ===
            if self.time_left > 0.0:
                self.time_left = max(0.0, self.time_left - dt)

            # Actualizar todos los sprites
            self.all_sprites.update(dt, self.playable_area)

            # Restringir movimiento del jugador
            self.constrain_player_movement()

            # Actualizar circuito lógico
            self.logic_circuit.update(dt)

            # Actualizar queso basado en el estado del circuito
            circuit_complete = self.logic_circuit.is_complete
            self.cheese.update(dt, self.playable_area, circuit_complete)

            # Manejar interacciones
            self.handle_stone_interactions()
            self.handle_cheese_collection()

            # Verificar si el nivel está completo
            if self.level_complete:
                # Aquí podrías mostrar un mensaje de victoria o cambiar de pantalla
                pass

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Dibujar zonas de debug (temporal para visualización)
        pygame.draw.rect(self.screen, (0, 255, 255), self.playable_area, 2)
        # pygame.draw.rect(self.screen, (255, 255, 0), self.stones_area, 2)
        # pygame.draw.rect(self.screen, (0, 255, 0), self.input_area, 2)
        pygame.draw.rect(self.screen, (255, 0, 0), self.circuit_area, 2)
        pygame.draw.rect(self.screen, (255, 0, 255), self.reward_area, 2)

        # Dibujar zonas de input
        for input_zone in self.input_zones:
            input_zone.draw(self.screen)

        # Dibujar circuito lógico
        self.logic_circuit.draw(self.screen)

        # Dibujar sprites (piedras, jugador, queso)
        self.all_sprites.draw(self.screen)

        # Si el jugador lleva una piedra, dibujarla por encima de todo (Funciona nice)
        if self.player.carried_stone:
            stone = self.player.carried_stone
            # El rect ya está sincronizado en su update; re-blit para asegurar z-order
            self.screen.blit(stone.image, stone.rect)

        # Dibujar queso con efectos especiales
        self.cheese.draw(self.screen)

        # ======= TIMER BAR (frame debajo, relleno arriba y CLIP interno) =======
        inner = self.bar_rect.inflate(-2*self.bar_padding, -2*self.bar_padding)

        # Fondo del área vacía (dentro del marco)
        pygame.draw.rect(self.screen, self.bar_bg_color, inner, border_radius=10)

        # 1) Dibujo el marco primero (queda debajo)
        self.screen.blit(self.bar_frame, self.bar_rect.topleft)

        # 2) Relleno amarillo por encima, recortado al área interna
        pct = max(0.0, min(1.0, self.time_left / self.time_limit)) if self.time_limit > 0 else 0.0
        fill_w = int(inner.width * pct)
        if fill_w > 0:
            prev_clip = self.screen.get_clip()
            self.screen.set_clip(inner)  # limitar el dibujo al área interna
            fill_rect = pygame.Rect(inner.left, inner.top, fill_w, inner.height)
            pygame.draw.rect(self.screen, self.bar_fill_color, fill_rect, border_radius=8)
            self.screen.set_clip(prev_clip)

        # 3) Texto del tiempo a la derecha, fuera del marco
        seconds = int(self.time_left)
        mm, ss = divmod(seconds, 60)
        time_str = f"{mm:02d}:{ss:02d}"
        time_surf = self.time_font.render(time_str, True, self.time_color)
        time_rect = time_surf.get_rect(midleft=(self.bar_rect.right + 12, self.bar_rect.centery))
        self.screen.blit(time_surf, time_rect)
        # ==============================================

        # Dibujar level number
        self.screen.blit(self.level_text, self.level_text_rect)

        # Dibujar información del jugador
        self.draw_player_info()

        # Draw pause modal if active
        if self.pause_modal:
            self.pause_modal.draw(self.screen)

        # Dibujar mensaje de victoria si el nivel está completo
        if self.level_complete:
            self.draw_victory_message()

    def draw_player_info(self):
        """Dibujar información sobre el estado del jugador"""
        info_font = pygame.font.Font("font/BlackCastleMF.ttf", 24)
        y_offset = 70

        if self.player.carried_stone:
            carried_text = f"Carrying stone: {self.player.carried_stone.weight}"
            text = info_font.render(carried_text, True, (255, 255, 255))
            self.screen.blit(text, (20, y_offset))
        else:
            instructions = "Press SPACE near a stone to pick it up"
            text = info_font.render(instructions, True, (255, 255, 255))
            self.screen.blit(text, (20, y_offset))

    def draw_victory_message(self):
        """Dibujar mensaje de victoria"""
        victory_font = pygame.font.Font(None, 72)
        victory_text = victory_font.render("LEVEL COMPLETE!", True, (0, 255, 0))
        victory_rect = victory_text.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2))

        # Fondo para el texto
        bg_rect = victory_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        self.screen.blit(victory_text, victory_rect)

        # Instrucciones
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render("Press ESC to continue", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2 + 60))
        self.screen.blit(instruction_text, instruction_rect)

    def handle_event(self, event):
        if self.pause_modal:
            action = self.pause_modal.handle_event(event)
            if action:
                if action == "resume":
                    self.pause_modal = None
                    pygame.mouse.set_visible(False)
                elif action == "settings":
                    from .settings_screen import SettingsScreen
                    self.game.change_screen(SettingsScreen(self.game))
                elif action == "select_level":
                    from .level_selection_screen import LevelSelectionScreen
                    self.game.change_screen(LevelSelectionScreen(self.game))
                elif action == "exit":
                    pygame.quit()
                    import sys
                    sys.exit()
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.level_complete:
                        # Ir al siguiente nivel o volver a la selección de nivel
                        from .level_selection_screen import LevelSelectionScreen
                        self.game.change_screen(LevelSelectionScreen(self.game))
                    else:
                        self.pause_modal = PauseModal(self.game.WIDTH // 2, self.game.HEIGHT // 2)
                        pygame.mouse.set_visible(True)
                elif event.key == pygame.K_SPACE:
                    # Manejar recogida/soltar de piedras
                    self.handle_space_interaction()

    def handle_space_interaction(self):
        """Manejar la interacción con SPACE (recoger/soltar piedras)"""
        if self.player.carried_stone:
            # Intentar soltar la piedra
            drop_zone = None
            player_pos = self.player.pos

            # Verificar si está sobre una zona de input
            for input_zone in self.input_zones:
                if input_zone.contains_point(player_pos):
                    drop_zone = input_zone
                    break

            self.player.drop_stone(drop_zone)
        else:
            # Intentar recoger una piedra
            for stone in self.stones:
                if not stone.is_carried and self.player.can_pickup_stone(stone):
                    self.player.pickup_stone(stone)
                    break
