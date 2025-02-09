import curses
from typing import Optional
from threading import Thread,Lock
def clear():
    pass  # No need for clear, curses handles screen rendering

class Menu:
    options: list[str]
    max_index: int

    def __init__(self):
        raise NotImplementedError("Menu is an abstract class")

    def __call__(self, index: int, stdscr):
        for x in range(len(self.options)):
            if index == x:
                stdscr.addstr(f"{self.options[x]} <#####\n")
            else:
                stdscr.addstr(f"{self.options[x]}\n")

    def on_option(self, index: int) -> Optional['Menu']:
        raise NotImplementedError("Menu is an abstract class")

class MainMenu(Menu):
    def __init__(self):
        self.options = ["hello world", "this kind of works", "does it though"]
        self.max_index = len(self.options) - 1

    def on_option(self, index):
        return print(self.options[index])

class Interface:
    index: int
    current_menu: Menu
    def __init__(self):
        self.index = 0
        self.current_menu = MainMenu()

    def __re_render(self, stdscr):
        stdscr.clear()
        self.current_menu(self.index, stdscr)
        stdscr.refresh()

    def __on_press(self, stdscr):
        key = stdscr.getch()
        if key == curses.KEY_UP and self.index > 0:
            self.index -= 1
            self.__re_render(stdscr)
        elif key == curses.KEY_DOWN and self.index < self.current_menu.max_index:
            self.index += 1
            self.__re_render(stdscr)
        elif key == 10:  # Enter key (newline)
            menu = self.current_menu.on_option(self.index)
            if isinstance(menu, Menu):
                self.index = 0
                self.current_menu = menu
        elif key == 27:  # ESC key
            return False
        return True

    def run(self, stdscr):
        self.__re_render(stdscr)
        while True:
            if not self.__on_press(stdscr):
                break
