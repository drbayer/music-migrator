#!/usr/bin/env python

from musicdb import MusicDB
from musiclibrary import MusicLibrary
from plexlibrary import PlexLibrary
from os import path
import click
import logging


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
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
    PlexLib = PlexLibrary(media_path=destination_dir)
    MigrationDB = MusicDB(database_name=migration_db)
    AppleMusic = MusicLibrary(playlist=playlist)
    AppleMusic.get_track_data(page_length="all")
    migrate_tracks(AppleMusic.tracks, PlexLib, MigrationDB)


def migrate_tracks(tracks, plex, db):
    for track in tracks:
        if track.sourceFile is None:
            logger.info(f"Track \"{track.trackName}\" from album \"{track.albumName}\" by {track.albumArtist} not available locally. Skipping track.")
            continue

        plex.build_filename(track)
        track.copy_file(db)


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
