import curses
import asyncio
from typing import Optional
from LogManager import *
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

    def on_option(self, index: int) -> Optional['Menu']:
        raise NotImplementedError("Menu is an abstract class")

class MainMenu(Menu):
    def __init__(self):
        self.options = ["Model", "Logs", "Exit"]
        self.max_index = len(self.options) - 1

    def on_option(self, index):
        if index == self.max_index:
            exit(0)
        
class Interface:
    def __init__(self):
        self.index = 0
        self.current_menu = MainMenu()
        self.loop = asyncio.get_event_loop()  # Store event loop
        
    def __re_render(self, stdscr):
        self.current_menu(self.index, stdscr)

    async def __on_press(self, stdscr):
        key = stdscr.getch()
        if key != -1:

            if key == curses.KEY_UP and self.index > 0:
                self.index -= 1
            elif key == curses.KEY_DOWN and self.index < self.current_menu.max_index:
                self.index += 1
            elif key == 10:  # Enter key
                menu = self.current_menu.on_option(self.index)
                if isinstance(menu, Menu):
                    self.index = 0
                    self.current_menu = menu
            elif key == 27:  # ESC key
                return False

            self.__re_render(stdscr)
            return True
        else:
            return True

    def __menu_loop(self, stdscr):
        """Sync function to work with curses.wrapper()."""
        stdscr.nodelay(True)
        self.__re_render(stdscr)

        while True:
            future = asyncio.run_coroutine_threadsafe(self.__on_press(stdscr), self.loop)
            if not future.result():  # Wait for the coroutine to return and check result
                break
            curses.napms(50)  # Prevent high CPU usage
        exit(0)
    async def run(self):
        debug("Starting CLI")
        await asyncio.to_thread(curses.wrapper, self.__menu_loop)
