import hashlib
from os import path


class MusicFile:
    @staticmethod
    def get_checksum(filename):
        if path.exists(filename):
            filehash = hashlib.md5(open(filename, "rb").read()).hexdigest()
            return filehash
