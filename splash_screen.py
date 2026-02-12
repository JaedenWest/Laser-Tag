#!/usr/bin/env python3
"""
splash_screen.py - Splash Screen Component

Displays the Photon logo for 3 seconds, then calls the callback
to transition to the next screen.
"""

import tkinter as tk
from PIL import Image, ImageTk
import os


class SplashScreen:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.frame = None
        self.photo = None

    def show(self):
        self.frame = tk.Frame(self.parent, bg="black")
        self.frame.pack(fill="both", expand=True)

        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.jpg")

        try:
            image = Image.open(logo_path)
            image.thumbnail((400, 300), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)

            logo_label = tk.Label(self.frame, image=self.photo, bg="black")
            logo_label.pack(expand=True)

        except FileNotFoundError:
            tk.Label(
                self.frame, text="PHOTON",
                font=("Helvetica", 72, "bold"), fg="red", bg="black",
            ).pack(expand=True)
            tk.Label(
                self.frame, text="Laser Tag System",
                font=("Helvetica", 24), fg="white", bg="black",
            ).pack()

        except Exception:
            tk.Label(
                self.frame, text="PHOTON",
                font=("Helvetica", 72, "bold"), fg="red", bg="black",
            ).pack(expand=True)

        self.parent.after(3000, self._end_splash)

    def _end_splash(self):
        if self.frame:
            self.frame.destroy()
        if self.callback:
            self.callback()

    def destroy(self):
        if self.frame:
            self.frame.destroy()


if __name__ == "__main__":
    def on_splash_end():
        root.destroy()

    root = tk.Tk()
    root.title("Splash Screen Test")
    root.geometry("800x600")
    root.configure(bg="black")

    splash = SplashScreen(root, on_splash_end)
    splash.show()
    root.mainloop()
