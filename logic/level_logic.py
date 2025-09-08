# level_logic.py
# -----------------------------------------------------------------------------
# Configuración y evaluación de niveles / lógica (AND, OR, NOT).
# Además, define qué piedras (pesos) spawnean por nivel.
# -----------------------------------------------------------------------------

from typing import Any, Dict, List, Tuple

# Si un nivel no especifica "stones", se usa este default
DEFAULT_STONES: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# -----------------------------------------------------------------------------
# ESTRUCTURA DE CONFIGURACIÓN
# -----------------------------------------------------------------------------
# - "inputs": lista por nivel, un dict por input:
#       { "threshold": int, "invert": bool }
#     * invert=True → NOT: vale 1 SOLO si total_piedras == 0 (ignora threshold).
#     * invert=False → vale 1 si total_piedras >= threshold.
#
# - "circuit": árbol de compuertas:
#       {"op": "AND"|"OR"|"NOT", "args": [subnodos...]}
#     subnodo: índice de input (0,1,2,...) o diccionario anidado {"op":...}
#
# - "circuit_bg": ruta de la imagen de fondo del circuito para ese nivel.
#
# - "stones": lista de pesos de piedras que spawnean en el nivel
#     (por ejemplo [1,2,3,4,5,6,7,8,9,10,11,12]).
# -----------------------------------------------------------------------------

LEVELS: Dict[int, Dict[str, Any]] = {
    1: {
        "inputs": [
            {"threshold": 6, "invert": False},
            {"threshold": 3, "invert": False},
        ],
        "circuit": {"op": "OR", "args": [0, 1]},
        "circuit_bg": "circuit-1.png",
        "stones": [1, 4, 2, 1],  # editá a gusto
        "time_limit": 60.0
    },
    2: {
        # 4 inputs con los thresholds de la imagen: /3, /4, /6, /8
        "inputs": [
            {"threshold": 3, "invert": False},  # I0
            {"threshold": 4, "invert": False},  # I1
            {"threshold": 6, "invert": False},  # I2
            {"threshold": 8, "invert": False},  # I3
        ],
        # (I0 OR I1) AND (I2 OR I3)
        "circuit": {
            "op": "AND",
            "args": [
                {"op": "OR", "args": [0, 1]},
                {"op": "OR", "args": [2, 3]}
            ]
        },
        # Fondo del circuito para este nivel
        "circuit_bg": "circuit-2.png",

        # Piedras disponibles según la tira de la imagen (① ② ① ② ④ ①)
        # Ajustá si querés más/menos unidades.
        "stones": [1, 2, 1, 2, 4, 1],

        # Tiempo para resolver (va a la barra del GameScreen)
        "time_limit": 60.0
    },
    3: {
        # Umbrales según la imagen: /5, /2 (NOT), /3 (NOT), /6
        "inputs": [
            {"threshold": 5, "invert": False},  # I0
            {"threshold": 2, "invert": True},   # I1  ← NOT (vale 1 sólo si hay 0 piedras)
            {"threshold": 3, "invert": True},   # I2  ← NOT
            {"threshold": 6, "invert": False},  # I3
        ],
        # Estructura: (I0 OR I1) AND (I2 AND I3)
        # OJO: como los NOT ya están modelados con invert=True arriba,
        # acá NO vuelvas a poner NOT en el árbol (evitás doble negación).
        "circuit": {
            "op": "AND",
            "args": [
                {"op": "OR",  "args": [0, 1]},
                {"op": "AND", "args": [2, 3]}
            ]
        },

        # Fondo del circuito para este nivel
        "circuit_bg": "circuit-3.png",

        # Piedras disponibles (① ② ① ① ② ④)
        "stones": [1, 2, 1, 1, 2, 4],

        # Tiempo para resolver (barra)
        "time_limit": 60.0
    },
    4: {
        "inputs": [
            {"threshold": 10, "invert": False},  # I0 (se niega en el diagrama)
            {"threshold": 8,  "invert": False},  # I1
            {"threshold": 12, "invert": False},  # I2
            {"threshold": 2,  "invert": False},  # I3 (se niega en el diagrama)
            {"threshold": 3,  "invert": False},  # I4
        ],
        "circuit": {
            "op": "AND",
            "args": [
                {"op": "AND", "args": [ {"op":"NOT","args":[0]}, 1 ]},
                {"op": "AND", "args": [ {"op":"NOT","args":[3]}, 2 ]},
                {"op": "OR",  "args": [ 4, {"op":"NOT","args":[0]} ]},
            ]
        },
        "display_invert": [True, False, False, True, False],  # ⬅️ mostrar invertidos al test
        "circuit_bg": "circuit-4.png",
        "stones": [1,7,1,9,2,2,12,5,7],
        "time_limit": 60.0,
    },
}

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def get_stone_weights(level_num: int) -> List[int]:
    """Devuelve la lista de pesos de piedras que spawnean en el nivel."""
    return list(LEVELS.get(level_num, {}).get("stones", DEFAULT_STONES))

# -----------------------------------------------------------------------------
# EVALUACIÓN
# -----------------------------------------------------------------------------

def _bit_from_weight(total_weight: int, rule: Dict[str, Any]) -> int:
    """Convierte el peso total de un input a bit (0/1) según la regla."""
    invert = bool(rule.get("invert", False))
    if invert:
        # NOT: cuenta 1 SOLO si hay 0 piedras
        return 1 if total_weight == 0 else 0
    # Normal: 1 si total_piedras >= threshold
    threshold = int(rule.get("threshold", 0))
    return 1 if total_weight >= threshold else 0


def _eval_node(node: Any, bits: List[int]) -> int:
    """Evalúa recursivamente el árbol de la compuerta, devolviendo 0/1."""
    if isinstance(node, int):
        return bits[node]

    if isinstance(node, dict):
        op = str(node.get("op", "")).upper()
        args = node.get("args", [])

        if op == "NOT":
            val = _eval_node(args[0], bits)
            return 1 - val

        vals = [_eval_node(arg, bits) for arg in args]

        if op == "AND":
            return 1 if all(vals) else 0
        if op == "OR":
            return 1 if any(vals) else 0

        raise ValueError(f"Operación desconocida: {op}")

    raise TypeError(f"Nodo inválido en circuito: {node!r}")


def compute_input_bits(level_num: int, weights: List[int]) -> List[int]:
    """
    A partir de los pesos totales por input (sumando piedras en cada caja),
    devuelve los bits (0/1) aplicando threshold o NOT según el config del nivel.
    """
    cfg = LEVELS[level_num]
    rules = cfg["inputs"]
    if len(weights) < len(rules):
        weights = list(weights) + [0] * (len(rules) - len(weights))
    return [_bit_from_weight(w, rules[i]) for i, w in enumerate(weights)]


def evaluate_level(level_num: int, input_zones: List[Any]) -> Tuple[bool, List[int]]:
    """
    Evalúa el circuito del nivel con los pesos actuales de cada InputZone.
    Devuelve:
      - is_complete (bool): True si la expresión del circuito da 1
      - bits (List[int]):   los bits calculados por input (para mostrar, ej. "1 0 1 ...")
    """
    cfg = LEVELS[level_num]
    # 1) Obtener pesos actuales de cada zona de input
    weights = [z.get_total_weight() for z in input_zones]

    # 2) Convertir a bits según reglas del nivel
    bits = compute_input_bits(level_num, weights)

    # 3) Evaluar el árbol de compuertas
    is_complete = bool(_eval_node(cfg["circuit"], bits))

    print()
    return is_complete, bits
