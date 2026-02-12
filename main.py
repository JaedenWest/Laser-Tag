#!/usr/bin/env python3
"""
main.py - Photon Laser Tag Main Application (UI Shell)

Entry point. Coordinates screen transitions:
    Splash Screen → Player Entry → Play Action (placeholder) → Player Entry (loop)
"""

import tkinter as tk
from splash_screen import SplashScreen
from player_entry import PlayerEntryScreen


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

    def start_game(self, red_players, green_players):
        print("Game starting!")
        print(f"  Red team  ({len(red_players)} players): {red_players}")
        print(f"  Green team ({len(green_players)} players): {green_players}")

        # TODO: Replace with PlayActionScreen when ready
        self._show_game_placeholder(red_players, green_players)

    def _show_game_placeholder(self, red_players, green_players):
        """Temporary stand-in for the Play Action Screen."""
        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="GAME IN PROGRESS",
            font=("Helvetica", 36, "bold"), fg="white", bg="#1a1a2e",
        ).pack(pady=40)

        info_text = f"Red Team: {len(red_players)} players\n"
        for p in red_players:
            info_text += f"  - {p['codename']} (ID: {p['id']}, Equipment: {p['equipment']})\n"
        info_text += f"\nGreen Team: {len(green_players)} players\n"
        for p in green_players:
            info_text += f"  - {p['codename']} (ID: {p['id']}, Equipment: {p['equipment']})\n"

        tk.Label(
            frame, text=info_text,
            font=("Courier", 14), fg="#cccccc", bg="#1a1a2e", justify="left",
        ).pack(pady=20)

        tk.Button(
            frame, text="New Game (Back to Player Entry)",
            font=("Helvetica", 14, "bold"), bg="#007bff", fg="white",
            padx=30, pady=10,
            command=lambda: self._return_to_entry(frame),
        ).pack(pady=30)

    def _return_to_entry(self, frame):
        frame.destroy()
        self.show_player_entry()

    def quit(self):
        self.root.quit()
        self.root.destroy()


def main():
    print("Starting Photon Laser Tag System...")
    app = PhotonApp()
    app.run()


if __name__ == "__main__":
    main()
