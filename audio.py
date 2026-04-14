from pygame import mixer
import os, random

class AudioController:
    def __init__(self):
        mixer.init()
        self.current_track_name = ""

    def play_random_track(self, start_time=0):
        tracks_dir = os.path.join(os.path.dirname(__file__), "assets", "photon-tracks")
        try:
            tracks = [
                os.path.join(tracks_dir, filename)
                for filename in os.listdir(tracks_dir)
                if filename.startswith("Track") and filename.endswith(".mp3")
            ]
        except FileNotFoundError:
            print("Photon track directory not found.")
            return

        if not tracks:
            print("No photon tracks available to play.")
            return

        selected_track = random.choice(tracks)
        try:
            mixer.music.load(selected_track)
            mixer.music.play(start=start_time)
            self.current_track_name = os.path.basename(selected_track)
        except Exception as ex:
            print(f"Failed to play audio track {selected_track}: {ex}")

    def stop(self):
        mixer.music.stop()
    
    def quit(self):
        mixer.quit()


if __name__ == "__main__":
    music = AudioController()
    music.play_random_track()
    input(f"Playing {music.current_track_name}. Press enter to quit... ")
    music.quit()