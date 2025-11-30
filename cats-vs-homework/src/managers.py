"""
Last edited by Dietrich Geisler, May 2025

Core class definitions for Cats vs. Homework
"""

import pathlib
import tkinter as tk
from typing import Callable, TYPE_CHECKING

# Ridiculous code to provide correct type annotations
if TYPE_CHECKING:
    from src.cats import Cat
    from src.contraptions import Contraption

# The overall sizes of the game window, kept as a constant
WINDOW_WIDTH = 1250
WINDOW_HEIGHT = 700

# The height of the board within the game window
BOARD_HEIGHT = 550

# The size of a single tile "button"
TILE_WIDTH = 100
TILE_HEIGHT = 100

# The amount of width allocated for information (end turn/batteries)\
INFO_WIDTH = 200

# The number of tiles in a "lane"
LANE_WIDTH = 8

# A list of all images by name
ACTOR_IMAGE_NAMES = [
    'calico',
    'charger',
    'colorful_ball',
    'colorful_thrower',
    'empty',
    'heater',
    'kitten',
    'laser',
    'triple_laser',
    'snacks',
    'tabby',
    'thrower',
]

# starting batteries
STARTING_BATTERIES = 8

# How many rounds until the game ends
WIN_ROUND = 40

# --------------------------------
# A bunch of background classes that manage the game logic
# You shouldn't need to work with these directly


