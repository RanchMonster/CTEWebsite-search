from typing import TypedDict,Optional,Literal,Union
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
        clicked (int): Indicates whether the user clicked on the result and found it relevant
    """
    query: str
    url: str
    clicked: int
class SearchQuery(TypedDict):
    query:str
    filters:Optional[list[str]]
SETTING_TYPES = Literal["string","path","bool","int","float"]
class Setting:
    """Represents a configurable setting with name and value."""
    def __init__(self, name: str,type = SETTING_TYPES):
        """Initialize a setting.
        
        Args:
            name (str): Name of the setting
            value (str): Value of the setting
        """
        if type is SETTING_TYPES:
            raise TypeError(f"Invaild Type for setting {name}")
        self.name = name
        self.__type = type
        self.__value = self.__default()
    def __default(self):
        __type = self.type
        return __type()

    @property
    def value(self):
        if self.__type == "string" or self.__type == "path":
            return self.__value
        elif self.__type == "bool":
            try:
                return bool(int(self.__value))
            except:
                if self.__value.lower() == "true":
                    return True
                else:
                    return False
        elif self.__type == "int":
            return int(self.__value)
        else:
            return float(self.__value)
    @value.setter
    def value(self, new_value: str):
        if self.__type == "bool":
            try:
                bool(int(str(new_value)))
            except:
                if str(new_value).lower() not in ["true", "false"]:
                    raise ValueError(f"Invalid value for boolean setting {self.name}")
        elif self.__type == "int":
            try:
                int(str(new_value))
            except:
                raise ValueError(f"Invalid value for integer setting {self.name}")
        elif self.__type == "float":
            try:
                float(str(new_value))
            except:
                raise ValueError(f"Invalid value for float setting {self.name}")
        self.__value = str(new_value)
    @property
    def type(self):
        if self.__type == "string":
            return str
        elif self.__type == "path":
            return str
        elif self.__type == "bool":
            return bool
        elif self.__type == "int":
            return int
        elif self.__type == "float":
            return float