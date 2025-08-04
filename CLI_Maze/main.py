import curses
from game import MazeGame

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: MazeGame().play(stdscr))