class GameManager:
    """
    Manages the game state and holds constant image references
    """

    _instance: 'GameManager | None' = None
    """
    There is exactly one instance of GameManager that is globally accessible
    We use the Singleton design pattern to enforce this
    """

    _root: tk.Tk
    """
    The root of the drawn game window
    """

    _board: 'Board'
    """
    The frame and container for the game board
    """

    _selection_manager: 'SelectionManager'
    """
    The frame and container for the contraption selector
    """

    _actor_images: dict[str, tk.PhotoImage]
    """
    The dictionary of all images used for constructing units (public)
    We use the name of the image as an access to avoid reloading images
    """

    _batteries: int
    """
    The number of batteries the player has
    """

    _rounds: int
    """
    How many rounds have passed
    """

    _contraptions: list['Contraption']
    """
    A list of all the contraptions currently on the board
    """

    _cats: list['Cat']
    """
    A list of all the cats in the game
    """

    _game_ended: bool
    """
    Whether or not the game has ended
    """

    def initialize(lane_count: list['Tile'],
                   contraptions: list['Contraption'],
                   cats: list['Cat']):
        """Sets up the (unique) GameManager with a window at the root

        Constructs a game board with the number of given 'lanes',
          the provided list of contraptions that can be build
          and the provided list of initialized cats
        """
        # Checks on the provided parameters
        assert isinstance(lane_count, int)
        assert isinstance(contraptions, list)
        assert isinstance(cats, list)

        # Assert we haven't yet been initialized and then initialize
        assert not GameManager.is_initialized()
        singleton = GameManager()
        GameManager._instance = singleton

        # Setup the root of the window
        root = tk.Tk()
        root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        root.resizable(width=False, height=False)
        singleton._root = root

        # Read images into the dictionary
        actor_images = {}
        for image_name in ACTOR_IMAGE_NAMES:
            path = pathlib.Path('resources') / \
                pathlib.Path(f'{image_name}.png')
            actor_images[image_name] = tk.PhotoImage(file=path)
        singleton._actor_images = actor_images

        singleton._batteries = STARTING_BATTERIES
        singleton._rounds = 0

        # construct the selection manager
        singleton._selection_manager = SelectionManager(
            contraptions, singleton.batteries())

        # construct a board
        singleton._board = Board(lane_count)

        # keep track of all the contraptions on the board
        # this list needs to be updated when a contraption is removed
        singleton._contraptions = []

        # initialize all of the cats
        singleton._cats = []
        for cat in cats:
            singleton._cats.append(cat())
        singleton.update_attentions()

        singleton._game_ended = False

    def is_initialized() -> bool:
        """
        Returns true if a singleton instance of GameManager has been initialized
        """
        return GameManager._instance is not None

    def manager() -> 'GameManager':
        """Gets the unique GameManager
        Requires that such a GameManager exist
        """
        assert GameManager.is_initialized()
        return GameManager._instance

    def destroy():
        """Destroys the singleton instance of GameManager
        Requires that such an instance exist
        """
        assert GameManager.is_initialized()
        GameManager._instance._root.destroy()
        GameManager._instance._game_ended = True
        GameManager._instance = None

    def root(self) -> tk.Tk:
        """
        Returns a reference to the root tkinter container
        """
        return self._root

    def selection_manager(self) -> 'SelectionManager':
        """
        Returns a reference to the selection manager used by this game
        """
        return self._selection_manager

    def board(self) -> 'Board':
        """
        Returns a reference to the board used by this game
        """
        return self._board

    def get_empty_image(self) -> tk.PhotoImage:
        """
        Returns the empty tile image
        """
        return self.get_actor_image('empty')

    def get_actor_image(self, image_name: str) -> tk.PhotoImage:
        """Returns the image associated with the given string name
        Requires that the provided image_name be in our list of IMAGE_NAMES
        """
        assert isinstance(image_name, str)
        assert image_name in ACTOR_IMAGE_NAMES
        return self._actor_images[image_name]

    def batteries(self) -> int:
        """
        Returns the number of batteries we currently have
        """
        return self._batteries

    def spend_batteries(self, amount: int):
        """
        Removes the non-negative 'amount' of batteries from this game
        Requires that we have at least as many batteries as 'amount'
        """
        assert amount >= 0 and self._batteries >= amount
        self._batteries -= amount
        self._selection_manager.update_battery_text(self._batteries)

    def add_contraption(self, contraption: 'Contraption'):
        """
        Adds the given contraption to the list of contraptions on the board
        """
        # Trick to allow the name Contraption without a circular import
        from src.contraptions import Contraption

        assert isinstance(contraption, Contraption)
        self._contraptions.append(contraption)

    def remove_contraption(self, contraption: 'Contraption'):
        """
        Removes the given contraption (by ID) from the board
        If no such contraption exists, this function will error
        """
        # Trick to allow the name Contraption without a circular import
        from src.contraptions import Contraption

        assert isinstance(contraption, Contraption)
        self._contraptions.remove(contraption)

    def increment_round(self):
        """Increases the number of rounds by one
        If we've reached WIN_ROUNDS, end the game in a win
        """
        self._rounds += 1
        self._selection_manager.update_round_text(self._rounds)
        if self._rounds >= WIN_ROUND:
            self.win_game()

    def add_batteries(self, amount: int):
        """
        Adds the non-negative 'amount' of batteries to this game
        """
        assert isinstance(amount, int) and amount >= 0
        self._batteries += amount
        self._selection_manager.update_battery_text(self._batteries)

    def update_attentions(self):
        """
        Updates the attention display of all cats
        """
        attentions = [cat.attention() for cat in self._cats]
        self._selection_manager.update_attention_text(attentions)

    def end_round(self):
        """
        Ends the current player turn and takes cat/contraption actions
        """
        self.add_batteries(1)
        for contraption in self._contraptions:
            contraption.end_round()
        for cat in self._cats:
            cat.end_round()
            # if the game ended when this cat moved
            if (self._game_ended):
                return
        self.update_attentions()
        self.increment_round()  # may end the game

    def lose_game(self):
        """
        Ends the game in a loss
        """
        print("You lose!")
        GameManager.destroy()

    def win_game(self):
        """
        Ends the game with a win
        """
        print("You win!")
        GameManager.destroy()


