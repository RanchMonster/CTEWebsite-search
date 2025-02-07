import joblib
import atexit

"""
The purpose of this file is to manage model caching, ensuring that we don't have to retrain the model on every reload.

This script uses a dictionary (MAP) to store and load cached models from a binary file (Cache.bin).

"""

MAP = {}  # The memory map used to manage long-term variables

def load() -> None:
    """
    Loads the cached model from the binary file.
    
    :return: None
    """
    global MAP
    try:
        MAP = joblib.load("Cache.bin")
    except FileNotFoundError:
        print("No cache found. Please retrain the model and save it to continue caching.")
    finally:
        print("If you need to reset the model run the wipe to wipe the Cache i")
def unload() -> None:
    """
    Saves the current model state to the binary file.
    
    :return: None
    """
    global MAP
    try:
        joblib.dump(MAP, "Cache.bin")
    except Exception as e:
        print(f"Error saving cache: {str(e)}")
        
atexit.register(unload)