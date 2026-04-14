#!/usr/bin/env python3
"""
main.py - Photon Laser Tag Main Application (UI Shell)

Entry point. Coordinates screen transitions:
    Splash Screen → Player Entry → Countdown → Play Action → Player Entry (loop)
"""

import tkinter as tk
from splash_screen import SplashScreen
from player_entry import PlayerEntryScreen
from countdown import CountdownScreen
from play_action import PlayActionScreen


class PhotonApp:
    """Main application class. Owns the window and manages screen transitions."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Photon Laser Tag System")
        self.root.geometry("1024x768")
        self.root.configure(bg="black")
        self.current_screen = None

    def run(self):
        self.show_splash()
        self.root.mainloop()

    def show_splash(self):
        self.current_screen = SplashScreen(self.root, self.show_player_entry)
        self.current_screen.show()

    def show_player_entry(self):
        self.current_screen = PlayerEntryScreen(self.root, self.start_game)
        self.current_screen.show()

    def start_game(self, red_players, green_players, short_countdown=False):
        print("Game starting!")
        print(f"  Red team  ({len(red_players)} players): {red_players}")
        print(f"  Green team ({len(green_players)} players): {green_players}")

        # Show the countdown before game starts
        self.show_countdown(red_players, green_players, short_countdown)
    
    def show_countdown(self, red_players, green_players, short_countdown=False):
        self.current_screen = CountdownScreen(
            self.root,
            lambda: self._show_game(red_players, green_players),
            self.show_player_entry,
            short_countdown,
        )
        self.current_screen.show()


    def _show_game(self, red_players, green_players):
        self.current_screen = PlayActionScreen(
            self.root, red_players, green_players, self.show_player_entry
        )
        self.current_screen.show()

    def quit(self):
        self.root.quit()
        self.root.destroy()


def main():
    print("Starting Photon Laser Tag System...")
    app = PhotonApp()
    app.run()


if __name__ == "__main__":
    main()
