import curses
import asyncio
from typing import Optional

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
        self.options = ["hello world", "this kind of works", "does it though"]
        self.max_index = len(self.options) - 1

    def on_option(self, index):
        print(self.options[index])  # Can replace with menu navigation logic

class Interface:
    def __init__(self):
        self.index = 0
        self.current_menu = MainMenu()

    def __re_render(self, stdscr):
        self.current_menu(self.index, stdscr)

    async def __on_press(self, stdscr):
        loop = asyncio.get_event_loop()
        key = await loop.run_in_executor(None, stdscr.getch)

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

    async def __menu_loop(self, stdscr):
        self.__re_render(stdscr)
        while await self.__on_press(stdscr):
            await asyncio.sleep(0)  # Yield control

    async def run(self):
        await asyncio.to_thread(curses.wrapper, self.__menu_loop)

if __name__ == "__main__":
    asyncio.run(Interface().run())
