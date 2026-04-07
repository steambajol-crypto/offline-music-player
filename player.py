import os
import vlc


class MusicPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.playlist = []
        self.current_index = -1

    def load_playlist(self, tracks):
        self.playlist = tracks
        self.current_index = 0 if tracks else -1

    def load_track(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Track not found: {file_path}")

        media = self.instance.media_new_path(file_path)
        self.player.set_media(media)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def play_index(self, index):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            self.load_track(self.playlist[index])
            self.play()

    def next_track(self):
        if not self.playlist:
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_index(self.current_index)

    def previous_track(self):
        if not self.playlist:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_index(self.current_index)

    def set_volume(self, volume):
        self.player.audio_set_volume(volume)

    def set_position(self, value):
        self.player.set_position(value / 1000.0)

    def get_position(self):
        pos = self.player.get_position()
        if pos < 0:
            return 0
        return int(pos * 1000)

    def get_length(self):
        length = self.player.get_length()
        return length if length > 0 else 0

    def get_time(self):
        current_time = self.player.get_time()
        return current_time if current_time > 0 else 0