class SelectionManager:
    """
    Manages the player's ability to select a Contraption
    """

    _frame: tk.Frame
    """
    The TKinter frame on which we draw the lanes of the board
    """

    _selector_frame: tk.Frame
    """
    The TKinter frame on which we draw selector buttons
    """

    _information_frame: tk.Frame
    """
    The TKinter frame on which we draw battery information and the end turn button
    """

    _battery_text: tk.Label
    """
    Label indicating the number of batteries
    """

    _round_text: tk.Label
    """
    Label indicating the number of Rounds that have passed
    """

    _end_turn: tk.Button
    """
    Button used to end the player turn
    """

    _selectors: list['Selector']
    """
    Ordered list of selectors that the player can interact with
    Strictly speaking, this need not be stored, but that feels wrong to just drop
    """

    _current_selector: 'Selector'
    """
    The currently clicked selector, which holds the selected contraption
    If no selector is clicked or after placing a contraption, then this can be None
    """

    def __init__(self,
                 contraptions: list['Contraption'],
                 batteries: int):
        """Constructs a selector from the provided (ordered) list of contraptions
        Also must be provided a (non-negative) number of starting batteries
        The allowed contraptions may depend on the specific game
        """
        assert isinstance(batteries, int) and batteries >= 0
        assert isinstance(contraptions, list)

        # Setup the frames
        frame = tk.Frame(
            GameManager.manager().root(),
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT - BOARD_HEIGHT)
        self._frame = frame

        frame.pack(side=tk.TOP)

        selector_frame = tk.Frame(frame,
                                  width=WINDOW_WIDTH - INFO_WIDTH)
        self._selector_frame = selector_frame

        information_frame = tk.Frame(frame,
                                     width=INFO_WIDTH)
        self._information_frame = information_frame

        attention_frame = tk.Frame(frame,
                                   width=INFO_WIDTH)

        selector_frame.place(relx=0, rely=0.5, relheight=1.0, anchor=tk.W)
        information_frame.place(relx=1.0, rely=0.5, relheight=1.0, anchor=tk.E)
        attention_frame.place(relx=0.72, rely=0, relheight=1.0, anchor=tk.N)

        # Setup the selectors
        self._selector = []
        for column, contraption in enumerate(contraptions):
            self._selector.append(
                Selector(selector_frame, contraption, column))
        self._current_selector = None

        # Setup the attention text
        attention_text = tk.Label(
            attention_frame, font=('consolas', 22, ''), text=f'')
        attention_text.pack()
        self._attention_text = attention_text

        # Setup the end turn button
        end_turn = tk.Button(
            information_frame,
            bg='white',
            font=('consolas', 22, ''),
            command=self._end_turn_clicked,
            text='End Turn'
        )
        self._end_turn = end_turn
        end_turn.pack()

        # Setup the battery and round texts
        self._battery_text = tk.Label(
            information_frame, font=('consolas', 22, ''))
        self.update_battery_text(batteries)
        self._battery_text.pack()
        self._round_text = tk.Label(
            information_frame, font=('consolas', 22, ''))
        self.update_round_text(0)
        self._round_text.pack()

    def frame(self) -> tk.Frame:
        """
        Returns the frame on which this selection manager is displayed
        """
        return self._frame

    def get_current_contraption(self) -> 'Contraption | None':
        """
        Returns the currently selected Contraption if one is selected
        """
        if self._current_selector is None:
            return None
        return self._current_selector.contraption()

    def get_current_constructor(self) -> 'Contraption | None':
        """
        Returns the currently selected Contraption constructor if one is selected
        """
        if self._current_selector is None:
            return None
        return self._current_selector.constructor()

    def set_current_selector(self, selector: 'Selector'):
        """
        Updates the current selector to the given selector
        """
        if self._current_selector is not None:
            self._current_selector.deselect()
        self._current_selector = selector
        selector.select()

    def clear_current_selector(self):
        """
        Clears any selected contraption
        """
        if self._current_selector is not None:
            self._current_selector.deselect()
        self._current_selector = None

    def update_round_text(self, round: int):
        """
        Updates the number of rounds displayed to the user
        The round number is validated to be positive
        """
        assert isinstance(round, int) and round >= 0
        self._round_text.config(text=f'Round: {round}')

    def update_battery_text(self, batteries: int):
        """
        Updates the number of batteries displayed to the user
        The number of batteries are validated to be positive
        """
        assert isinstance(batteries, int) and batteries >= 0
        self._battery_text.config(text=f'Batteries: {batteries}')

    def _end_turn_clicked(self):
        """
        The event triggered when the end-of-turn button is clicked
        """
        self.clear_current_selector()
        GameManager.manager().end_round()

    def update_attention_text(self, attentions: list[int]):
        """
        Updates the list of attention per-Cat
        Concretely, this list of attention spans must be already formatted as an int
        """
        assert isinstance(attentions, list)
        text = 'Cat Attentions:\n'
        for attention in attentions:
            assert isinstance(attention, int)
            if attention == 0:
                text += f'R '
            else:
                text += f'{attention} '
        self._attention_text.config(text=text)


