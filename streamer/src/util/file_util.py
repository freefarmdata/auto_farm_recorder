import psutil
import os


def file_is_being_accessed(file_path=None):
    ab_path = os.path.abspath(file_path)
    if os.path.exists(ab_path):
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    if ab_path == item.path:
                        return True
            except:
                pass
        return False