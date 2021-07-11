import os
def get_parent_folder(folder):
    return os.path.dirname(folder)

def has_subfolders(path):
    for file in os.listdir(path):
        d = os.path.join(path, file)
        if os.path.isdir(d):
            return True
    return False
