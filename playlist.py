import json
import os


class PlaylistManager:
    def __init__(self, save_file="playlists.json"):
        self.save_file = save_file

    def save_playlist(self, tracks):
        with open(self.save_file, "w", encoding="utf-8") as f:
            json.dump(tracks, f, indent=2)

    def load_playlist(self):
        if not os.path.exists(self.save_file):
            return []

        with open(self.save_file, "r", encoding="utf-8") as f:
            return json.load(f)