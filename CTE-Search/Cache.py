import joblib
import atexit
from LogManager import *  # Assuming this is needed for logging

"""
Manages data caching, ensuring we don't retrain the model on every reload.
"""

cache  = None  # Singleton instance

class CacheHandle:
    __map: dict

    def __new__(cls):
        """Ensure only one instance exists (Singleton)."""
        global cache 
        if cache  is None:
            instance = super().__new__(cls)
            instance.__map = {}
            cache  = instance
        return cache 
    
    @classmethod
    def load(cls) -> 'CacheHandle':
        """Loads the cache  from disk."""
        global cache 
        if cache  is None:
            try:
                info("Attempting to load cache  from disk")
                cache_data = joblib.load("cache .bin")
                instance = super().__new__(cls)
                instance.__map = cache_data
                cache  = instance
                info("cache  LOADED")
            except FileNotFoundError:
                error("No cache  found. Please retrain the model and save it to continue caching.")
        return cache 

    @staticmethod
    def unload() -> None:
        """Saves the cache  to disk."""
        global cache 
        if cache  is not None:
            try:
                info("Saving cache  to disk")
                joblib.dump(cache .__map, "cache .bin")  # Save only the dict
                info("cache  successfully saved")
            except Exception as e:
                error(f"Error saving cache : {str(e)}")

    def add(self, key, value):
        """Adds a new immutable value (prevents modification of existing values)."""
        if key in self.__map:
            error(f"Attempted to modify existing key '{key}'")
            raise ValueError(f"Key '{key}' already exists. Cannot modify existing values.")
        self.__map[key] = frozenset([value]) if isinstance(value, set) else value
        debug(f"Added new key-value pair: {key}")

    def remove(self, key):
        """Removes a value from the cache ."""
        if key in self.__map:
            debug(f"Removing key from cache : {key}")
            del self.__map[key]
        else:
            warning(f"Attempted to remove non-existent key: {key}")

    def get(self, key):
        """Retrieves a value but prevents direct modification."""
        value = self.__map.get(key)
        if value is None:
            debug(f"cache  miss for key: {key}")
        else:
            debug(f"cache  hit for key: {key}")
        return value

    def __setattr__(self, name, value):
        """Prevents modifying existing values but allows adding new keys."""
        if name in self.__dict__:  # Internal attributes
            object.__setattr__(self, name, value)
        else:
            self.add(name, value)

    def __delattr__(self, name):
        """Allows deleting attributes from the map."""
        self.remove(name)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return key in self.__map

# Ensure cache  is saved on program exit
atexit.register(CacheHandle.unload)
