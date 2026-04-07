#!/usr/bin/env python3
"""
countdown.py - 30 Second Start Countdown Component

Displays a countdown from 30 to 1 using countdown images.
"""

import tkinter as tk


class CountdownScreen:
    """Displays a countdown before the game starts."""
    def __init__(self, parent, callback, cancel_callback, short_countdown=False):
        self.parent = parent
        self.callback = callback
        self.cancel_callback = cancel_callback
        self.frame = None
        self.label = None
        self.photo = None
        self.countdown_duration = 5 if short_countdown else 30
        self.current_number = self.countdown_duration
        self.scheduled_callback = None

    def show(self):
        """Display the countdown screen and start the countdown."""
        self.frame = tk.Frame(self.parent, bg="#1a1a2e")
        self.frame.pack(fill="both", expand=True)

        inner_frame = tk.Frame(self.frame, bg="#1a1a2e")
        inner_frame.pack(expand=True)

        tk.Label(
            inner_frame, text="The game will start in...",
            font=("Helvetica", 24, "bold"), fg="white", bg="#1a1a2e",
        ).pack()

        # Create label for countdown number
        self.label = tk.Label(
            inner_frame, text=self.current_number, font=("Helvetica", 72, "bold"), fg="white", bg="#1a1a2e"
        )
        self.label.pack()

        tk.Button(
            self.frame, text="Cancel (Esc)",
            font=("Helvetica", 14, "bold"), bg="#007bff", fg="white",
            padx=30, pady=10,
            command=self._cancel,
        ).pack(pady=30)

        self.parent.bind("<Escape>", lambda e: self._cancel())

        # Start the countdown
        self._start_countdown()

    def _start_countdown(self):
        """Start the countdown sequence."""
        self.current_number = self.countdown_duration

        # Start displaying countdown numbers
        self._show_next_number()


    def _show_next_number(self):
        """Display the next countdown number and schedule the next one."""
        if self.current_number <= 1:
            self._end_countdown()
            return

        self.current_number -= 1
        self.label.config(text=self.current_number)

        # Schedule next number (1 second delay)
        self.scheduled_callback = self.parent.after(
            1000, self._show_next_number
        )


    def _end_countdown(self):
        """Clean up and call the callback when countdown completes."""


        if self.frame:
            self.parent.unbind("<Escape>")
            self.frame.destroy()

        if self.callback:
            self.callback()

    def _cancel(self):
        """Cancel countdown and return to player entry."""
        self.callback = self.cancel_callback
        if self.scheduled_callback:
            self.parent.after_cancel(self.scheduled_callback)
        self._end_countdown()



    def destroy(self):
        """Clean up resources."""
        if self.scheduled_callback:
            self.parent.after_cancel(self.scheduled_callback)

        if self.frame:
            self.frame.destroy()


if __name__ == "__main__":

    def on_countdown_complete():
        print("Countdown complete!")
        root.destroy()
    
    def on_countdown_cancel():
        print("Countdown cancelled.")
        root.destroy()

    root = tk.Tk()
    root.title("Countdown Test")
    root.geometry("1024x768")
    root.configure(bg="black")

    countdown = CountdownScreen(root, on_countdown_complete, on_countdown_cancel)
    countdown.show()
    root.mainloop()
