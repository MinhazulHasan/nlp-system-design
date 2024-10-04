import hashlib


def hash_file(file):
    """Calculate the MD5 hash of a file."""
    md5_hash = hashlib.md5()
    for chunk in iter(lambda: file.read(8192), b""):
        md5_hash.update(chunk)
    file.seek(0)  # Reset file pointer to the beginning
    return md5_hash.hexdigest()
