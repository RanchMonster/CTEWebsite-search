import joblib
import atexit
from LogManager import *  # Assuming this is needed for logging

"""
Manages data caching, ensuring we don't retrain the model on every reload.
"""

cache = None  # Singleton instance

class CacheHandle:
    def __new__(cls):
        """Ensure only one instance exists (Singleton)."""
        global cache 
        if cache is None:
            instance = super().__new__(cls)
            cache = instance
        return cache 
    
    @classmethod
    def load(cls) -> 'CacheHandle':
        """Loads the cache from disk."""
        global cache 
        if cache is None:
            try:
                info("Attempting to load cache from disk")
                cache_data = joblib.load("cache.bin")
                instance = super().__new__(cls)
                for key, value in cache_data.items():
                    setattr(instance, key, value)
                cache = instance
                info("cache LOADED")
            except FileNotFoundError:
                instance = super().__new__(cls)
                cache = instance
                CacheHandle.unload()
        return cache

    @staticmethod
    def unload() -> None:
        """Saves the cache to disk."""
        global cache 
        if cache is not None:
            try:
                info("Saving cache to disk")
                cache_data = {k: v for k, v in cache.__dict__.items()}
                joblib.dump(cache_data, "cache.bin")
                info("cache successfully saved")
            except Exception as e:
                error(f"Error saving cache: {str(e)}")

    def add(self, key, value):
        """Adds a new immutable value (prevents modification of existing values)."""
        if hasattr(self, key):
            error(f"Attempted to modify existing key '{key}'")
            raise ValueError(f"Key '{key}' already exists. Cannot modify existing values.")
        value = frozenset([value]) if isinstance(value, set) else value
        setattr(self, key, value)
        debug(f"Added new key-value pair: {key}")

    def remove(self, key):
        """Removes a value from the cache."""
        if hasattr(self, key):
            debug(f"Removing key from cache: {key}")
            self.__dict__.pop(key)
        else:
            warning(f"Attempted to remove non-existent key: {key}")

    def get(self, key):
        """Retrieves a value but prevents direct modification."""
        value = getattr(self, key, None)
        if value is None:
            debug(f"cache miss for key: {key}")
        else:
            debug(f"cache hit for key: {key}")
        return value

    def __setattr__(self, name, value):
        """Prevents modifying existing values but allows adding new keys."""
        if hasattr(self, name):
            error(f"Attempted to modify existing key '{name}'")
            raise ValueError(f"Key '{name}' already exists. Cannot modify existing values.")
        object.__setattr__(self, name, value)

    def __setitem__(self, key, value):
        self.add(key, value)

    def __delattr__(self, name):
        """Allows deleting attributes from the map."""
        self.remove(name)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return hasattr(self, key)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)
def get_model():
    """
    Retrieves the trained model from cache.
    
    Returns:
        The trained model if available, None otherwise
    """
    cache = CacheHandle.load()
    if "model" in cache:
        return cache.model
    else:
        critical("No trained model stored please retrain")
        return None

# Ensure cache is saved on program exit
atexit.register(CacheHandle.unload)
