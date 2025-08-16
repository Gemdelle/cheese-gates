import pygame

class LogicCircuit:
    """
    Maneja la lógica del circuito basado en los inputs y determina si está completo.
    """
    def __init__(self, pos, circuit_image_path=None):
        self.pos = pygame.Vector2(pos)
        self.input_zones = []  # Lista de zonas de input
        self.is_complete = False
        
        # Configuración del circuito para el nivel actual
        # Basado en la imagen, parece que necesitamos inputs específicos para completar el circuito
        self.required_pattern = [1, 4, 5, 2, 3, 1, 5, 6, 2, 3, 1, 4]  # Patrón de ejemplo
        
        # Crear imagen temporal del circuito con cubos de colores
        self.circuit_image = self.create_circuit_placeholder()
        self.rect = self.circuit_image.get_rect(center=pos)
            
    def create_circuit_placeholder(self):
        """Crear una réplica del circuito lógico de la imagen"""
        surface = pygame.Surface((600, 400), pygame.SRCALPHA)
        
        # Fondo del circuito
        surface.fill((245, 245, 245, 255))  # Fondo blanco como en la imagen
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, 600, 400), 2)
        
        # Definir posiciones y dimensiones
        input_x = 20
        line_spacing = 35
        gate_width = 50
        gate_height = 30
        
        # Posiciones de las líneas de entrada (6 inputs)
        input_lines = [
            50,   # Input 1
            85,   # Input 2  
            120,  # Input 3
            155,  # Input 4
            190,  # Input 5
            225,  # Input 6
            270,  # Input 7
            305,  # Input 8
            340   # Input 9
        ]
        
        # Dibujar líneas de entrada desde la izquierda
        line_color = (0, 0, 0)
        for i, y in enumerate(input_lines):
            pygame.draw.line(surface, line_color, (input_x, y), (input_x + 80, y), 2)
            # Etiquetas de entrada
            font = pygame.font.Font(None, 20)
            label = font.render(f"I{i+1}", True, (0, 0, 0))
            surface.blit(label, (5, y - 8))
        
        # Primera columna de NOT gates (inversores)
        not_x = 100
        not_positions = [50, 85, 155, 270]
        for y in not_positions:
            self.draw_not_gate(surface, not_x, y)
            
        # Primera columna de compuertas AND
        and1_x = 180
        and1_y = 65
        self.draw_and_gate(surface, and1_x, and1_y)
        
        # Compuerta OR en la parte superior
        or1_x = 180
        or1_y = 200
        self.draw_or_gate(surface, or1_x, or1_y)
        
        # Segunda columna de compuertas AND
        and2_x = 280
        and2_y = 85
        self.draw_and_gate(surface, and2_x, and2_y)
        
        and3_x = 280
        and3_y = 130
        self.draw_and_gate(surface, and3_x, and3_y)
        
        # Compuerta OR en la parte inferior
        or2_x = 280
        or2_y = 290
        self.draw_or_gate(surface, or2_x, or2_y)
        
        # Tercera columna - compuerta AND
        and4_x = 380
        and4_y = 108
        self.draw_and_gate(surface, and4_x, and4_y)
        
        and5_x = 380
        and5_y = 270
        self.draw_and_gate(surface, and5_x, and5_y)
        
        # Cuarta columna - compuerta AND final
        and_final_x = 480
        and_final_y = 160
        self.draw_and_gate(surface, and_final_x, and_final_y)
        
        # Compuerta OR final
        or_final_x = 480
        or_final_y = 240
        self.draw_or_gate(surface, or_final_x, or_final_y)
        
        # Línea de salida
        pygame.draw.line(surface, line_color, (530, 250), (580, 250), 2)
        font = pygame.font.Font(None, 20)
        output_label = font.render("OUT", True, (0, 0, 0))
        surface.blit(output_label, (545, 260))
        
        # Dibujar todas las conexiones
        self.draw_circuit_connections(surface)
        
        return surface
    
    def draw_not_gate(self, surface, x, y):
        """Dibujar una compuerta NOT (inversor)"""
        # Triángulo del inversor
        points = [(x, y-10), (x, y+10), (x+25, y)]
        pygame.draw.polygon(surface, (255, 255, 255), points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 2)
        
        # Círculo pequeño de negación
        pygame.draw.circle(surface, (255, 255, 255), (x+25, y), 3)
        pygame.draw.circle(surface, (0, 0, 0), (x+25, y), 3, 2)
        
        # Línea de salida
        pygame.draw.line(surface, (0, 0, 0), (x+28, y), (x+40, y), 2)
    
    def draw_and_gate(self, surface, x, y):
        """Dibujar una compuerta AND"""
        # Forma de la compuerta AND
        rect_part = pygame.Rect(x, y-15, 25, 30)
        pygame.draw.rect(surface, (255, 255, 255), rect_part)
        pygame.draw.rect(surface, (0, 0, 0), rect_part, 2)
        
        # Parte semicircular
        pygame.draw.arc(surface, (0, 0, 0), (x+20, y-15, 30, 30), -1.57, 1.57, 2)
        pygame.draw.arc(surface, (255, 255, 255), (x+21, y-14, 28, 28), -1.57, 1.57, 0)
        
        # Texto AND
        font = pygame.font.Font(None, 16)
        text = font.render("AND", True, (255, 0, 0))
        surface.blit(text, (x+5, y-6))
        
        # Líneas de entrada
        pygame.draw.line(surface, (0, 0, 0), (x-15, y-8), (x, y-8), 2)
        pygame.draw.line(surface, (0, 0, 0), (x-15, y+8), (x, y+8), 2)
        
        # Línea de salida
        pygame.draw.line(surface, (0, 0, 0), (x+35, y), (x+50, y), 2)
    
    def draw_or_gate(self, surface, x, y):
        """Dibujar una compuerta OR"""
        # Forma de la compuerta OR (simplificada como forma curva)
        points = [
            (x, y-15), (x+10, y-15), (x+25, y-10),
            (x+35, y), (x+25, y+10), (x+10, y+15), (x, y+15),
            (x+8, y)
        ]
        pygame.draw.polygon(surface, (255, 255, 255), points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 2)
        
        # Texto OR
        font = pygame.font.Font(None, 16)
        text = font.render("OR", True, (255, 0, 0))
        surface.blit(text, (x+8, y-6))
        
        # Líneas de entrada
        pygame.draw.line(surface, (0, 0, 0), (x-15, y-8), (x+3, y-8), 2)
        pygame.draw.line(surface, (0, 0, 0), (x-15, y+8), (x+3, y+8), 2)
        
        # Línea de salida
        pygame.draw.line(surface, (0, 0, 0), (x+35, y), (x+50, y), 2)
    
    def draw_circuit_connections(self, surface):
        """Dibujar todas las conexiones del circuito"""
        line_color = (0, 0, 0)
        
        # Conexiones desde inputs hasta NOT gates
        pygame.draw.line(surface, line_color, (100, 50), (140, 50), 2)
        pygame.draw.line(surface, line_color, (100, 85), (140, 85), 2)
        pygame.draw.line(surface, line_color, (100, 155), (140, 155), 2)
        pygame.draw.line(surface, line_color, (100, 270), (140, 270), 2)
        
        # Conexiones a primera AND gate
        pygame.draw.line(surface, line_color, (140, 50), (165, 57), 2)
        pygame.draw.line(surface, line_color, (140, 85), (165, 73), 2)
        
        # Conexiones complejas - líneas principales horizontales
        pygame.draw.line(surface, line_color, (100, 120), (400, 120), 2)
        pygame.draw.line(surface, line_color, (100, 190), (250, 190), 2)
        pygame.draw.line(surface, line_color, (100, 225), (250, 225), 2)
        pygame.draw.line(surface, line_color, (100, 305), (400, 305), 2)
        pygame.draw.line(surface, line_color, (100, 340), (250, 340), 2)
        
        # Conexiones verticales para routing
        pygame.draw.line(surface, line_color, (250, 190), (250, 225), 2)
        pygame.draw.line(surface, line_color, (400, 120), (400, 305), 2)
        
        # Conexiones a las compuertas finales
        pygame.draw.line(surface, line_color, (430, 108), (465, 152), 2)
        pygame.draw.line(surface, line_color, (430, 270), (465, 168), 2)
        
        # Conexión final a OR
        pygame.draw.line(surface, line_color, (530, 160), (550, 160), 2)
        pygame.draw.line(surface, line_color, (550, 160), (550, 232), 2)
        pygame.draw.line(surface, line_color, (550, 232), (530, 232), 2)
        
    def add_input_zone(self, input_zone):
        """Agregar una zona de input al circuito"""
        self.input_zones.append(input_zone)
        
    def evaluate_circuit(self):
        """
        Evaluar el circuito basado en los valores de los inputs según el diagrama.
        Implementa la lógica real del circuito de la imagen.
        """
        if len(self.input_zones) < 6:
            return False
            
        # Obtener los valores binarios de cada input (necesitamos al menos 6)
        inputs = []
        for i in range(min(6, len(self.input_zones))):
            inputs.append(self.input_zones[i].get_binary_value())
        
        # Asegurar que tenemos 6 inputs
        while len(inputs) < 6:
            inputs.append(0)
            
        # Implementar la lógica del circuito según el diagrama
        # Aplicar inversores (NOT gates) a algunos inputs
        not_i1 = 1 - inputs[0]  # NOT de input 1
        not_i2 = 1 - inputs[1]  # NOT de input 2
        not_i4 = 1 - inputs[3]  # NOT de input 4
        
        # Primera fila de compuertas
        and1 = not_i1 & not_i2  # Primera AND con NOT I1 y NOT I2
        
        # Segunda fila 
        or1 = inputs[2] | inputs[3]  # OR con I3 e I4
        and2 = and1 & inputs[2]     # AND con resultado de and1 e I3
        and3 = or1 & not_i4         # AND con resultado de or1 y NOT I4
        
        # Tercera fila
        and4 = and2 & and3          # AND con resultados de and2 y and3
        
        # Cuarta fila (parte inferior)
        or2 = inputs[4] | inputs[5]  # OR con I5 e I6
        and5 = or2 & inputs[4]       # AND con resultado de or2 e I5
        
        # Compuertas finales
        and_final = and4 & inputs[1]  # AND final con and4 e I2
        or_final = and_final | and5   # OR final
        
        # El circuito está completo si la salida es 1
        self.is_complete = bool(or_final)
        return self.is_complete
        
    def get_output_value(self):
        """Obtener el valor de salida del circuito"""
        self.evaluate_circuit()
        return 1 if self.is_complete else 0
        
    def draw(self, screen):
        """Dibujar el circuito lógico"""
        # Dibujar la imagen del circuito
        screen.blit(self.circuit_image, self.rect)
        
        # Dibujar indicador de estado
        status_color = (0, 255, 0) if self.is_complete else (255, 0, 0)
        status_text = "COMPLETE" if self.is_complete else "INCOMPLETE"
        
        font = pygame.font.Font(None, 36)
        text = font.render(status_text, True, status_color)
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.bottom + 30))
        screen.blit(text, text_rect)
        
        # Dibujar información de debug (peso total)
        debug_font = pygame.font.Font(None, 24)
        total_weight = sum(zone.get_total_weight() for zone in self.input_zones)
        debug_text = debug_font.render(f"Total Weight: {total_weight}", True, (255, 255, 255))
        debug_rect = debug_text.get_rect(center=(self.rect.centerx, self.rect.bottom + 60))
        screen.blit(debug_text, debug_rect)
        
        # Dibujar valores de input
        input_values = [zone.get_binary_value() for zone in self.input_zones]
        input_text = debug_font.render(f"Inputs: {input_values}", True, (255, 255, 255))
        input_rect = input_text.get_rect(center=(self.rect.centerx, self.rect.bottom + 85))
        screen.blit(input_text, input_rect)
        
    def update(self, dt):
        """Actualizar el estado del circuito"""
        self.evaluate_circuit()
