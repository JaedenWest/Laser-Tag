#!/usr/bin/env python3
"""
play_action.py - Play Action Screen Component

Displays both teams' players with codenames and scores, a timer placeholder,
and an event log placeholder during an active game.
"""

import tkinter as tk


class PlayActionScreen:
    """Displays the in-game action screen with teams, timer, and event log."""

    def __init__(self, parent, red_players, green_players, end_callback):
        self.parent = parent
        self.red_players = red_players
        self.green_players = green_players
        self.end_callback = end_callback
        self.frame = None

    def show(self):
        self.frame = tk.Frame(self.parent, bg="#1a1a2e")
        self.frame.pack(fill="both", expand=True)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)

        # Header
        tk.Label(
            self.frame, text="GAME IN PROGRESS",
            font=("Helvetica", 28, "bold"), fg="white", bg="#1a1a2e",
        ).grid(row=0, column=0, columnspan=3, pady=20)

        # Row 1: Team panels and timer
        self._create_team_panel(self.red_players, "RED TEAM", "#ff4444", column=0)
        self._create_timer_panel()
        self._create_team_panel(self.green_players, "GREEN TEAM", "#44ff44", column=2)

        # Row 2: Event log
        self._create_event_log()

        # Row 3: Footer
        self._create_footer()

        self.parent.bind("<F5>", lambda e: self._end_game())

    def _create_team_panel(self, players, team_name, color, column):
        panel = tk.Frame(
            self.frame, bg="#0f0f23", bd=2, relief="groove",
        )
        panel.grid(row=1, column=column, padx=10, pady=10, sticky="nsew")

        tk.Label(
            panel, text=team_name,
            font=("Helvetica", 16, "bold"), fg=color, bg="#0f0f23",
        ).pack(pady=(10, 5))

        header = tk.Frame(panel, bg="#0f0f23")
        header.pack(fill="x", padx=15)

        tk.Label(
            header, text="Codename",
            font=("Helvetica", 11, "bold"), fg="white", bg="#0f0f23",
        ).pack(side="left")

        tk.Label(
            header, text="Score",
            font=("Helvetica", 11, "bold"), fg="white", bg="#0f0f23",
        ).pack(side="right")

        if players:
            for player in players:
                row = tk.Frame(panel, bg="#0f0f23")
                row.pack(fill="x", padx=15, pady=2)

                tk.Label(
                    row, text=player.get("codename", "Unknown"),
                    font=("Helvetica", 12), fg=color, bg="#0f0f23",
                ).pack(side="left")

                tk.Label(
                    row, text="0",
                    font=("Helvetica", 12), fg="white", bg="#0f0f23",
                ).pack(side="right")
        else:
            tk.Label(
                panel, text="No players",
                font=("Helvetica", 11, "italic"), fg="gray", bg="#0f0f23",
            ).pack(pady=10)

    def _create_timer_panel(self):
        panel = tk.Frame(
            self.frame, bg="#0f0f23", bd=2, relief="groove",
        )
        panel.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(
            panel, text="GAME TIMER",
            font=("Helvetica", 16, "bold"), fg="white", bg="#0f0f23",
        ).pack(pady=(10, 5))

        tk.Label(
            panel, text="6:00",
            font=("Helvetica", 48, "bold"), fg="#ffcc00", bg="#0f0f23",
        ).pack(pady=10)

        tk.Label(
            panel, text="(Sprint 4)",
            font=("Helvetica", 10, "italic"), fg="gray", bg="#0f0f23",
        ).pack()

    def _create_event_log(self):
        log_frame = tk.Frame(
            self.frame, bg="#0f0f23", bd=2, relief="groove",
        )
        log_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        tk.Label(
            log_frame, text="EVENT LOG",
            font=("Helvetica", 14, "bold"), fg="white", bg="#0f0f23",
        ).pack(pady=(10, 5))

        text_frame = tk.Frame(log_frame, bg="#0a0a1a")
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self.event_log = tk.Text(
            text_frame, height=8, bg="#0a0a1a", fg="#888888",
            font=("Courier", 10), state="normal", wrap="word",
            yscrollcommand=scrollbar.set,
        )
        self.event_log.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.event_log.yview)
        self.event_log.insert("1.0", "Game events will appear here during gameplay...")
        self.event_log.config(state="disabled")

    def _create_footer(self):
        footer = tk.Frame(self.frame, bg="#1a1a2e")
        footer.grid(row=3, column=0, columnspan=3, pady=15)

        tk.Button(
            footer, text="End Game (F5)",
            font=("Helvetica", 14, "bold"), bg="#dc3545", fg="white",
            padx=30, pady=10, command=self._end_game,
        ).pack()

    def _end_game(self):
        self.parent.unbind("<F5>")
        if self.frame:
            self.frame.destroy()
            self.frame = None
        if self.end_callback:
            self.end_callback()

    def destroy(self):
        self.parent.unbind("<F5>")
        if self.frame:
            self.frame.destroy()
            self.frame = None


if __name__ == "__main__":
    def on_end_game():
        print("Game ended!")
        root.destroy()

    root = tk.Tk()
    root.title("Play Action Screen Test")
    root.geometry("1024x768")
    root.configure(bg="#1a1a2e")

    red = [
        {"id": "1", "codename": "Viper", "equipment": "101"},
        {"id": "3", "codename": "Shadow", "equipment": "103"},
    ]
    green = [
        {"id": "2", "codename": "Phoenix", "equipment": "102"},
        {"id": "4", "codename": "Storm", "equipment": "104"},
    ]

    screen = PlayActionScreen(root, red, green, on_end_game)
    screen.show()
    root.mainloop()
