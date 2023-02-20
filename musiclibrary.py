import subprocess
import json
import logging
from sys import exit
from musictrack import MusicTrack


class MusicLibrary:
    def __init__(self, playlist="All Music", parentlog=None):
        logname = '.'.join([parentlog, "MusicLibrary"]) if parentlog else "MusicLibrary"
        self.logger = logging.getLogger(logname)
        self.logger.info('Initializing MusicLibrary')
        self.playlist = playlist
        if self.playlist_exists():
            self.get_playlist_length()
        else:
            exit(f"Playlist {self.playlist} not found!")

    def __repr__(self):
        return f"MusicLibrary(playlist: {self.playlist}, playlistLength: {self.playlistLength})"

    def get_playlist_length(self):
        self.logger.info(f"Getting length of playlist {self.playlist}")
        script = "musiclibrary/get_playlist_count.jxa"
        try:
            output = self.run_script(script, self.playlist)
            self.playlistLength = int(output)
        except subprocess.CalledProcessError as e:
            self.logger.error(e.__dict__)

    def playlist_exists(self):
        output = self.run_script("musiclibrary/playlist_exists.jxa", self.playlist)
        if output == "found":
            return True
        else:
            self.logger.error(f"Playlist {self.playlist} not found")
            return False

    def get_track_data(self, starting_track=0, page_length=5, page_count=1):
        self.logger.info(f"Getting track data for playlist {self.playlist}")
        next_track = starting_track
        page_number = 0

        if page_length == "all":
            page_length = self.playlistLength

        script = "musiclibrary/get_tracks.jxa"
        tracks = []

        while page_number < page_count:
            next_track = starting_track + page_length
            if next_track > self.playlistLength:
                next_track = self.playlistLength + 1

            try:
                track_info = self.run_script(script, self.playlist, str(starting_track), str(next_track))
                for track in json.loads(track_info)["items"]:
                    tracks.append(MusicTrack(**track))
            except subprocess.CalledProcessError as e:
                print(track_info.stdout)
                print(e)

            starting_track = next_track
            page_number += 1
        self.tracks = tracks

    def run_script(self, script, *args):
        try:
            output = subprocess.run(["/usr/bin/osascript", "-l", "JavaScript", f"{script}", *args], stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, check=True)
            return output.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(e.output)
