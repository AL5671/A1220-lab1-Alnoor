# file_io.py
import os
import base64

def encode_file(path):
    """Read a file as bytes and return its base64-encoded contents.

    Args:
        path: Path to the file to encode.

    Returns:
        A base64-encoded string of the file contents (UTF-8 text).
    """
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def list_files(dirpath):
    """Yield (filename, filepath) pairs for regular files in a directory.

    Args:
        dirpath: Path to a directory to scan.

    Yields:
        Tuples of (name, path) for each file directly inside the directory.
    """
    for name in os.listdir(dirpath):
        path = os.path.join(dirpath, name)
        if os.path.isfile(path):
            yield name, path

