import hashlib
import os


def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files. This is, files with
    extension ".png", ".jpg", ".jpeg" or ".gif".

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    # Guard: must be a non-empty string
    if not filename or not isinstance(filename, str):
        return False

    # Extract the basename to ignore any directory components
    base = os.path.basename(filename)
    if not base:
        return False

    # If the basename ends with a dot (e.g. 'dog.'), treat as no extension
    if base.endswith('.'):
        return False

    # Split extension and check against allowed set (case-insensitive)
    _, ext = os.path.splitext(base)
    if not ext:
        return False

    allowed_ext = {'.png', '.jpg', '.jpeg', '.gif'}
    return ext.lower() in allowed_ext


async def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """
    # Read file-like object in chunks to compute md5 without loading everything
    hasher = hashlib.md5()

    # Some UploadFile implementations expose the underlying file as `.file`
    fp = getattr(file, "file", None) or file

    # Ensure we start from the beginning
    try:
        fp.seek(0)
    except Exception:
        pass

    # Read in chunks
    chunk_size = 8192
    while True:
        chunk = fp.read(chunk_size)
        if not chunk:
            break
        # If chunk is str (unlikely), encode it
        if isinstance(chunk, str):
            chunk = chunk.encode()
        hasher.update(chunk)

    # Reset file pointer to beginning for downstream consumers
    try:
        fp.seek(0)
    except Exception:
        pass

    # Preserve the original extension (lowercased)
    _, ext = os.path.splitext(getattr(file, 'filename', '') or '')
    ext = ext.lower() if ext else ''

    return hasher.hexdigest() + ext
