from typing import TypedDict
from os import PathLike
# Define the basic data structures using TypedDict for type hinting
class PageData(TypedDict):
    """
    Represents structured data for web pages with their associated metadata.
    
    Attributes:
        url (str): The complete URL/location of the web page
        title (str): The title or heading of the web page
        content (str): The main textual content of the web page
        filters (list[str]): List of filter tags or categories applied to the page
    """
    url: str
    title: str
    content: str
    filters: list[str]

class FeedBack(TypedDict):
    """
    Stores user feedback data for search interactions and result relevance.
    
    Attributes:
        query (str): The search query entered by the user
        url (str): The URL of the page that was interacted with
        clicked (str): Indicates whether the user clicked on the result and found it relevant
    """
    query: str
    url: str
    clicked: str
class Setting:
    """Represents a configurable setting with name and value."""
    def __init__(self, name: str, value: str):
        """Initialize a setting.
        
        Args:
            name (str): Name of the setting
            value (str): Value of the setting
        """
        self.name = name
        self.value = value