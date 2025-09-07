import io
import sys
from game import Game
from screens.splash_screen import SplashScreen

def main():
    # Filtrar advertencias de libpng iCCP en stderr (ruido conocido de algunos PNGs)
    class _StderrFilter(io.TextIOBase):
        def __init__(self, orig):
            self._orig = orig
        def write(self, s):
            try:
                if "libpng warning: iCCP: known incorrect sRGB profile" in s:
                    return 0
            except Exception:
                pass
            return self._orig.write(s)
        def flush(self):
            try:
                return self._orig.flush()
            except Exception:
                pass
    try:
        sys.stderr = _StderrFilter(sys.stderr)
    except Exception:
        pass
    game = Game()
    splash_screen = SplashScreen(game)
    game.change_screen(splash_screen)
    game.run()

if __name__ == "__main__":
    main()