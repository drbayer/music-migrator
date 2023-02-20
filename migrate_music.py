#!/usr/bin/env python

from musicdb import MusicDB
from musiclibrary import MusicLibrary
from plexlibrary import PlexLibrary
from musicfile import MusicFile
from os import path
import click
import logging


@click.command()
@click.option('-p', '--playlist', prompt=True, default="All Music", show_default=True, help="Name of playlist to migrate")
@click.option('-m', '--mediadir', prompt=True, default="/Volumes/Media", show_default=True, help="Root media dir for Plex library")
@click.option('-u', '--musicdir', prompt=True, default="Music", show_default=True, help="Music dir in Plex media library")
@click.option('-d', '--database', prompt=True, default="music_migration.db", show_default=True, help="Database containing migration progress")
@click.option('-v', '--verbose', count=True, help="Verbosity level. Can be specified multiple times (e.g. -vvv)")
def migrate(playlist, mediadir, musicdir, database, verbose):
    loglevel = 40 - (10 * verbose)
    logger.setLevel(loglevel)
    mediadir = path.expanduser(mediadir)
    destination_dir = path.join(mediadir, musicdir)
    migration_db = path.join(mediadir, database)
    PlexLib = PlexLibrary(media_path=destination_dir, parentlog=logger.name)
    MigrationDB = MusicDB(database_name=migration_db, parentlog=logger.name)
    AppleMusic = MusicLibrary(playlist=playlist, parentlog=logger.name)
    AppleMusic.get_track_data(page_length="all")
    migrate_tracks(AppleMusic.tracks, PlexLib, MigrationDB)


def migrate_tracks(tracks, plex, db):
    for track in tracks:
        if track.fileLocation is None:
            logger.info(f"Track \"{track.trackName}\" from album \"{track.albumName}\" by {track.albumArtist} not available locally. Skipping track.")
            continue

        plex.build_filename(track)
        if path.exists(track.destinationFile):
            if track.sourceCheckSum == MusicFile.get_checksum(track.destinationFile):
                logger.info(f"Track \"{track.trackName}\" from album \"{track.albumName}\" by {track.albumArtist}",
                            "already exists in destination. Skipping track.")
                continue
        track.copy_file()


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    filename='music_migration.log',
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%Y%m%d %H:%M:%S')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger = logging.getLogger('migrate_music')


if __name__ == "__main__":
    logger.info("Starting music migration")
    migrate()
    logger.info("Ending music migration")
