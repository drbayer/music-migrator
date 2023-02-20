from musicfile import MusicFile
from os import makedirs, path
from shutil import copyfile
import logging


class MusicTrack(MusicFile):
    def __init__(self, trackName, albumArtist=None, albumName=None, trackNumber=None, discNumber=None, fileLocation=None, parentlog=None):
        logname = '.'.join([parentlog, "MusicTrack"]) if parentlog else "MusicTrack"
        self.logger = logging.getLogger(logname)
        self.trackName = trackName
        self.albumArtist = albumArtist
        self.albumName = albumName
        self.trackNumber = trackNumber
        self.discNumber = discNumber
        self.sourceFile = fileLocation
        self.sourceChecksum = None
        self.destinationFile = None
        self.destinationChecksum = None
        if self.sourceFile is not None:
            self.get_source_checksum()

    def __repr__(self):
        return f"MusicTrack(trackName: {self.trackName}, albumName: {self.albumName}, albumArtist: {self.albumArtist})"

    def copy_file(self, db):
        if path.exists(self.destinationFile):
            if self.sourceChecksum == self.get_checksum(self.destinationFile):
                self.logger.info(f"Track \"{self.trackName}\" from album \"{self.albumName}\" by {self.albumArtist}",
                                 "already exists in destination. Skipping track.")
            else:
                try:
                    makedirs(path.dirname(self.destinationFile), exist_ok=True)
                    copyfile(self.sourceFile, self.destinationFile)
                    self.destinationChecksum = self.get_checksum(self.destinationFile)
                except Exception as e:
                    self.logger.error(e.__dict__)
                    exit(1)
                if self.sourceChecksum == self.destinationChecksum:
                    db.add(artist=self.albumArtist, album=self.albumName, trackname=self.trackName, tracknumber=self.trackNumber,
                           discnumber=self.discNumber, sourcefile=self.sourceFile, destfile=self.destinationFile, checksum=self.sourceChecksum)
                    self.logger.info(f"Successfully migrated \"{self.trackName}\" from album \"{self.albumName}\" by \"{self.albumArtist}\"")
                else:
                    self.logger.error(f"Checksum mismatch between \"{self.sourceFile}\" and \"{self.destinationfile}\"")

    def get_source_checksum(self):
        if path.exists(self.sourceFile):
            self.logger.debug(f"Getting checksum of file {self.sourceFile}")
            self.sourceChecksum = self.get_checksum(self.sourceFile)
