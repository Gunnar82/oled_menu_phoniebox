import os
def get_parent_folder(folder):
    return os.path.dirname(folder)

def has_subfolders(path):
    for file in os.listdir(path):
        d = os.path.join(path, file)
        if os.path.isdir(d):
            return True
    return False


def to_min_sec(seconds):
        mins = int(float(seconds) // 60)
        secs = int(float(seconds) - (mins*60))
        if mins >=60:
            hours = int(float(mins) // 60)
            mins = int(float(mins) - (hours*60))
            return "%d:%2.2d:%2.2d" % (hours,mins,secs)
        else:
            return "%2.2d:%2.2d" % (mins,secs)
