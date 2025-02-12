
import curses
import asyncio
from typing import Optional
from LogManager import *
from Cache import CacheHandle
from platform import platform
from DataTypes import Setting
from Server import start_server
async def get_text_input(stdscr, prompt: str) -> str:
        """Get text input from the user using curses.
        
        Args:
            stdscr: Curses screen object
            prompt: The prompt message to display
        
        Returns:
            str: The user input
        """
        curses.echo()  # Enable echoing of typed characters
        stdscr.clear()
        stdscr.addstr(prompt)
        stdscr.refresh()
    
        user_input = ''
        while True:
            key = stdscr.getch()
            if key == -1:
                continue
            if key == 10 or key == 13:  # Enter key (10 for Unix, 13 for Windows)
                break
            elif key == 27:  # ESC key
                user_input = ''
                break
            elif key in (curses.KEY_BACKSPACE, 8, 127):  # Backspace key (8 for Windows, 127 for Unix)
                if len(user_input) > 0:
                    user_input = user_input[:-1]
                    stdscr.clear()
                    stdscr.addstr(prompt + user_input)
                    stdscr.refresh()
                if len(user_input) ==0:
                    stdscr.clear()
                    stdscr.addstr(prompt + user_input)
                    stdscr.refresh()
            else:
                if chr(key).isascii():
                    user_input += chr(key)
                    stdscr.clear()
                    stdscr.addstr(prompt + user_input)
                    stdscr.refresh()
            await asyncio.sleep(0)

        curses.noecho()  # Disable echoing of typed characters
        return user_input
class Menu:
    """Abstract base class for menu implementations."""
    options: list[str]
    max_index: int

    def __init__(self):
        """Initialize the menu. This is an abstract class and should not be instantiated directly."""
        raise NotImplementedError("Menu is an abstract class")

    def __call__(self, index: int, stdscr):
        """Render the menu on the screen.
        
        Args:
            index (int): Currently selected menu item
            stdscr: Curses screen object
        """
        stdscr.clear()
        for x in range(len(self.options)):
            if index == x:
                stdscr.addstr(f"{self.options[x]} <#####\n")
            else:
                stdscr.addstr(f"{self.options[x]}\n")
        stdscr.refresh()

    async def on_option(self, index: int) -> Optional['Menu']:
        """Handle menu option selection. Must be implemented by subclasses.
        
        Args:
            index (int): Selected menu item index
            
        Returns:
            Optional[Menu]: New menu to display or None
        """
        raise NotImplementedError("Menu is an abstract class")



class SettingsMenu(Menu):
    """Menu for managing application settings."""
    def __init__(self):
        """Initialize settings menu with available options."""
        self.options = [*SettingsMenu.__load_settings(), "Back"]
        self.max_index = len(self.options) - 1

    async def on_option(self, index: int) -> Optional[Menu]:
        """Handle settings menu option selection.
        
        Args:
            index (int): Selected setting index
            
        Returns:
            Optional[Menu]: New menu to display or None
        """
        if self.options[index] == "Back":
            return MainMenu()
        
        # Using curses to get text input instead of aioconsole
        value = await get_text_input(self.stdscr, f"Enter the new value for {self.options[index].name}: ")
        
        self.options[index].value = value
        cache = CacheHandle.load()
        del cache.settings
        cache.settings = self.options[:-1]  # Exclude "Back" option
        debug(str(cache))
        return self

    @staticmethod
    def __load_settings() -> list[Setting]:
        """Load settings from cache or return defaults.
        
        Returns:
            list[Setting]: List of available settings
        """
        try:
            cache = CacheHandle.load()
            if "settings" in cache:
                return cache.settings
            return [
                Setting("ssl", "false"),
                Setting("address", "0.0.0.0"),
                Setting("port",""),
                Setting("cert", ""),
                Setting("key", "")
            ]
        except Exception as e:
            critical(str(e))

    def __call__(self, index: int, stdscr):
        """Render the settings menu.
        
        Args:
            index (int): Currently selected setting
            stdscr: Curses screen object
        """
        self.stdscr = stdscr
        stdscr.clear()
        for x in range(len(self.options)):
            if isinstance(self.options[x], Setting):
                item = f"{self.options[x].name}: {self.options[x].value}"
            else:
                item = self.options[x]
            if index == x:
                stdscr.addstr(f"{item} <#####\n")
            else:
                stdscr.addstr(f"{item}\n")
        stdscr.refresh()

    
class MainMenu(Menu):
    """Main application menu."""
    def __init__(self):
        """Initialize main menu with primary options."""
        self.options = ["Settings", "Start Server", "Exit"]
        self.max_index = len(self.options) - 1
        self.task = None
    async def on_option(self, index: int) -> Optional[Menu]:
        """Handle main menu option selection.
        
        Args:
            index (int): Selected option index
            
        Returns:
            Optional[Menu]: New menu to display or None
        """
        if index == 0:
            if self.task:
                self.stdscr.addstr("Please Stop Server before attempting to change settings")
                self.stdscr.refresh()
                await asyncio.sleep(1)
            else:
                return SettingsMenu()
        elif index == 1:
            await self.__toggle_server()

        elif index == 2:
            await asyncio.gather()
            exit(0)
            
        return None
    def __call__(self, index, stdscr):
        self.stdscr = stdscr
        return super().__call__(index, stdscr)
    async def __toggle_server(self):
        if self.task:
            self.options[1] = "Start Server"
            self.task.cancel()
            self.task = None
        else:
            self.options[1] = "Stop Server"
            self.task = asyncio.create_task(start_server())
class Interface:
    """Main interface controller handling menu navigation and input."""
    def __init__(self):
        """Initialize the interface with main menu."""
        self.index = 0
        self.current_menu = MainMenu()
        self.loop = asyncio.get_event_loop()
        self.stdscr = None

    def __re_render(self):
        """Refresh the current menu display."""
        self.current_menu(self.index, self.stdscr)

    async def __on_press(self) -> bool:
        """Handle keyboard input.
        
        Returns:
            bool: False if ESC pressed, True otherwise
        """
        key = self.stdscr.getch()
        if key != -1:
            if key == curses.KEY_UP and self.index > 0:
                self.index -= 1
            elif key == curses.KEY_DOWN and self.index < self.current_menu.max_index:
                self.index += 1
            elif key == 10 or key == 13:  # Enter key (10 for Unix, 13 for Windows)
                menu = await self.current_menu.on_option(self.index)
                if isinstance(menu, Menu):
                    self.index = 0
                    self.current_menu = menu
                self.stdscr.clear()
                self.__re_render()
                return True
            elif key == 27:  # ESC key
                await asyncio.gather()
                return False

            self.__re_render()
        return True

    def __menu_loop(self, stdscr):
        """Main menu loop handling rendering and input.
        
        Args:
            stdscr: Curses screen object
        """
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
        self.__re_render()

        while True:
            future = asyncio.run_coroutine_threadsafe(self.__on_press(), self.loop)
            if not future.result():
                break
            curses.napms(50)  # Prevent high CPU usage
        exit(0)

    async def run(self):
        """Start the interface."""
        debug("Starting CLI")
        await asyncio.to_thread(curses.wrapper, self.__menu_loop)
        debug("Closed CLI")