class Selector:
    """
    Manages a specific contraption selection the player can make
    """

    _contraption: 'Contraption'
    """
    The read-only contraption associated with this Selector
    """

    _constructor: Callable[[], 'Contraption']
    """
    The contraption constructor expression associated with this Selector
    """

    _button: tk.Button
    """
    The Tkinter button the player can interact with to select a contraption
    """

    _selected: bool
    """
    Whether or not this selector is currently selected by the player
    """

    def __init__(self,
                 frame: tk.Frame,
                 constructor: Callable[[], 'Contraption'],
                 column: int):
        """
        Builds a selector for the given contraption on the given frame
        """
        assert isinstance(frame, tk.Frame)
        assert isinstance(column, int)

        self._constructor = constructor
        contraption = constructor()
        # Trick to allow the name Contraption without a circular import
        from src.contraptions import Contraption

        assert isinstance(contraption, Contraption)

        self._contraption = contraption
        button = tk.Button(
            frame,
            bg='white',
            width=TILE_WIDTH,
            height=TILE_HEIGHT,
            command=self._clicked,
            # start with the empty image
            image=contraption.image(),
        )
        label = tk.Label(frame, font=('consolas', 16, ''),
                         text=f'Cost {contraption.cost()}')
        self._button = button
        button.grid(row=0, column=column)
        label.grid(row=1, column=column)

    def contraption(self) -> 'Contraption':
        """
        Returns the contraption associated with this Selector
        """
        return self._contraption

    def constructor(self) -> Callable[[], 'Contraption']:
        """
        Returns the contraption constructor associated with this Selector
        """
        return self._constructor

    def selected(self) -> bool:
        """
        Returns true if this Selector is selected
        """
        return self._selected

    def select(self):
        """
        Selects this selector, which changes the button color
        """
        self._selected = True
        self._button.config(bg='darkgray')

    def deselect(self):
        """
        Removes the selection from this selector, which changes the button color
        """
        self._selected = False
        self._button.config(bg='white')

    def _clicked(self):
        """
        Called when this button is pressed
        The selection manager handles calling `select()` on this object
        """
        GameManager.manager().selection_manager().set_current_selector(self)


