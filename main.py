import sys
import os
import atexit

def main():
    # Ajustar el directorio de trabajo cuando se ejecuta como EXE (PyInstaller onefile)
    # para que las rutas relativas (imágenes, fuentes, etc.) funcionen.
    try:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)
    except Exception:
        pass
    # Filtro de advertencia de libpng iCCP en stderr (C-level). Se puede desactivar con
    # CHEESEGATES_SUPPRESS_LIBPNG=0. Por defecto activo en dev y en EXE.
    def _install_libpng_warning_filter():
        try:
            import threading
            pattern = b"libpng warning: iCCP: known incorrect sRGB profile"

            orig_fd = os.dup(2)           # dup de stderr real
            r_fd, w_fd = os.pipe()        # pipe para interceptar
            os.dup2(w_fd, 2)              # redirigir fd2 -> write end del pipe
            os.close(w_fd)                # cerramos el duplicado local del write end (fd2 sigue abierto)

            # Asegurar cierre de orig_fd al salir
            def _cleanup():
                try:
                    os.close(orig_fd)
                except Exception:
                    pass
            atexit.register(_cleanup)

            def _reader():
                try:
                    with os.fdopen(r_fd, 'rb', closefd=True) as rf, os.fdopen(orig_fd, 'wb', closefd=False) as of:
                        while True:
                            data = rf.readline()
                            if not data:
                                break
                            if pattern in data:
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

    if os.environ.get("CHEESEGATES_SUPPRESS_LIBPNG", "1") != "0":
        _install_libpng_warning_filter()
    # Importar tarde para evitar que se emitan warnings antes de instalar el filtro
    from game import Game
    from screens.splash_screen import SplashScreen
    game = Game()
    splash_screen = SplashScreen(game)
    game.change_screen(splash_screen)
    game.run()

if __name__ == "__main__":
    main()