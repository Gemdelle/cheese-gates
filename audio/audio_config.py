
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional


class SfxEvent(Enum):
    """Eventos de efectos de sonido semánticos.

    Agrega o quita los que necesites; mantén nombres claros y consistentes.
    """
    UI_HOVER = auto()
    UI_CLICK = auto()
    PICKUP = auto()
    DROP = auto()
    WIN = auto()
    LOSE = auto()
    # Ejemplos extra posibles:
    # STEP = auto()
    # IDLE = auto()


class MusicTrack(Enum):
    """Pistas de música por contexto/escena."""
    MENU = auto()
    LEVEL_SELECT = auto()
    LEVEL = auto()


@dataclass(frozen=True)
class SoundDef:
    """Definición de un SFX con variantes y valores por defecto.

    Atributos:
        names: Lista de nombres base (sin extensión). Si hay más de uno,
               se elige aleatoriamente al reproducir.
        volume: Volumen por defecto (0..1) para este SFX.
        loop: Si debe loopear por defecto.
        cooldown_ms: Tiempo mínimo entre reproducciones del mismo evento (anti-spam).
    """
    names: List[str]
    volume: float = 1.0
    loop: bool = False
    cooldown_ms: int = 0


@dataclass(frozen=True)
class MusicDef:
    """Definición de música por pista.

    Atributos:
        name: Nombre base (sin extensión) en assets/music.
        volume: Volumen por defecto (0..1) para esta pista.
        loop: Si debe loopear por defecto.
        fade_ms: Fade al iniciar (y al cambiar desde otra pista), en ms.
    """
    name: str
    volume: float = 1.0
    loop: bool = True
    fade_ms: int = 600


# =====================
# Mapeos por defecto
# =====================

# SFX: asigna cada evento a uno o varios archivos.
SOUND_MAP: Dict[SfxEvent, SoundDef] = {
    SfxEvent.UI_HOVER: SoundDef(["ui_hover"], volume=0.6, cooldown_ms=40),
    SfxEvent.UI_CLICK: SoundDef(["ui_click"], volume=0.7, cooldown_ms=60),
    SfxEvent.PICKUP:   SoundDef(["pickup"], volume=0.85, cooldown_ms=80),
    SfxEvent.DROP:     SoundDef(["drop"], volume=0.85, cooldown_ms=80),
    SfxEvent.WIN:      SoundDef(["win"], volume=0.9),
    SfxEvent.LOSE:     SoundDef(["lose"], volume=0.9),
    # Ejemplo con variantes aleatorias:
    # SfxEvent.STEP: SoundDef(["step1", "step2", "step3", "step4"], volume=0.5, cooldown_ms=120),
}


# Música: asigna cada pista a un archivo.
MUSIC_MAP: Dict[MusicTrack, MusicDef] = {
    MusicTrack.MENU:         MusicDef("menu", volume=0.7, loop=True, fade_ms=600),
    MusicTrack.LEVEL_SELECT: MusicDef("level_select", volume=0.7, loop=True, fade_ms=600),
    MusicTrack.LEVEL:        MusicDef("level", volume=0.75, loop=True, fade_ms=800),
}