class Board:
    """
    Manages the geometry of the game board
    """

    _frame: tk.Frame
    """
    The TKinter frame on which we draw the lanes of the board
    """

    _lanes: list['Tile']
    """
    The entry tile for each lane from the perspective of the cats
    """

    _attention_text: tk.Label
    """
    The Label listing the attention spans of each cat
    """

    def __init__(self, lane_count: int):
        # Construct and assign the frame
        frame = tk.Frame(
            GameManager.manager().root(),
            width=WINDOW_WIDTH,
            height=BOARD_HEIGHT)
        self._frame = frame

        # Center the main frame on the root
        frame.pack(side=tk.TOP, expand=True)

        # Setup lanes along the window
        # Each tile constructs their own buttons
        self._lanes = []
        previous_row = []  # for building up "above" and "below" in each tile
        for row in range(lane_count):
            above = None if row == 0 else previous_row[0]
            next = Tile(frame, above=above)
            next.align(row, 0)
            current_row = [next]
            # Subtract one to account for the head already being made
            for column in range(1, LANE_WIDTH):
                above = None if row == 0 else previous_row[column]
                next = Tile(frame, next, above)
                next.align(row, column)
                current_row.append(next)
            previous_row = current_row
            # Add the head we created to lanes
            self._lanes.append(next)

    def __repr__(self) -> str:
        """
        Returns the basic debugging representation of this Board
        """
        return f'{self.__class__.__name__} : {vars(self)}'

    def get_lane_count(self) -> int:
        """
        Returns the number of lanes in this game
        """
        return len(self._lanes)

    def get_lane_entrance(self, index: int) -> 'Tile':
        """
        Returns the entrance tile of the given in-bounds lane index
        """
        return self._lanes[index]

    def frame(self) -> tk.Frame:
        """
        Returns a reference to the main frame on which we draw
        """
        return self._frame

# --------------------------------
# NOTE: The classes you'll be directly interacting with


class Tile:
    """
    Holds information for a single tile on the board
    Each tile can hold exactly one actor, and may have a successor and predecessor
    """

    _button: tk.Button
    """
    The Tkinter button used to interact with this Tile (e.g. to place a contraption)
    """

    _actor: 'Actor'
    """
    The Actor contained in this Tile
    Only one Actor can be on a tile at once
    """

    _entrance: 'Tile | None'
    """
    The Tile _entrance_ from this particular board tile.  
    Visually this is the Tile to the right of this Tile
    """

    _exit: 'Tile | None'
    """
    The Tile _exit_ from this particular board tile.  
    Visually this is the Tile left of this Tile
    """

    _above: 'Tile | None'
    """
    The Tile in the lane directly above this particular board tile.
    """

    _below: 'Tile | None'
    """
    The Tile in the lane directly below this particular board tile. 
    """

    def __init__(self, frame: tk.Frame, exit: 'Tile | None' = None, above:  'Tile | None' = None):
        """
        Initializes a tile with a given frame to attach to
          along with an (optional) tile entrance and tile above this tile
        We choose to restrict constructing a tile with an explicit exit
        Instead, adding a tile as an entrance will update the provided tile's exit
        """
        assert isinstance(frame, tk.Frame)
        assert (exit is None) or isinstance(exit, Tile)
        assert (above is None) or isinstance(above, Tile)

        # constant-size buttons for the tiles
        self._button = tk.Button(
            frame,
            bg='white',
            width=TILE_WIDTH,
            height=TILE_HEIGHT,
            command=self._clicked,
            # start with the empty image
            image=GameManager.manager().get_empty_image())

        self._actor = None
        self._entrance = None
        self._exit = exit
        self._above = above
        self._below = None

        # Update the link for the entrance
        if exit is not None:
            exit._entrance = self

        # Update the link for the tile above this one
        if above is not None:
            above._below = self

    def __repr__(self) -> str:
        """
        Returns the string representation of this Tile
        Includes the tile row and column information of this Tile
        """
        board: 'Board' = GameManager.manager().board()
        location = (-1, -1)
        row = 0
        while row < board.get_lane_count():
            column = 0
            current: 'Tile' = board.get_lane_entrance(row)
            while current is not None:
                if current == self:
                    location = (row, column)
                current = current.exit()
                column += 1
            row += 1
        value_at = f'is empty' if self._actor is None else f'contains {self._actor}'
        return f'Tile at {location} {value_at}'

    def align(self, row: int, column: int):
        """
        Packs this tile into the board along the specified alignment
        """
        self._button.grid(row=row, column=column)

    def _clicked(self):
        """
        The function called when this tile is clicked
        """
        manager = GameManager.manager()
        selected = manager.selection_manager().get_current_contraption()
        if selected is None:
            return

        # We can't build a contraption on the "entrance" to a lane or an occupied Tile
        can_build = self.entrance() is not None and self.is_empty()
        # We also can only build a contraption if we can afford it
        can_build = can_build and selected.cost() <= manager.batteries()
        if can_build:
            manager.spend_batteries(selected.cost())

            # a bunch of silliness to construct a new contraption and place it
            constructor = manager.selection_manager().get_current_constructor()
            new_contraption = constructor()
            manager.selection_manager().clear_current_selector()

            new_contraption.place(self)  # semi-evil reference trickery

    def _set_image(self, image: tk.PhotoImage):
        """
        An internal helper function to set the image displayed by this tile
        """
        assert (isinstance(image, tk.PhotoImage))
        self._button.config(image=image)

    def entrance(self) -> 'Tile | None':
        """
        Returns a reference to the tile that _enters_ this tile in the lane
          (from the perspective of the cats, so the Tile to the 'right' of this Tile
        Returns None if no such tile exists
        """
        return self._entrance

    def exit(self) -> 'Tile | None':
        """
        Returns a reference to the tile that is the _exit_ from this tile
          (from the perspective of the cats, so the Tile to the 'right' of this Tile
        Returns None if no such tile exists
        """
        return self._exit

    def above(self) -> 'Tile | None':
        """
        Returns a reference to the tile that is directly above this tile
          That is, the Tile in the same column as this tile, but in self.lane() - 1
        Returns None if no such tile exists
        """
        return self._above

    def below(self) -> 'Tile | None':
        """
        Returns a reference to the tile that is directly below this tile
          That is, the Tile in the same column as this tile, but in self.lane() - 1
        Returns None if no such tile exists
        """
        return self._below

    def actor(self) -> 'Actor | None':
        """Returns a reference to the actor in this tile if one exists
        Returns None if no such actor exists
        """
        return self._actor

    def is_empty(self) -> bool:
        """Returns True if this tile is empty, that is, it does not contain an actor
        Returns False if this Tile contains an actor
        """
        return self._actor is None

    def set_actor(self, actor: 'Actor'):
        """Updates this tile to contain a new actor
        This tile must not have an actor to take on a new actor
        """
        assert self.is_empty()
        assert isinstance(actor, Actor)
        self._actor = actor
        self._set_image(actor.image())

    def clear_actor(self):
        """Clears the Actor from this tile

        If this does not Tile contain an Actor, raises an Error

        This should be called when an Actor is moved to another tile
          or when it is removed from the game
        """
        assert not self.is_empty()
        self._actor = None
        self._set_image(GameManager.manager().get_empty_image())


