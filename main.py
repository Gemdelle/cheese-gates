from game import Game
from screens.splash_screen import SplashScreen

def main():
    game = Game()
    splash_screen = SplashScreen(game)
    game.change_screen(splash_screen)
    game.run()

if __name__ == "__main__":
    main()