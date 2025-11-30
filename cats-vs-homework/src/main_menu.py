"""
Last edited by Dietrich Geisler, November 2025

Main menu manager for Cats vs Homework game
"""

import tkinter as tk
from src.managers import GameManager
from src.contraptions import *
from src.cats import *

# Size of the entire window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

# The size of the difficulty frame
DIFFICULTY_HEIGHT = 100

# The size of the selection frame
SELECTION_HEIGHT = 100

# The list of contraptions for all of our game modes

CONTRAPTIONS = [lambda: LaserPointer(),
         lambda: BatteryCharger(),
         lambda: SnackDispenser(),
         lambda: BallThrower(),
         lambda: TripleLaserPointer(),
         lambda: ColorfulBallThrower(),
         lambda: SpaceHeater()]

def easy_game() -> GameManager:
    """
    Setup and run the GUI for the easy difficulty game
    """
    GameManager.initialize(
        3,
        CONTRAPTIONS,
        [lambda: Tabby(2), lambda: Tabby(4), lambda: Tabby(8)])
    return GameManager.manager()


def medium_game() -> GameManager:
    """
    Setup and run the GUI for the medium difficulty game
    """
    GameManager.initialize(
        4,
        CONTRAPTIONS,
        [lambda: Calico(2), lambda: Tabby(4), lambda: Calico(5), lambda: Tabby(6)])
    return GameManager.manager()


def hard_game() -> GameManager:
    """
    Setup and run the GUI for the hard difficulty game
    """
    GameManager.initialize(
        5,
        CONTRAPTIONS,
        [lambda: Tabby(2), lambda: Kitten(3), lambda: Calico(4), lambda: Tabby(6), lambda: Kitten(8)])
    return GameManager.manager()


class MainMenu:
    """
    Class to manage the MainMenu
    """

    root : tk.Tk
    """
    Root Tkinter window
    """

    _difficulty : int
    """
    The difficulty currently selected by the player
    """

    _play : bool
    """
    True if the player wants to play the game, False if the player wants to exit
    """

    _difficulty_buttons : list[tk.Button]
    """
    The list of difficulty buttons, maintained to have one selected
    """

    def __init__(self):
        self._choice = 0
        self._difficulty = 0
        self._play = False

        # Setup and run the main menu window
        self.root = tk.Tk()
        self.root.resizable(width=False, height=False)
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')

        difficulty = tk.Frame(self.root, height=DIFFICULTY_HEIGHT, width=WINDOW_WIDTH)
        selection = tk.Frame(self.root, height=SELECTION_HEIGHT, width=WINDOW_WIDTH)

        self._difficulty_buttons = []
        difficulty.pack(side=tk.TOP, expand=True)
        for index, text in enumerate(['Easy', 'Medium', 'Hard']):
            difficulty.grid_columnconfigure(index, minsize=WINDOW_WIDTH // 3)
            button = tk.Button(
                difficulty,
                bg='white',
                font=('consolas', 32, ''),
                text=text,
                # python is dumb
                command=lambda n=index: self._update_choice(n)
            )
            self._difficulty_buttons.append(button)
            button.grid(row=0, column=index)

        # Initially select difficulty 0
        self._difficulty = 0
        self._difficulty_buttons[0].config(bg='darkgray')

        selection.pack(side=tk.BOTTOM, expand=True)

        selection.grid_columnconfigure(0, minsize=WINDOW_WIDTH // 2)
        selection.grid_columnconfigure(1, minsize=WINDOW_WIDTH // 2)

        tk.Button(
            selection,
            bg='white',
            font=('consolas', 32, ''),
            text='Start',
            command=self._start_play
        ).grid(row=0, column=0)

        tk.Button(
            selection,
            bg='white',
            font=('consolas', 32, ''),
            text='Exit',
            command=self._exit
        ).grid(row=0, column=1)

    def _update_choice(self, choice : int):
        """
        Updates choice to a value between 0 and 2
        """
        assert isinstance(choice, int) and 0 <= choice <= 2
        # Makes the given button selected
        for index in range(3):
            button = self._difficulty_buttons[index]
            if index == choice:
                button.config(bg='darkgray')
            else:
                button.config(bg='white')
        self._choice = choice

    def _start_play(self):
        self._play = True
        self.root.destroy()

    def _exit(self):
        self._play = False
        self.root.destroy()

    def run(self):
        # Run the main menu until an option is selected
        # Returns "None" if exit is selected
        self.root.mainloop()
        if not self._play:
            return None
        if self._choice == 0:
            return easy_game()
        elif self._choice == 1:
            return medium_game()
        elif self._choice == 2:
            return hard_game()
        else:
            assert False, "Expected a choice in the range [0, 2]"
