import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QFileDialog,
    QLabel,
    QSlider,
)

from player import MusicPlayer
from playlist import PlaylistManager


def format_ms(ms):
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


class MusicPlayerWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Offline Music Player")
        self.resize(700, 500)

        self.player = MusicPlayer()
        self.playlist_manager = PlaylistManager()

        self.tracks = self.playlist_manager.load_playlist()
        self.is_seeking = False

        self.build_ui()
        self.player.set_volume(80)
        self.load_saved_tracks()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)

    def build_ui(self):
        main_layout = QVBoxLayout()

        self.track_label = QLabel("No track loaded")
        self.track_label.setWordWrap(True)
        self.track_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.track_label)

        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_track)
        main_layout.addWidget(self.playlist_widget)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.time_label)

        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderPressed.connect(self.start_seek)
        self.seek_slider.sliderReleased.connect(self.end_seek)
        main_layout.addWidget(self.seek_slider)

        controls_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Songs")
        self.prev_button = QPushButton("Previous")
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.next_button = QPushButton("Next")

        self.load_button.clicked.connect(self.load_songs)
        self.prev_button.clicked.connect(self.play_previous)
        self.play_button.clicked.connect(self.play_current)
        self.pause_button.clicked.connect(self.player.pause)
        self.next_button.clicked.connect(self.play_next)

        controls_layout.addWidget(self.load_button)
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.next_button)

        main_layout.addLayout(controls_layout)

        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.player.set_volume)

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)

        main_layout.addLayout(volume_layout)

        self.setLayout(main_layout)

    def load_saved_tracks(self):
        if self.tracks:
            self.player.load_playlist(self.tracks)
            for track in self.tracks:
                self.playlist_widget.addItem(os.path.basename(track))

    def load_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.wav *.flac *.aac *.m4a)"
        )

        if not files:
            return

        self.tracks = files
        self.playlist_widget.clear()

        for track in self.tracks:
            self.playlist_widget.addItem(os.path.basename(track))

        self.player.load_playlist(self.tracks)
        self.playlist_manager.save_playlist(self.tracks)

        self.track_label.setText("Songs loaded")

    def play_selected_track(self, item=None):
        index = self.playlist_widget.currentRow()
        if index >= 0:
            self.player.play_index(index)
            self.track_label.setText(os.path.basename(self.tracks[index]))

    def play_current(self):
        current_row = self.playlist_widget.currentRow()

        if current_row >= 0:
            self.player.play_index(current_row)
            self.playlist_widget.setCurrentRow(current_row)
            self.track_label.setText(os.path.basename(self.tracks[current_row]))
        elif self.tracks:
            self.player.play_index(0)
            self.playlist_widget.setCurrentRow(0)
            self.track_label.setText(os.path.basename(self.tracks[0]))

    def play_next(self):
        self.player.next_track()
        if self.player.current_index >= 0:
            self.playlist_widget.setCurrentRow(self.player.current_index)
            self.track_label.setText(
                os.path.basename(self.tracks[self.player.current_index])
            )

    def play_previous(self):
        self.player.previous_track()
        if self.player.current_index >= 0:
            self.playlist_widget.setCurrentRow(self.player.current_index)
            self.track_label.setText(
                os.path.basename(self.tracks[self.player.current_index])
            )

    def start_seek(self):
        self.is_seeking = True

    def end_seek(self):
        self.player.set_position(self.seek_slider.value())
        self.tracks = self.playlist_manager.load_playlist()
        self.is_seeking = False
        self.track_was_playing = False
    def update_progress(self):
        if not self.tracks:
            return

        state = self.player.player.get_state()
        current_time = self.player.get_time()
        total_time = self.player.get_length()

        if total_time > 0:
            self.time_label.setText(
                f"{format_ms(current_time)} / {format_ms(total_time)}"
            )

        if not self.is_seeking:
            self.seek_slider.setValue(self.player.get_position())

        # detect track end safely
        if state == 3:  # playing
            self.track_was_playing = True
        elif self.track_was_playing and state == 6:  # ended
            self.track_was_playing = False
            self.play_next()