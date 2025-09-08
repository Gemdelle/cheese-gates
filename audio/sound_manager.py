"""
SoundManager: Maneja SFX y música con pygame.mixer.

- Master/music/SFX enable + volume
- Auto-carga SFX desde assets/sounds y música desde assets/music
- Fade, loop, one-shot, y SFX en loop (e.g., pasos)
- Config JSON amigable (audio/audio_config.json) para eventos/música/escenas
"""
from __future__ import annotations

import os
import json
import random
from typing import Optional, Tuple

import pygame

try:
    from .audio_config import (
        SfxEvent,
        MusicTrack,
        SOUND_MAP,
        MUSIC_MAP,
        SoundDef,
        MusicDef,
    )
except Exception:
    SfxEvent = None
    MusicTrack = None
    SOUND_MAP = {}
    MUSIC_MAP = {}


def _find_file(base_dir: str, name: str, exts: Tuple[str, ...]) -> Optional[str]:
    for ext in exts:
        p = os.path.join(base_dir, f"{name}{ext}")
        if os.path.exists(p):
            return p
    return None


class SoundManager:
    _instance: Optional["SoundManager"] = None

    def __init__(self):
        # Singleton
        SoundManager._instance = self

        # Estados
        self.master_enabled = True
        self.music_enabled = True
        self.sfx_enabled = True

        # Volúmenes
        self.master_volume = 1.0
        self.music_volume = 0.8
        self.sfx_volume = 0.8

        # Caches
        self._sfx = {}
        self._missing_logged = {}
        self._played_once = {}
        self._loop_channels = {}

        # Música actual
        self._current_music = None

        # Rutas
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.sounds_dir = os.path.join(base_dir, "assets", "sounds")
        self.music_dir = os.path.join(base_dir, "assets", "music")
        self.config_path = os.path.join(os.path.dirname(__file__), "audio_config.json")

        # Extensiones
        self.sfx_exts = (".ogg", ".wav", ".mp3")
        self.music_exts = (".ogg", ".mp3", ".wav")

        # Config JSON
        self._cfg_events = {}
        self._cfg_music = {}
        self._cfg_scenes = {}
        self._load_json_config()

    # ================= Volumen/habilitar =================
    def set_enabled(self, enabled: bool):
        self.master_enabled = bool(enabled)
        vol = self.master_volume if self.master_enabled else 0.0
        pygame.mixer.music.set_volume(self.music_volume * vol)
        for s in self._sfx.values():
            try:
                s.set_volume(self.sfx_volume * vol)
            except Exception:
                pass
        for ch in self._loop_channels.values():
            try:
                ch.set_volume(self.sfx_volume * vol)
            except Exception:
                pass

    def set_music_enabled(self, enabled: bool):
        self.music_enabled = bool(enabled)
        if not self.music_enabled:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def set_sfx_enabled(self, enabled: bool):
        self.sfx_enabled = bool(enabled)
        if not self.sfx_enabled:
            # Stop all SFX immediately (does not affect music)
            try:
                # Fade out and clear looped SFX channels
                for name, ch in list(self._loop_channels.items()):
                    try:
                        ch.fadeout(150)
                    except Exception:
                        try:
                            ch.stop()
                        except Exception:
                            pass
                self._loop_channels.clear()
                # Stop any currently playing one-shot SFX channels
                pygame.mixer.stop()
            except Exception:
                pass
        else:
            # Restore volumes on cached SFX so next plays have correct loudness
            try:
                for s in self._sfx.values():
                    s.set_volume(self.sfx_volume * self.master_volume)
            except Exception:
                pass

    def set_master_volume(self, v: float):
        self.master_volume = max(0.0, min(1.0, v))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        for s in self._sfx.values():
            try:
                s.set_volume(self.sfx_volume * self.master_volume)
            except Exception:
                pass
        for ch in self._loop_channels.values():
            try:
                ch.set_volume(self.sfx_volume * self.master_volume)
            except Exception:
                pass

    def set_music_volume(self, v: float):
        self.music_volume = max(0.0, min(1.0, v))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def set_sfx_volume(self, v: float):
        self.sfx_volume = max(0.0, min(1.0, v))
        for s in self._sfx.values():
            try:
                s.set_volume(self.sfx_volume * self.master_volume)
            except Exception:
                pass
        for ch in self._loop_channels.values():
            try:
                ch.set_volume(self.sfx_volume * self.master_volume)
            except Exception:
                pass

    # ================= Config JSON =================
    def _load_json_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._cfg_events = dict(data.get("events", {}))
                self._cfg_music = dict(data.get("music", {}))
                self._cfg_scenes = dict(data.get("scenes", {}))
        except Exception as e:
            print(f"[Audio] Failed to load audio_config.json: {e}")

    # ================= SFX =================
    def _load_sfx(self, name: str):
        if name in self._sfx:
            return self._sfx[name]
        path = _find_file(os.path.abspath(self.sounds_dir), name, self.sfx_exts)
        if not path:
            if not self._missing_logged.get(name):
                print(f"[Audio] SFX missing: {name}")
                self._missing_logged[name] = True
            return None
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(self.sfx_volume * self.master_volume)
            self._sfx[name] = snd
            return snd
        except Exception as e:
            if not self._missing_logged.get(name):
                print(f"[Audio] Failed to load SFX {name}: {e}")
                self._missing_logged[name] = True
            return None

    def play_sfx(self, name: str, *, volume: Optional[float] = None, loop: bool = False,
                  maxtime: int = 0, fade_ms: int = 0) -> None:
        if not (self.master_enabled and self.sfx_enabled):
            return
        snd = self._load_sfx(name)
        if not snd:
            return
        if volume is not None:
            try:
                snd.set_volume(max(0.0, min(1.0, volume)) * self.master_volume)
            except Exception:
                pass
        loops = -1 if loop else 0
        try:
            snd.play(loops=loops, maxtime=maxtime, fade_ms=fade_ms)
        except Exception:
            pass

    # SFX por nombre desde JSON (no programar)
    def play_event_name(self, event_name: str, *, volume: Optional[float] = None,
                        loop: Optional[bool] = None, fade_in: int = 0) -> None:
        if not self._cfg_events:
            return
        cfg = self._cfg_events.get(event_name)
        if not cfg:
            return
        files = cfg.get("files") or []
        if not files:
            return
        name = random.choice(files) if len(files) > 1 else files[0]
        eff_vol = cfg.get("volume", 1.0) if volume is None else max(0.0, min(1.0, volume))
        eff_loop = bool(cfg.get("loop", False)) if loop is None else bool(loop)
        fade_ms = int(max(0, fade_in or 0))
        self.play_sfx(name, volume=eff_vol, loop=eff_loop, fade_ms=fade_ms)

    def play_sfx_once(self, name: str, **kwargs) -> None:
        if self._played_once.get(name):
            return
        self._played_once[name] = True
        self.play_sfx(name, **kwargs)

    # SFX en loop (para pasos/ambiente)
    def start_loop_sfx(self, name: str, *, volume: Optional[float] = None, fade_ms: int = 100) -> None:
        if not (self.master_enabled and self.sfx_enabled):
            return
        ch = self._loop_channels.get(name)
        if ch is not None and ch.get_busy():
            return
        snd = self._load_sfx(name)
        if not snd:
            return
        try:
            ch = snd.play(loops=-1, fade_ms=max(0, fade_ms))
            if ch is not None:
                eff_vol = self.sfx_volume if volume is None else max(0.0, min(1.0, volume))
                ch.set_volume(eff_vol * self.master_volume)
                self._loop_channels[name] = ch
        except Exception:
            pass

    def stop_loop_sfx(self, name: str, *, fade_ms: int = 150) -> None:
        ch = self._loop_channels.get(name)
        if not ch:
            return
        try:
            if fade_ms > 0:
                ch.fadeout(fade_ms)
            else:
                ch.stop()
        except Exception:
            pass
        self._loop_channels.pop(name, None)

    # ================= Música =================
    def play_music(self, name: str, *, volume: Optional[float] = None, loop: bool = True,
                   fade_ms: int = 600) -> None:
        if not self.master_enabled or not self.music_enabled:
            return
        path = _find_file(os.path.abspath(self.music_dir), name, self.music_exts)
        if not path:
            if not self._missing_logged.get(f"music:{name}"):
                print(f"[Audio] Music missing: {name}")
                self._missing_logged[f"music:{name}"] = True
            return
        try:
            if fade_ms > 0:
                try:
                    pygame.mixer.music.fadeout(fade_ms)
                except Exception:
                    pass
            pygame.mixer.music.load(path)
            vol = self.music_volume if volume is None else max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(vol * self.master_volume)
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            self._current_music = name
        except Exception as e:
            if not self._missing_logged.get(f"music:{name}"):
                print(f"[Audio] Failed to play music {name}: {e}")
                self._missing_logged[f"music:{name}"] = True

    def stop_music(self, *, fade_ms: int = 400):
        try:
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
        except Exception:
            pass
        self._current_music = None

    def stop_all(self, *, fade_ms_music: int = 300, fade_ms_sfx: int = 120) -> None:
        """Stop all audio: music and SFX (including loop channels)."""
        # Stop music
        self.stop_music(fade_ms=fade_ms_music)
        # Stop looped SFX channels
        try:
            for name, ch in list(self._loop_channels.items()):
                try:
                    if fade_ms_sfx > 0:
                        ch.fadeout(fade_ms_sfx)
                    else:
                        ch.stop()
                except Exception:
                    pass
            self._loop_channels.clear()
        except Exception:
            pass
        # Stop any one-shot SFX
        try:
            if fade_ms_sfx > 0:
                # pygame has no global fade; best effort: immediate stop
                pygame.mixer.stop()
            else:
                pygame.mixer.stop()
        except Exception:
            pass

    # Música por nombre desde JSON
    def play_music_name(self, music_name: str, *, volume: Optional[float] = None,
                        loop: Optional[bool] = None, fade_in: Optional[int] = None) -> None:
        if not self._cfg_music:
            return
        cfg = self._cfg_music.get(music_name)
        if not cfg:
            return
        name = cfg.get("file") or music_name
        eff_vol = cfg.get("volume", 1.0) if volume is None else max(0.0, min(1.0, volume))
        eff_loop = bool(cfg.get("loop", True)) if loop is None else bool(loop)
        eff_fade = int(max(0, cfg.get("fade_in", 600))) if fade_in is None else int(max(0, fade_in))
        self.play_music(name, volume=eff_vol, loop=eff_loop, fade_ms=eff_fade)

    # Escenas
    def enter_scene(self, scene_name: str) -> None:
        if not self._cfg_scenes:
            return
        cfg = self._cfg_scenes.get(scene_name)
        if not cfg:
            return
        music_key = cfg.get("music")
        if music_key:
            self.play_music_name(music_key)

    # ================= Utilidades =================
    def play_random(self, base_name: str, count: int, **kwargs):
        idx = random.randint(1, max(1, count))
        self.play_sfx(f"{base_name}{idx}", **kwargs)

    @classmethod
    def get(cls) -> Optional["SoundManager"]:
        return getattr(cls, "_instance", None)

    # ================= API Declarativa (limpia) =================
    def play_event(self, event, *, volume: Optional[float] = None, loop: Optional[bool] = None) -> None:
        if not SOUND_MAP or event not in SOUND_MAP:
            return
        spec: SoundDef = SOUND_MAP[event]
        if not spec.names:
            return
        name = random.choice(spec.names) if len(spec.names) > 1 else spec.names[0]
        eff_vol = spec.volume if volume is None else max(0.0, min(1.0, volume))
        eff_loop = spec.loop if loop is None else bool(loop)
        self.play_sfx(name, volume=eff_vol, loop=eff_loop)

    def play_music_track(self, track, *, volume: Optional[float] = None, loop: Optional[bool] = None,
                         fade_ms: Optional[int] = None) -> None:
        if not MUSIC_MAP or track not in MUSIC_MAP:
            return
        spec: MusicDef = MUSIC_MAP[track]
        eff_vol = spec.volume if volume is None else max(0.0, min(1.0, volume))
        eff_loop = spec.loop if loop is None else bool(loop)
        eff_fade = spec.fade_ms if fade_ms is None else int(max(0, fade_ms))
        self.play_music(spec.name, volume=eff_vol, loop=eff_loop, fade_ms=eff_fade)
