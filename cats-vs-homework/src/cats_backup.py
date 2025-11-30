"""
Author: Abdoul Rahim Ousseini
Starting Date: November 17, 2025

Cat implementations for the game - different types of cats that try to distract my roommate
"""

import random  # for placing cats
from typing import TYPE_CHECKING
from src.managers import GameManager, Actor


class Cat(Actor):
    """
    Base class that represents all cats
    """

    _starting_attention: int
    """
    Starting attention of this Cat when entering the board
    """

    _attention: int
    """
    The current attention of this Cat
    If attention reaches zero, this Cat becomes distracted
      and is removed from the board
    If this Cat is not on the board, this value will always be zero
    """

    _needed_rest_time: int
    """
    How many turns this cat needs to rest after becoming distracted
    """

    _rest_time: int
    """
    How long until this cat returns to the board
      If this cat is on the board, this value will always be zero
    """

    def __init__(self,
                 image_name: str,
                 starting_attention: int,
                 needed_rest_time: int,
                 starting_rest_time: int):
        """
        Initializes this cat with the given attention and rest times

        Note that "needed_rest_time" must be greater than or equal to 1
            (a cat must rest at least one round)

        Note that we also must provide a distinct "starting rest time"
          to indicate how many rounds this cat rests
          before initially entering the board
          (this value can be larger than rest_time)
        """
        super().__init__(image_name)
        assert isinstance(starting_attention, int) and starting_attention >= 0
        assert isinstance(needed_rest_time, int) and needed_rest_time >= 1
        assert isinstance(starting_rest_time, int) and starting_rest_time >= 0

        self._attention = 0
        self._starting_attention = starting_attention
        self._needed_rest_time = needed_rest_time
        self._rest_time = starting_rest_time

    def __repr__(self) -> str:
        """
        Returns the basic debugging representation of this Cat
        """
        return f'{self.__class__.__name__}(attention={self._attention}, rest_time={self._rest_time})'

    def attention(self) -> int:
        """
        Returns the current attention of this Cat
        """
        return self._attention

    def rest_time(self) -> int:
        """
        Returns how long this cat needs to rest
        """
        return self._rest_time

    def end_round(self):
        """
        Runs the behavior of this cat for the end of the round
        If this cat is on the board, move forward
        Otherwise, this cat rests and possibly is placed on the board
        """
        if self.is_on_board():
            self.move()
        else:
            self.rest()

    def move(self):
        """
        Moves this Cat forward, if able
        If there is a contraption in the way, 
          instead "interact" with the contraption
        """
        from src.contraptions import Contraption, ColorfulBall, SpaceHeater

        # check if we reached the end - game over if so
        if self.tile().exit() is None:
            GameManager.manager().lose_game()
            return

        next_spot = self.tile().exit()
        
        # check if there's a colorful ball - pick it up and move there
        if isinstance(next_spot.actor(), ColorfulBall):
            next_spot.clear_actor()  # pick up the ball
            self.teleport(next_spot)
            self.distract(1)  # get distracted by the ball
            self._check_space_heater()
            return
        
        # if next spot is empty, just move there
        if next_spot.is_empty():
            self.teleport(next_spot)
            self._check_space_heater()
            return
        
        # if there's a contraption, interact with it
        if isinstance(next_spot.actor(), Contraption):
            next_spot.actor().interact()
            return
        
        # otherwise there's another cat blocking, so do nothing

    def _check_space_heater(self):
        """Check if there's a space heater nearby and get distracted"""
        from src.contraptions import SpaceHeater
        
        # need to check tiles within range 2 in all directions
        # this includes same row, row above, and row below
        
        # check current lane - tiles to the right
        for i in range(1, 3):
            t = self._tile
            for j in range(i):
                if t is None:
                    break
                t = t.entrance()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
        
        # check current lane - tiles to the left
        for i in range(1, 3):
            t = self._tile
            for j in range(i):
                if t is None:
                    break
                t = t.exit()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
        
        # check lane above if it exists
        # for adjacent lanes, max distance is 1 (since 1 up/down + 1 left/right = distance 2)
        if self._tile.above():
            # check same column
            if isinstance(self._tile.above().actor(), SpaceHeater):
                self.distract(1)
                return
            # check to the right (only distance 1)
            t = self._tile.above().entrance()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
            # check to the left (only distance 1)
            t = self._tile.above().exit()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
        
        # check lane below if it exists
        # for adjacent lanes, max distance is 1
        if self._tile.below():
            # check same column
            if isinstance(self._tile.below().actor(), SpaceHeater):
                self.distract(1)
                return
            # check to the right (only distance 1)
            t = self._tile.below().entrance()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
            # check to the left (only distance 1)
            t = self._tile.below().exit()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return

    def rest(self):
        """
        Reduces the current rest time of this cat by one
        If this Cat is finished resting, attempts to place this cat
          on an empty starting board position
        If there are no available board positions, this Cat rests another round
        """
        self._rest_time -= 1

        # if we're done resting, attempt to add this Cat to the board
        if self._rest_time == 0:
            board = GameManager.manager().board()
            # First, find all of the empty lanes
            empty_lanes = []
            for lane_index in range(board.get_lane_count()):
                lane = board.get_lane_entrance(lane_index)
                if lane.is_empty():
                    empty_lanes.append(lane)

            # if there are no empty lanes, rest another round
            if len(empty_lanes) == 0:
                self._rest_time = 1

            # otherwise, add self to an empy lane at random
            else:
                index = random.randint(0, len(empty_lanes)-1)
                lane_to_add = empty_lanes[index]
                self._attention = self._starting_attention
                self.teleport(lane_to_add)

    def distract(self, amount: int):
        """
        Distracts this cat by the given amount
        amount must be a positive integer
        If this cat is fully distracted (has no attention left)
          this cat is removed from the board and starts resting
        """
        assert isinstance(amount, int) and amount >= 0
        self._attention -= amount
        if self._attention <= 0:
            self._attention = 0
            self._rest_time = self._needed_rest_time
            self.remove_from_board()


