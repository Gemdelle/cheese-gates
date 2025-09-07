import sys
from game import Game
from screens.splash_screen import SplashScreen

def main():
    # Filtrar a nivel de FD (C) la advertencia específica de libpng iCCP en stderr,
    # manteniendo visibles el resto de errores/avisos.
    def _install_libpng_warning_filter():
        try:
            import os, threading
            pattern = b"libpng warning: iCCP: known incorrect sRGB profile"

            # Duplicar stderr real y crear una tubería para interceptar todo lo que salga por fd=2
            orig_fd = os.dup(2)
            r_fd, w_fd = os.pipe()
            os.dup2(w_fd, 2)
            os.close(w_fd)

            def _reader():
                try:
                    with os.fdopen(r_fd, 'rb', closefd=True) as rf, os.fdopen(orig_fd, 'wb', closefd=True) as of:
                        while True:
                            data = rf.readline()
                            if not data:
                                break
                            if pattern in data:
                                # Ignorar solo esta advertencia puntual
                                continue
                            try:
                                of.write(data)
                                of.flush()
                            except Exception:
                                pass
                except Exception:
                    pass

            threading.Thread(target=_reader, daemon=True).start()
        except Exception:
            pass

    _install_libpng_warning_filter()
    game = Game()
    splash_screen = SplashScreen(game)
    game.change_screen(splash_screen)
    game.run()

if __name__ == "__main__":
    main()