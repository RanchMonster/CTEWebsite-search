from cli import Interface
import curses

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: Interface().run(stdscr))