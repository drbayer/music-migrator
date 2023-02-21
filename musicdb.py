import sqlite3
import logging
from os import path
from sys import exit


class MusicDB:
    def __init__(self, database_name="music_migration.db"):
        self.logger = logging.getLogger("MusicDB")
        self.logger.info("Initializing MusicDB")
        create_statement = """
        CREATE TABLE IF NOT EXISTS music(
        id INTEGER PRIMARY KEY,
        artist VARCHAR,
        album VARCHAR,
        trackname VARCHAR,
        tracknumber INTEGER,
        discnumber INTEGER,
        sourcefile VARCHAR,
        destfile VARCHAR,
        checksum VARCHAR,
        UNIQUE(artist, album, trackname, checksum)
        );
        """
        if not path.exists(path.dirname(database_name)):
            self.logger.error(f"Migration database folder '{path.dirname(database_name)}' not found. Abandon ship!")
            exit(1)

        self.logger.debug(f"Initializing database connection for {database_name}")
        self.db = sqlite3.connect(database_name)
        with self.db:
            self.db.execute(create_statement)

    def __del__(self):
        self.logger.debug("Closing connection to database")
        self.db.close()

    def add(self, artist, album, trackname, tracknumber, discnumber, sourcefile, destfile, checksum):
        insert_statement = """
        INSERT INTO music (artist, album, trackname, tracknumber, discnumber, sourcefile, destfile, checksum)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (artist, album, trackname, tracknumber, discnumber, sourcefile, destfile, checksum)
        with self.db:
            self.logger.debug(f"Writing to database for {trackname} by {artist} from album {album}")
            self.db.execute(insert_statement, params)

    def found(self, track):
        params = (track.trackName, track.albumName, track.albumArtist, track.trackNumber, track.discNumber)
        print(params)
        select_statement = """SELECT COUNT(checksum) FROM music
        WHERE trackname=? AND album=? AND artist=? AND tracknumber=? AND discnumber=?"""
        cursor = self.db.cursor()
        cursor.execute(select_statement, params)
        result = cursor.fetchone()[0]
        if result == 1:
            return True
        else:
            return False
