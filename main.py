import sys
import os
from game import Game
from screens.splash_screen import SplashScreen

def main():
    # Ajustar el directorio de trabajo cuando se ejecuta como EXE (PyInstaller onefile)
    # para que las rutas relativas (imágenes, fuentes, etc.) funcionen.
    try:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)
    except Exception:
        pass
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

    # Instalar filtro de advertencia SOLO en builds congelados, para no interferir en desarrollo
    if getattr(sys, 'frozen', False):
        _install_libpng_warning_filter()
    game = Game()
    splash_screen = SplashScreen(game)
    game.change_screen(splash_screen)
    game.run()

if __name__ == "__main__":
    main()