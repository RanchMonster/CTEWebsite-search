import curses
import asyncio
from LogManager import *
from Cache import CacheHandle, get_model
from DataTypes import Setting, PageData
from Server import start_server
import json

async def get_text_input(stdscr, prompt: str) -> str:
    curses.echo()
    stdscr.clear()
    stdscr.addstr(prompt)
    stdscr.refresh()
    
    user_input = ''
    while True:
        key = stdscr.getch()
        if key == -1:
            continue
        if key in (10, 13):  # Enter key
            break
        elif key == 27:  # ESC key
            user_input = ''
            break
        elif key in (curses.KEY_BACKSPACE, 8, 127):  # Backspace
            if user_input:
                user_input = user_input[:-1]
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

    curses.noecho()
    return user_input

class Menu:
    options: list[str]
    max_index: int

    def __init__(self):
        raise NotImplementedError("Menu is an abstract class")

    def __call__(self, index: int, stdscr):
        stdscr.clear()
        for x in range(len(self.options)):
            if index == x:
                stdscr.addstr(f"{self.options[x]} <#####\n")
            else:
                stdscr.addstr(f"{self.options[x]}\n")
        stdscr.refresh()

    async def on_option(self, index: int) -> object | None:
        raise NotImplementedError("Menu is an abstract class")

class ModelMenu(Menu):
    def __init__(self):
        self.options = ["Add Page", "Remove Page", "Back"]
        self.max_index = len(self.options) - 1

    async def on_option(self, index: int) -> Menu | None | int:
        if index == 0:
            model = get_model()
            new_page: PageData = {}
            new_page["title"] = await get_text_input(self.stdscr, "Enter Page Title: ")
            new_page["content"] = await get_text_input(self.stdscr, "Enter Page Content: ")
            new_page["filters"] = []
            filter_input = await get_text_input(self.stdscr, "Enter a filter (leave blank to finish): ")
            while filter_input:
                new_page["filters"].append(filter_input)
                filter_input = await get_text_input(self.stdscr, "Enter a filter (leave blank to finish): ")
            new_page["url"] = await get_text_input(self.stdscr, "Enter the URL local to the server (e.g., /home): ")
            model.append_page_data(new_page)
        elif index == 1:
            pass  # TODO: Implement page removal
        elif index == self.max_index:
            return -1
        else:
            return None

    def __call__(self, index: int, stdscr):
        self.stdscr = stdscr
        return super().__call__(index, stdscr)

class SettingsMenu(Menu):
    def __init__(self):
        self.options = [*SettingsMenu.__load_settings(), "Back"]
        self.max_index = len(self.options) - 1

    async def on_option(self, index: int) -> Menu | int | None:
        if self.options[index] == "Back":
            return -1

        setting: Setting = self.options[index]
        try:
            setting.value = await get_text_input(self.stdscr, f"Enter new value for {setting.name}: ")
        except Exception as e:
            error(str(e))
            self.stdscr.addstr(str(e))
            self.stdscr.refresh()
        self.options[index] = setting
        cache = CacheHandle.load()
        cache.settings = self.options[:-1]
        debug(str(cache))
        
    @staticmethod
    def __load_settings() -> list[Setting]:
        try:
            cache = CacheHandle.load()
            return cache.settings
        except Exception as e:
            critical(str(e))
            return []
    def __call__(self, index: int, stdscr):
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

class MainMenu(Menu):
    """Main application menu."""
    def __init__(self):
        """Initialize main menu with primary options."""
        self.options = ["Settings", "Start Server","Model", "Exit"]
        self.max_index = len(self.options) - 1
        self.task = None
    async def on_option(self, index: int) -> Menu | None:
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
            return ModelMenu()
        else:
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
            while self.task.cancelled():
                asyncio.sleep(0)
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
        self.menu_path = []
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
                    self.menu_path.append(self.current_menu)
                    self.current_menu = menu
                elif menu == -1:
                    if len(self.menu_path) >0:
                        self. current_menu =self.menu_path.pop()
                        self.index = 0
                    else:
                        return False
            elif key == 27:  # ESC key
                if len(self.menu_path) >0:
                    self. current_menu =self.menu_path.pop()
                    self.index = 0
                else:
                    return False
            self.stdscr.clear()
            self.__re_render()
        else:
            pass
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
        debug("Starting CLI")
        await asyncio.to_thread(curses.wrapper, self.__menu_loop)
        debug("Closed CLI")
    
