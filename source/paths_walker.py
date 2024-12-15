import glob
import os

def check_path(path):
    if not os.path.exists(path):
        return -1
    elif os.path.isdir(path):
        return 0
    elif os.path.isfile(path):
        return 1
    else:
        return -1

def get_filepaths(directory, pattern="*"):
    try:
        filepaths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return filepaths
    except OSError as e:
        print(e)
        return []

def get_all_filepaths(root_directory, pattern="*"):
    all_filepaths = []
    try:
        for dirpath, dirnames, filenames in os.walk(root_directory):
            filepaths = get_filepaths(dirpath, pattern)
            all_filepaths.extend(filepaths)
    except OSError as e:
        print(e)
        return []

    return all_filepaths


def get_file_tree(root_directory: str) -> dict:
    tree = {
        'path': root_directory,
        'files': [],
        'dirs': {}
    }

    try:
        items = os.listdir(root_directory)

        for item in items:
            full_path = os.path.join(root_directory, item)
            if os.path.isfile(full_path):
                tree['files'].append(full_path)
            elif os.path.isdir(full_path):
                tree['dirs'][item] = get_file_tree(full_path)
    except OSError as e:
        print(f"Error accessing {root_directory}: {e}")

    return tree