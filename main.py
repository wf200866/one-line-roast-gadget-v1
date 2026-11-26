"""Roast payload: wireless earbuds that save their single low-battery
warning for the worst possible moment -- the middle of a live call.

Stores the one-liner in /output/entry.txt for the grader to read.
"""

import os
import tempfile

JOKE = "My earbuds wait until I'm mid-sentence on a call to whisper 'battery low' — their one warning, timed perfectly to be useless."

MIN_CHARS = 1
MAX_CHARS = 200
OUTPUT_DIR = "/output"
OUTPUT_NAME = "entry.txt"
FILE_MODE = 0o644


def validate(value):
    """Return value only when it is a non-blank string of 1..200 characters.

    Anything else raises ValueError so a malformed roast never reaches disk.
    """
    if not isinstance(value, str):
        raise ValueError("payload must be a string")
    if not value.strip():
        raise ValueError("payload must not be empty or whitespace-only")
    length = len(value)
    if not (MIN_CHARS <= length <= MAX_CHARS):
        raise ValueError(
            "payload length %d out of range %d..%d"
            % (length, MIN_CHARS, MAX_CHARS)
        )
    return value


def _discard(path):
    """Best-effort removal of a staging file we created."""
    try:
        os.unlink(path)
    except OSError:
        pass


def _stage_on_disk(payload):
    """Write payload to a fresh temp file inside /output and return its path.

    /output already exists (main() creates it). Only the temp file itself is
    chmod'ed here; the directory is left alone because the grader runs as a
    uid that does not own it and a chmod on /output would raise.
    """
    fd, path = tempfile.mkstemp(dir=OUTPUT_DIR, prefix="roast.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
        os.chmod(path, FILE_MODE)
    except BaseException:
        _discard(path)
        raise
    return path


def _promote(staging):
    """Atomically rename staging to the final entry and fix its mode."""
    dest = os.path.join(OUTPUT_DIR, OUTPUT_NAME)
    try:
        os.replace(staging, dest)
    except BaseException:
        _discard(staging)
        raise
    os.chmod(dest, FILE_MODE)
    return dest


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    payload = validate(JOKE)
    staging = _stage_on_disk(payload)
    dest = _promote(staging)
    print("stored %d characters in %s" % (len(payload), dest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
