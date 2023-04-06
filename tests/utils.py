from pathlib import Path

def file_count(path: str) -> int:
    """ Returns the number of files in a folder. """
    return len([file_path for file_path in Path(path).iterdir() if file_path.is_file()])