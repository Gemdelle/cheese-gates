# level_logic.py
# -----------------------------------------------------------------------------
# Configuración y evaluación de niveles / lógica (AND, OR, NOT).
# Usá este archivo para definir cuántas piedras requiere cada input y
# cómo se conectan las compuertas por nivel.
# -----------------------------------------------------------------------------

from typing import Any, Dict, List, Tuple

# -----------------------------------------------------------------------------
# ESTRUCTURA DE CONFIGURACIÓN
# -----------------------------------------------------------------------------
# - "inputs": lista por nivel, un dict por input:
#       { "threshold": int, "invert": bool }
#     * Si invert=True → es un NOT: ese input vale 1 SOLO si el total de piedras es 0.
#       (En ese caso se ignora threshold).
#     * Si invert=False → vale 1 si total_piedras >= threshold.
#
# - "circuit": árbol de compuertas con la forma:
#       {"op": "AND"|"OR"|"NOT", "args": [subnodos...]}
#     Donde un "subnodo" puede ser:
#       - un índice de input (0, 1, 2, ...) para referenciar el bit de ese input
#       - otro diccionario compuesto {"op": ..., "args": [...]}
#
# EJEMPLOS:
#   {"op": "OR",  "args": [0, 1]}                         # input0 OR input1
#   {"op": "AND", "args": [0, 1]}                         # input0 AND input1
#   {"op": "AND", "args": [ {"op":"NOT","args":[0]}, 1 ]} # (NOT input0) AND input1
#
# NOTA: Ajustá "inputs" y "circuit" por nivel a tu gusto; acá hay placeholders.

LEVELS: Dict[int, Dict[str, Any]] = {
    1: {
        # Cantidad de inputs que tenga tu circuito en el nivel 1 (editalo a gusto)
        "inputs": [
            {"threshold": 6, "invert": False},
            {"threshold": 3, "invert": False},
        ],
        # Lógica del nivel 1: con OR alcanza con que 1 cumpla.
        "circuit": {"op": "OR", "args": [0, 1]},
    },
    2: {

    },
    3: {

    },
    4: {

    },
}

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
    # Si el nodo es un índice de input (ej. 0, 1, 2...)
    if isinstance(node, int):
        return bits[node]

    # Si es un dict con {op, args}
    if isinstance(node, dict):
        op = str(node.get("op", "")).upper()
        args = node.get("args", [])

        if op == "NOT":
            # NOT es unario
            val = _eval_node(args[0], bits)
            return 1 - val

        # Para AND/OR evaluamos todos los hijos primero
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
    devuelve la lista de bits (0/1) aplicando threshold o NOT según el config del nivel.
    """
    cfg = LEVELS[level_num]
    rules = cfg["inputs"]
    if len(weights) < len(rules):
        # Podés preferir lanzar error; acá simplemente completamos con ceros.
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
    return is_complete, bits
