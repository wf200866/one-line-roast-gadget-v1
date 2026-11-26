"""Emit the project's lone entry file.

Subject here is the wireless earbuds and their single spoken alert: it fires
halfway through a sentence on a live call, which means the device's only
message to its owner is that it is about to die at the least convenient
instant it could pick.
"""

import os
import sys
import tempfile

JOKE = "My earbuds wait until I'm mid-sentence on a call to whisper 'battery low' — their one warning, timed perfectly to be useless."

# Inclusive bounds for one entry.
FLOOR_CHARS = 1
CEIL_CHARS = 200
LANDING_DIR = "/output"
LANDING_NAME = "entry.txt"


def validate(text):
    """Check a candidate entry and hand it back, or raise ValueError."""
    if text is None or not text.strip():
        raise ValueError("refusing to ship a blank entry")
    count = len(text)
    if count < FLOOR_CHARS or count > CEIL_CHARS:
        raise ValueError(
            "entry is %d characters; the window is %d..%d"
            % (count, FLOOR_CHARS, CEIL_CHARS)
        )
    return text


def _stage(text):
    """Spill text to a private temp file already set to 0644; return its path."""
    fd, path = tempfile.mkstemp(dir=LANDING_DIR, prefix=".entry-", suffix=".swap")
    os.fchmod(fd, 0o644)
    with os.fdopen(fd, "wb") as sink:
        sink.write(text.encode("utf-8"))
        sink.flush()
        os.fsync(sink.fileno())
    return path


def _promote(staged, final):
    """Rename the staged file into place and re-assert its permissions."""
    os.replace(staged, final)
    os.chmod(final, 0o644)


def main():
    entry = validate(JOKE)
    os.makedirs(LANDING_DIR, mode=0o755, exist_ok=True)
    os.chmod(LANDING_DIR, 0o755)
    staged = _stage(entry)
    try:
        _promote(staged, os.path.join(LANDING_DIR, LANDING_NAME))
    except BaseException:
        try:
            os.unlink(staged)
        except FileNotFoundError:
            pass
        raise
    print(len(entry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
