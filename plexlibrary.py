from os import path
from sys import exit
import logging


class PlexLibrary:
    def __init__(self, media_path=path.expanduser("~/tmp/music/plexlib")):
        self.logger = logging.getLogger("PlexLibrary")
        self.logger.info(f"Initializing PlexLibrary with media path {media_path}")
        self.media_path = media_path
        if not path.exists(media_path):
            self.logger.error(f"Can't find Plex media folder at {media_path}. Abandon ship!")
            exit(1)

    def build_filename(self, track):
        if not track.sourceFile:
            self.logger.warn(f"Source file not set for {track}. Not setting destinationFile.")
        else:
            destFolder = path.join(self.media_path, track.albumArtist, track.albumName)
            if track.discNumber == 0 or track.discNumber is None:
                track.discNumber = 1
            destFilename = f"{track.discNumber}{track.trackNumber:02} - {track.trackName}{path.splitext(track.sourceFile)[1]}"
            track.destinationFile = path.join(destFolder, destFilename)
            self.logger.debug(f"Setting destination filename for {track} to {track.destinationFile}")
