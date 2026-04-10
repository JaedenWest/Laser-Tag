#!/usr/bin/env python3
"""
play_action.py - Play Action Screen Component

Handles:
- live player scores
- team totals
- event log
- UDP gameplay events
"""
from PIL import Image, ImageTk
import os
import tkinter as tk
from udp.udp_service import set_message_handler, send_message
from queue import Queue, Empty

class PlayActionScreen:
    """Displays the in-game action screen with teams, timer, and event log."""

    def __init__(self, parent, red_players, green_players, end_callback):
        self.parent = parent
        self.red_players = red_players
        self.green_players = green_players
        self.end_callback = end_callback
        self.frame = None

        self.players_by_equipment = {}
        self.red_score_var = tk.StringVar(value="0")
        self.green_score_var = tk.StringVar(value="0")
        self.timer_var = tk.StringVar(value="6:00")

        self.red_player_rows = []
        self.green_player_rows = []

        self.game_seconds_remaining = 360
        self.timer_job = None

        self.flash_on = False
        self.flash_job = None

        self.red_score_title_label = None
        self.red_score_value_label = None
        self.green_score_title_label = None
        self.green_score_value_label = None

        self.pending_udp_events = Queue()
        self.poll_job = None

        self._build_player_state()

    def _build_player_state(self):
        for player in self.red_players:
            equipment = int(player["equipment"])
            self.players_by_equipment[equipment] = {
                "id": player["id"],
                "codename": player["codename"],
                "equipment": equipment,
                "team": "red",
                "score": 0,
                "has_base": False,
            }

        for player in self.green_players:
            equipment = int(player["equipment"])
            self.players_by_equipment[equipment] = {
                "id": player["id"],
                "codename": player["codename"],
                "equipment": equipment,
                "team": "green",
                "score": 0,
                "has_base": False,
            }


    def show(self):
        self.frame = tk.Frame(self.parent, bg="#1a1a2e")
        self.frame.pack(fill="both", expand=True)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)

        # Load trophy image

        img = Image.open(os.path.join("assets", "images", "Trophy.png"))
        img = img.resize((25, 25), Image.LANCZOS)
        self.trophy_image = ImageTk.PhotoImage(img)


        header = tk.Frame(self.frame, bg="#1a1a2e")
        header.grid(row=0, column=0, columnspan=3, pady=20, sticky="ew")

        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=1)

        red_frame = tk.Frame(header, bg="#1a1a2e")
        red_frame.grid(row=0, column=0)

        red_row = tk.Frame(red_frame, bg="#1a1a2e")
        red_row.pack(fill="x")

        self.red_left_trophy = tk.Label(red_row, image=self.trophy_image, bg="#1a1a2e")
        self.red_left_trophy.grid(row=0, column = 0, padx=(0, 5))

        self.red_score_title_label = tk.Label(
            red_row,
            text="RED TEAM SCORE",
            font=("Helvetica", 17, "bold"),
            fg="#ff4444",
            bg="#1a1a2e",
        )
        self.red_score_title_label.grid(row=0, column=1, padx=5)

        self.red_right_trophy = tk.Label(red_row, image=self.trophy_image, bg="#1a1a2e")
        self.red_right_trophy.grid(row=0, column=2, padx=(5,0))

        self.red_score_value_label = tk.Label(
            red_frame,
            textvariable=self.red_score_var,
            font=("Helvetica", 28, "bold"),
            fg="white",
            bg="#1a1a2e",
        )
        self.red_score_value_label.pack()

        tk.Label(
            header,
            text="GAME IN PROGRESS",
            font=("Helvetica", 28, "bold"),
            fg="white",
            bg="#1a1a2e",
        ).grid(row=0, column=1, padx=20)

        green_frame = tk.Frame(header, bg="#1a1a2e")
        green_frame.grid(row=0, column=2)

        green_row = tk.Frame(green_frame, bg="#1a1a2e")
        green_row.pack(fill = "x")

        self.green_left_trophy = tk.Label(green_row, image=self.trophy_image, bg="#1a1a2e")
        self.green_left_trophy.grid(row=0, column=0, padx=(0, 5))

        
        self.green_right_trophy = tk.Label(green_row, image=self.trophy_image, bg="#1a1a2e")
        self.green_right_trophy.grid(row=0, column=2, padx=(5, 0))


        self.green_score_title_label = tk.Label(
            green_row,
            text="GREEN TEAM SCORE",
            font=("Helvetica", 17, "bold"),
            fg="#44ff44",
            bg="#1a1a2e",
        )
        self.green_score_title_label.grid(row=0, column=1, padx=5)

        self.green_score_value_label = tk.Label(
            green_frame,
            textvariable=self.green_score_var,
            font=("Helvetica", 28, "bold"),
            fg="white",
            bg="#1a1a2e",
        )
        self.green_score_value_label.pack()

        self._create_team_panel("red", "RED TEAM", "#ff4444", column=0)
        self._create_timer_panel()
        self._create_team_panel("green", "GREEN TEAM", "#44ff44", column=2)
        self._create_event_log()
        self._create_footer()

        self.parent.bind("<F5>", lambda e: self._end_game())

        set_message_handler(self._handle_udp_message)
        self._refresh_scores()
        self._log_event("Game started")
        self._start_game_timer()
        self._start_score_flash()
        self._poll_udp_queue()
        send_message(202)

    def _hide_all_trophies(self):
        self.red_left_trophy.grid_remove()
        self.red_right_trophy.grid_remove()
        self.green_left_trophy.grid_remove()
        self.green_right_trophy.grid_remove()
    def _show_red_trophies(self):
        self.red_left_trophy.grid()
        self.red_right_trophy.grid()
    def _show_green_trophies(self):
        self.green_left_trophy.grid()
        self.green_right_trophy.grid()

    def _create_team_panel(self, team_key, team_name, color, column):
        panel = tk.Frame(self.frame, bg="#0f0f23", bd=2, relief="groove")
        panel.grid(row=1, column=column, padx=10, pady=10, sticky="nsew")

        tk.Label(
            panel,
            text=team_name,
            font=("Helvetica", 16, "bold"),
            fg=color,
            bg="#0f0f23",
        ).pack(pady=(10, 5))

        header = tk.Frame(panel, bg="#0f0f23")
        header.pack(fill="x", padx=15)

        tk.Label(
            header,
            text="Codename",
            font=("Helvetica", 11, "bold"),
            fg="white",
            bg="#0f0f23",
        ).pack(side="left")

        tk.Label(
            header,
            text="Score",
            font=("Helvetica", 11, "bold"),
            fg="white",
            bg="#0f0f23",
        ).pack(side="right")

        rows = self.red_player_rows if team_key == "red" else self.green_player_rows
        players = [
            player for player in self.players_by_equipment.values()
            if player["team"] == team_key
        ]

        for player in players:
            row = tk.Frame(panel, bg="#0f0f23")
            row.pack(fill="x", padx=15, pady=2)

            name_var = tk.StringVar(value=player["codename"])
            score_var = tk.StringVar(value=str(player["score"]))

            tk.Label(
                row,
                textvariable=name_var,
                font=("Helvetica", 12),
                fg=color,
                bg="#0f0f23",
            ).pack(side="left")

            tk.Label(
                row,
                textvariable=score_var,
                font=("Helvetica", 12),
                fg="white",
                bg="#0f0f23",
            ).pack(side="right")

            rows.append({
                "equipment": player["equipment"],
                "name_var": name_var,
                "score_var": score_var,
            })

    def _create_timer_panel(self):
        panel = tk.Frame(self.frame, bg="#0f0f23", bd=2, relief="groove")
        panel.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(
            panel,
            text="GAME TIMER",
            font=("Helvetica", 16, "bold"),
            fg="white",
            bg="#0f0f23",
        ).pack(pady=(10, 5))

        tk.Label(
            panel,
            textvariable=self.timer_var,
            font=("Helvetica", 48, "bold"),
            fg="#ffcc00",
            bg="#0f0f23",
        ).pack(pady=10)

    def _create_event_log(self):
        log_frame = tk.Frame(self.frame, bg="#0f0f23", bd=2, relief="groove")
        log_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        tk.Label(
            log_frame,
            text="EVENT LOG",
            font=("Helvetica", 14, "bold"),
            fg="white",
            bg="#0f0f23",
        ).pack(pady=(10, 5))

        text_frame = tk.Frame(log_frame, bg="#0a0a1a")
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self.event_log = tk.Text(
            text_frame,
            height=8,
            bg="#0a0a1a",
            fg="#dddddd",
            font=("Courier", 10),
            state="disabled",
            wrap="word",
            yscrollcommand=scrollbar.set,
        )
        self.event_log.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.event_log.yview)

    def _create_footer(self):
        footer = tk.Frame(self.frame, bg="#1a1a2e")
        footer.grid(row=3, column=0, columnspan=3, pady=15)

        tk.Button(
            footer,
            text="End Game (F5)",
            font=("Helvetica", 14, "bold"),
            bg="#dc3545",
            fg="white",
            padx=30,
            pady=10,
            command=self._end_game,
        ).pack()

    def _start_game_timer(self):
        self.game_seconds_remaining = 360
        self._update_timer_display()
        self._tick_timer()

    def _tick_timer(self):
        if self.game_seconds_remaining <= 0:
            self.timer_var.set("0:00")
            self._log_event("Game over")
            self._end_game()
            return

        self.game_seconds_remaining -= 1
        self._update_timer_display()
        self.timer_job = self.parent.after(1000, self._tick_timer)

    def _update_timer_display(self):
        minutes = self.game_seconds_remaining // 60
        seconds = self.game_seconds_remaining % 60
        self.timer_var.set(f"{minutes}:{seconds:02d}")

    def _start_score_flash(self):
        self._flash_score_labels()

    def _flash_score_labels(self):
        red_total = int(self.red_score_var.get())
        green_total = int(self.green_score_var.get())

        self.flash_on = not self.flash_on

        # reset defaults first
        self.red_score_title_label.config(fg="#ff4444")
        self.green_score_title_label.config(fg="#44ff44")
        self.red_score_value_label.config(fg="white")
        self.green_score_value_label.config(fg="white")

        #always hide both trophies first
        self._hide_all_trophies()

        if red_total > green_total:
            if self.flash_on:
                self.red_score_title_label.config(fg="white")
                self.red_score_value_label.config(fg="#ff4444")
                self._show_red_trophies()
                
        elif green_total > red_total:
            if self.flash_on:
                self.green_score_title_label.config(fg="white")
                self.green_score_value_label.config(fg="#44ff44")
                self._show_green_trophies()

        self.flash_job = self.parent.after(500, self._flash_score_labels)

    def _handle_udp_message(self, parsed):
        self.pending_udp_events.put(parsed)

    def _poll_udp_queue(self):
        try:
            while True:
                parsed = self.pending_udp_events.get_nowait()
                self._process_udp_message(parsed)
        except Empty:
            pass

        self.poll_job = self.parent.after(100, self._poll_udp_queue)

    def _process_udp_message(self, parsed):
        message_type = parsed[0]

        if message_type == "tag":
            attacker_eq = parsed[1]
            target_value = parsed[2]
            self._log_event(f"Received event: {attacker_eq}:{target_value}")
            self._handle_tag_event(attacker_eq, target_value)

        elif message_type == "code":
            self._log_event(f"Received code {parsed[1]}")

    def _handle_tag_event(self, attacker_eq, target_value):
        attacker = self.players_by_equipment.get(attacker_eq)

        if attacker is None:
            self._log_event(f"Unknown attacker equipment ID: {attacker_eq}")
            return

        if target_value == 43:
            if attacker["team"] == "red":
                attacker["score"] += 100
                attacker["has_base"] = True
                self._log_event(f"{attacker['codename']} captured GREEN base (+100)")
            else:
                self._log_event(f"{attacker['codename']} hit GREEN base, but no points awarded")
            self._refresh_scores()
            return

        if target_value == 53:
            if attacker["team"] == "green":
                attacker["score"] += 100
                attacker["has_base"] = True
                self._log_event(f"{attacker['codename']} captured RED base (+100)")
            else:
                self._log_event(f"{attacker['codename']} hit RED base, but no points awarded")
            self._refresh_scores()
            return

        target = self.players_by_equipment.get(target_value)

        if target is None:
            self._log_event(f"{attacker['codename']} triggered unknown target/event: {target_value}")
            return

        if attacker["team"] == target["team"]:
            attacker["score"] -= 10
            target["score"] -= 10

            send_message(attacker["equipment"])
            send_message(target["equipment"])

            self._log_event(
                f"Friendly fire: {attacker['codename']} hit teammate {target['codename']} (-10 each)"
            )
        else:
            attacker["score"] += 10

            send_message(target["equipment"])

            self._log_event(
                f"{attacker['codename']} tagged {target['codename']} (+10)"
            )

        self._refresh_scores()

    def _refresh_scores(self):
        red_total = 0
        green_total = 0

        for player in self.players_by_equipment.values():
            if player["team"] == "red":
                red_total += player["score"]
            else:
                green_total += player["score"]

        self.red_score_var.set(str(red_total))
        self.green_score_var.set(str(green_total))

        self._refresh_team_rows()

    def _refresh_team_rows(self):
        red_players = sorted(
            [p for p in self.players_by_equipment.values() if p["team"] == "red"],
            key=lambda player: player["score"],
            reverse=True,
        )

        green_players = sorted(
            [p for p in self.players_by_equipment.values() if p["team"] == "green"],
            key=lambda player: player["score"],
            reverse=True,
        )

        for row, player in zip(self.red_player_rows, red_players):
            name = player["codename"]
            if player["has_base"]:
                name = "[BASE] " + name
            row["name_var"].set(name)
            row["score_var"].set(str(player["score"]))

        for row, player in zip(self.green_player_rows, green_players):
            name = player["codename"]
            if player["has_base"]:
                name = "[BASE] " + name
            row["name_var"].set(name)
            row["score_var"].set(str(player["score"]))

    def _log_event(self, text):
        self.event_log.config(state="normal")
        self.event_log.insert("end", text + "\n")
        self.event_log.see("end")
        self.event_log.config(state="disabled")

    def _end_game(self):
        set_message_handler(None)

        if self.timer_job is not None:
            self.parent.after_cancel(self.timer_job)
            self.timer_job = None

        if self.flash_job is not None:
            self.parent.after_cancel(self.flash_job)
            self.flash_job = None

        if self.poll_job is not None:
            self.parent.after_cancel(self.poll_job)
            self.poll_job = None

        send_message(221)
        send_message(221)
        send_message(221)

        self.parent.unbind("<F5>")
        if self.frame:
            self.frame.destroy()
            self.frame = None
        if self.end_callback:
            self.end_callback()

    def destroy(self):
        set_message_handler(None)

        if self.timer_job is not None:
            self.parent.after_cancel(self.timer_job)
            self.timer_job = None

        if self.flash_job is not None:
            self.parent.after_cancel(self.flash_job)
            self.flash_job = None

        if self.poll_job is not None:
            self.parent.after_cancel(self.poll_job)
            self.poll_job = None

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