class Actor:
    """Holds information about a single Actor
    Every Actor has an associated image
    """

    _image: tk.PhotoImage
    """
    The (constant) image associated with this Actor
    """

    _tile: 'Tile | None'
    """
    The Tile that this Actor is on within the game board
    If this Actor is not on the Board, this will be None
    """

    def __init__(self, image_name: str):
        """
        Requires the name of a valid image and a GameManager to setup an actor
        """
        assert isinstance(image_name, str)
        self._image = GameManager.manager().get_actor_image(image_name)
        self._tile = None

    def __repr__(self) -> str:
        """
        Returns the basic debugging representation of this Actor
        """
        return f'{self.__class__.__name__}'

    def image(self) -> tk.PhotoImage:
        """
        Returns the image associated with this actor
        """
        return self._image

    def tile(self) -> 'Tile':
        """
        Returns the tile of the board this Actor is on
        """
        assert self.is_on_board()
        return self._tile

    def is_on_board(self) -> bool:
        """
        Returns whether or not this Actor is on the board
        """
        return self._tile is not None

    def remove_from_board(self):
        """
        Removes this Actor from the board
        """
        self._tile.clear_actor()
        self._tile = None

    def teleport(self, tile: Tile):
        """Teleports this Actor to the given tile
        Explicitly avoids invoking any sort of movement logic
        Intended primarily for testing
        """
        assert isinstance(tile, Tile)
        if self.is_on_board():
            self._tile.clear_actor()
        self._tile = tile
        tile.set_actor(self)
