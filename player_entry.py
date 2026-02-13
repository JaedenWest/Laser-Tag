#!/usr/bin/env python3
"""
player_entry.py - Player Entry Screen Component

Operators enter player IDs and equipment IDs for Red and Green teams.
Codenames are auto-looked up from the database.
"""

import tkinter as tk
from tkinter import messagebox
from database import lookup_player_codename, add_new_player
from udp.udp_service import send_equipment_id, set_broadcast_address, get_broadcast_address


class PlayerEntryScreen:
    MAX_PLAYERS_PER_TEAM = 15

    def __init__(self, parent, start_game_callback):
        self.parent = parent
        self.start_game_callback = start_game_callback
        self.frame = None
        self.red_team_entries = []
        self.green_team_entries = []
        self.udp_addr_entry = None

    def show(self):
        self.frame = tk.Frame(self.parent, bg="#1a1a2e")
        self.frame.pack(fill="both", expand=True)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        tk.Label(
            self.frame, text="PHOTON LASER TAG - PLAYER ENTRY",
            font=("Helvetica", 24, "bold"), fg="white", bg="#1a1a2e",
        ).grid(row=0, column=0, columnspan=2, pady=20)

        self._create_team_frame("RED TEAM", 0, self.red_team_entries, "#ff4444")
        self._create_team_frame("GREEN TEAM", 1, self.green_team_entries, "#44ff44")
        self._create_button_frame()

        tk.Label(
            self.frame,
            text="Press F5 or click 'Start Game' to begin  |  Press F12 or click 'Clear All' to reset",
            font=("Helvetica", 10), fg="gray", bg="#1a1a2e",
        ).grid(row=3, column=0, columnspan=2, pady=10)

        self.parent.bind("<F5>", lambda e: self._start_game())
        self.parent.bind("<F12>", lambda e: self._clear_all())
        self.parent.bind("<F1>", lambda e: self._show_add_player_dialog())

        if self.red_team_entries:
            self.red_team_entries[0]["id"].focus_set()

    def _create_team_frame(self, team_name, column, entries_list, color):
        team_frame = tk.Frame(self.frame, bg="#1a1a2e")
        team_frame.grid(row=1, column=column, padx=20, pady=10, sticky="n")

        tk.Label(
            team_frame, text=team_name,
            font=("Helvetica", 18, "bold"), fg=color, bg="#1a1a2e",
        ).grid(row=0, column=0, columnspan=3, pady=(0, 10))

        for i, text in enumerate(["Player ID", "Codename", "Equipment ID"]):
            tk.Label(
                team_frame, text=text,
                font=("Helvetica", 10, "bold"), fg="white", bg="#1a1a2e",
            ).grid(row=1, column=i, padx=5, pady=2)

        for row in range(self.MAX_PLAYERS_PER_TEAM):
            entries_list.append(self._create_player_row(team_frame, row + 2))

    def _create_player_row(self, parent_frame, grid_row):
        entries = {}

        id_entry = tk.Entry(parent_frame, width=10, justify="center")
        id_entry.grid(row=grid_row, column=0, padx=2, pady=2)
        entries["id"] = id_entry

        codename_entry = tk.Entry(parent_frame, width=15, justify="center")
        codename_entry.grid(row=grid_row, column=1, padx=2, pady=2)
        codename_entry.config(state="readonly")
        entries["codename"] = codename_entry

        equipment_entry = tk.Entry(parent_frame, width=10, justify="center")
        equipment_entry.grid(row=grid_row, column=2, padx=2, pady=2)
        entries["equipment"] = equipment_entry

        # Multiple events to trigger codename lookup (macOS <FocusOut> can be unreliable)
        id_entry.bind("<Return>", lambda e, ent=entries: self._schedule_lookup(ent))
        id_entry.bind("<Tab>", lambda e, ent=entries: self._schedule_lookup(ent))
        id_entry.bind("<FocusOut>", lambda e, ent=entries: self._schedule_lookup(ent))
        codename_entry.bind("<Button-1>", lambda e, ent=entries: self._schedule_lookup(ent))
        equipment_entry.bind("<FocusIn>", lambda e, ent=entries: self._schedule_lookup(ent))
        equipment_entry.bind("<Return>", lambda e, ent=entries: self._broadcast_equipment(ent))


        return entries

    def _schedule_lookup(self, entries):
        self.parent.after(50, lambda: self._lookup_codename(entries))

    def _lookup_codename(self, entries):
        player_id = entries["id"].get().strip()

        if not player_id:
            entries["codename"].config(state="normal")
            entries["codename"].delete(0, tk.END)
            entries["codename"].config(state="readonly")
            return

        try:
            player_id_int = int(player_id)
            codename = lookup_player_codename(player_id_int)

            entries["codename"].config(state="normal")
            entries["codename"].delete(0, tk.END)
            entries["codename"].insert(0, codename if codename else "[Not Found]")
            entries["codename"].config(state="readonly")

        except ValueError:
            entries["codename"].config(state="normal")
            entries["codename"].delete(0, tk.END)
            entries["codename"].insert(0, "[Invalid ID]")
            entries["codename"].config(state="readonly")

    def _create_button_frame(self):
        button_frame = tk.Frame(self.frame, bg="#1a1a2e")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(
            button_frame, text="Add Player (F1)",
            font=("Helvetica", 14, "bold"), bg="#007bff", fg="white",
            padx=30, pady=10, command=self._show_add_player_dialog,
        ).pack(side="left", padx=20)

        tk.Button(
            button_frame, text="Start Game (F5)",
            font=("Helvetica", 14, "bold"), bg="#28a745", fg="white",
            padx=30, pady=10, command=self._start_game,
        ).pack(side="left", padx=20)

        tk.Button(
            button_frame, text="Clear All (F12)",
            font=("Helvetica", 14, "bold"), bg="#dc3545", fg="white",
            padx=30, pady=10, command=self._clear_all,
        ).pack(side="left", padx=20)

        # UDP address row (Sprint 2 requirement: configurable network)
        udp_frame = tk.Frame(button_frame, bg="#1a1a2e")
        udp_frame.pack(side="left", padx=20)

        tk.Label(
            udp_frame, text="UDP Address:",
            font=("Helvetica", 12, "bold"), fg="white", bg="#2e2b1a",
        ).pack(side="left", padx=(0, 8))

        self.udp_addr_entry = tk.Entry(udp_frame, width=16, justify="center")
        self.udp_addr_entry.pack(side="left")
        self.udp_addr_entry.insert(0, get_broadcast_address())

        tk.Button(
            udp_frame, text="Set UDP",
            font=("Helvetica", 12, "bold"), bg="#fcdc3b", fg="white",
            padx=14, pady=6, command=self._apply_udp_address,
        ).pack(side="left", padx=(10, 0))


    def _start_game(self):
        red_players = self._collect_team_data(self.red_team_entries)
        green_players = self._collect_team_data(self.green_team_entries)

        if not red_players:
            messagebox.showwarning("Warning", "Red team needs at least one player!")
            return
        if not green_players:
            messagebox.showwarning("Warning", "Green team needs at least one player!")
            return

        self.parent.unbind("<F5>")
        self.parent.unbind("<F12>")
        self.frame.destroy()

        if self.start_game_callback:
            self.start_game_callback(red_players, green_players)

    def _collect_team_data(self, entries_list):
        players = []
        for entries in entries_list:
            player_id = entries["id"].get().strip()
            equipment_id = entries["equipment"].get().strip()

            if player_id and equipment_id:
                entries["codename"].config(state="normal")
                codename = entries["codename"].get().strip()
                entries["codename"].config(state="readonly")

                players.append({
                    "id": player_id,
                    "codename": codename
                    if codename and codename not in ["[Not Found]", "[Invalid ID]"]
                    else f"Player {player_id}",
                    "equipment": equipment_id,
                })
        return players

    def _clear_all(self):
        for entries in self.red_team_entries + self.green_team_entries:
            entries["id"].delete(0, tk.END)
            entries["codename"].config(state="normal")
            entries["codename"].delete(0, tk.END)
            entries["codename"].config(state="readonly")
            entries["equipment"].delete(0, tk.END)

        if self.red_team_entries:
            self.red_team_entries[0]["id"].focus_set()

    def _broadcast_equipment(self, entries):
        player_id = entries["id"].get().strip()
        if not player_id:
            return
        equipment_id = entries["equipment"].get().strip()
        if not equipment_id:
            return
        try:
            send_equipment_id(int(equipment_id))
        except ValueError:
            messagebox.showerror("Input Error", "Equipment ID must be a number", detail="Press Enter to dismiss.")
        except OSError as ex:
            messagebox.showwarning("UDP Warning", f"Failed to broadcast equipment ID: {ex}", detail="Press Enter to dismiss.")

    def _apply_udp_address(self):
        if self.udp_addr_entry is None:
            return

        address = self.udp_addr_entry.get().strip()
        if not address:
            messagebox.showwarning("Input Error", "Please enter a UDP address.", detail="Press Enter to dismiss.")
            return

        # Basic “looks like an IP/hostname” check (not strict, but prevents empty/space)
        if " " in address:
            messagebox.showwarning("Input Error", "UDP address cannot contain spaces.", detail="Press Enter to dismiss.")
        return

        set_broadcast_address(address)
        messagebox.showinfo("UDP", f"UDP broadcast address set to: {address}", detail="Press Enter to dismiss.")

    def _apply_udp_address(self):
        if self.udp_addr_entry is None:
            return
        
        address = self.udp_addr_entry.get().strip()
        if not address:
            messagebox.showwarning("Input Error", "Please enter a UDP address.", detail="Press Enter to dismiss.")
            return
        if " " in address:
            messagebox.showwarning("Input Error", "UDP address cannot contain spaces.", detail="Press Enter to dismiss.")
            return
        
        set_broadcast_address(address)
        messagebox.showinfo("UDP", f"UDP broadcast address set to: {address}", detail="Press Enter to dismiss.")

    def _show_add_player_dialog(self):
        # Show a dialog to add a new player to the database.
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Player")
        dialog.geometry("400x250")
        dialog.configure(bg="#1a1a2e")
        dialog.resizable(False, False)

        # Center dialog on parent window
        dialog.transient(self.parent)
        dialog.grab_set()

        # Title
        tk.Label(
            dialog, text="Add New Player",
            font=("Helvetica", 16, "bold"), fg="white", bg="#1a1a2e",
        ).pack(pady=20)

        # Player ID frame
        id_frame = tk.Frame(dialog, bg="#1a1a2e")
        id_frame.pack(padx=20, pady=10, fill="x")

        tk.Label(
            id_frame, text="Player ID:",
            font=("Helvetica", 12), fg="white", bg="#1a1a2e",
        ).pack(side="left", padx=(0, 10))

        id_entry = tk.Entry(id_frame, width=20, font=("Helvetica", 12))
        id_entry.pack(side="left", fill="x", expand=True)

        # Codename frame
        codename_frame = tk.Frame(dialog, bg="#1a1a2e")
        codename_frame.pack(padx=20, pady=10, fill="x")

        tk.Label(
            codename_frame, text="Codename:",
            font=("Helvetica", 12), fg="white", bg="#1a1a2e",
        ).pack(side="left", padx=(0, 10))

        codename_entry = tk.Entry(codename_frame, width=20, font=("Helvetica", 12))
        codename_entry.pack(side="left", fill="x", expand=True)

        # Button frame
        button_frame = tk.Frame(dialog, bg="#1a1a2e")
        button_frame.pack(pady=20)

        def add_player():
            player_id = id_entry.get().strip()
            codename = codename_entry.get().strip()

            if not player_id or not codename:
                messagebox.showwarning("Input Error", "Please enter both Player ID and Codename", detail="Press Enter to dismiss.")
                return

            try:
                player_id_int = int(player_id)
            except ValueError:
                messagebox.showerror("Input Error", "Player ID must be a number", detail="Press Enter to dismiss.")
                return

            # Attempt to add the player
            success = add_new_player(player_id_int, codename)

            if success:
                messagebox.showinfo("Success", f"Player '{codename}' (ID: {player_id_int}) added successfully!", detail="Press Enter to dismiss.")
                # Refresh codenames for any entries with this player ID
                self._refresh_codenames_for_player(player_id_int)
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add player. The player ID may already exist.", detail="Press Enter to dismiss.")

        tk.Button(
            button_frame, text="Add Player (F1)",
            font=("Helvetica", 12, "bold"), bg="#28a745", fg="white",
            padx=30, pady=8, command=add_player,
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame, text="Cancel (Esc)",
            font=("Helvetica", 12, "bold"), bg="#dc3545", fg="white",
            padx=30, pady=8, command=dialog.destroy,
        ).pack(side="left", padx=10)

        # Key bindings
        dialog.bind("<F1>", lambda e: add_player())
        dialog.bind("<Escape>", lambda e: dialog.destroy())

        # Focus on first field
        id_entry.focus_set()

    def _refresh_codenames_for_player(self, player_id):
        # Update codename fields for any entries with the given player ID.
        all_entries = self.red_team_entries + self.green_team_entries
        for entries in all_entries:
            entry_id = entries["id"].get().strip()
            if entry_id:
                try:
                    if int(entry_id) == player_id:
                        self._lookup_codename(entries)
                except ValueError:
                    pass

    def destroy(self):
        if self.frame:
            self.frame.destroy()


if __name__ == "__main__":
    def on_start_game(red_players, green_players):
        print(f"Red team:   {red_players}")
        print(f"Green team: {green_players}")
        root.destroy()

    root = tk.Tk()
    root.title("Player Entry Test")
    root.geometry("1024x768")
    root.configure(bg="#1a1a2e")

    screen = PlayerEntryScreen(root, on_start_game)
    screen.show()
    root.mainloop()