class Tabby(Cat):
    """
    A moderately distractable cat, they're just doing their best
    """

    def __init__(self, initial_rest_time: int):
        """
        The constructor for a Tabby
        Tabbies have an image name 'tabby', 
          4 starting attention,
          and 4 rounds of needed rest time
        """
        super().__init__('tabby', 4, 4, initial_rest_time)

# Part 2: "New Cats"


class Calico(Cat):
    """A particularly clever cat, Calicos can focus longer
       and will try and dodge your contraptions

    They move up a lane after they are distracted (if they are still on the board)
    If the tile above this is not empty (i.e. contains an Actor) or if this Calico 
      is already at the top of the board, they instead don't move

    They also have 5 starting attention and 4 rounds of needed rest time
    """

    def __init__(self, initial_rest_time: int):
        super().__init__('calico', 5, 4, initial_rest_time)

    def distract(self, amount: int):
        # do the normal distraction stuff first
        super().distract(amount)
        
        # if the cat is still on board after getting distracted, try to move up
        if self.is_on_board():
            tile_above = self._tile.above()
            # only move up if there's a tile above and it's empty
            if tile_above and tile_above.is_empty():
                self.teleport(tile_above)


class Kitten(Cat):
    """
    Especially energetic, kittens get to take two moves per turn
    Fortunately, kittens are easily distractable and take long rests
    """

    def __init__(self, initial_rest_time: int):
        super().__init__('kitten', 3, 6, initial_rest_time)

    def end_round(self):
        # kittens move twice if they're on the board
        if self.is_on_board():
            self.move()
            # need to check again because might've been removed after first move
            if self.is_on_board():
                self.move()
        else:
            self.rest()
