"""
Abdoul Rahim Ousseini

This module implements different cat types with unique behaviors.
Each cat has distinct movement patterns, attention characteristics, and special abilities.
"""

import random
from typing import TYPE_CHECKING
from src.managers import GameManager, Actor


class Cat(Actor):
    """
    Base class representing all cats in the game.
    
    Cats move toward the player's roommate, attempting to distract them.
    Each cat has an attention level that must be reduced to zero before
    they are removed from the board and need to rest.
    """

    _starting_attention: int
    """Starting attention level when cat enters the board"""

    _attention: int
    """
    Current attention level of this cat.
    When this reaches zero, the cat becomes fully distracted and leaves the board.
    """

    _needed_rest_time: int
    """Number of rounds this cat rests after being distracted"""

    _rest_time: int
    """
    Rounds remaining until this cat returns to the board.
    Zero when cat is actively on the board.
    """

    def __init__(self,
                 image_name: str,
                 starting_attention: int,
                 needed_rest_time: int,
                 starting_rest_time: int):
        """
        Initialize a cat with specified attention and rest characteristics.

        Args:
            image_name: Name of the cat's image file
            starting_attention: Initial attention level when entering board
            needed_rest_time: Rounds to rest after being distracted (minimum 1)
            starting_rest_time: Initial rounds before first board appearance
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
        """Return debugging representation of this cat."""
        return f'{self.__class__.__name__}(attention={self._attention}, rest_time={self._rest_time})'

    def attention(self) -> int:
        """Return current attention level."""
        return self._attention

    def rest_time(self) -> int:
        """Return remaining rest time."""
        return self._rest_time

    def end_round(self):
        """
        Execute cat behavior at round end.
        Active cats move forward, resting cats count down rest time.
        """
        if self.is_on_board():
            self.move()
        else:
            self.rest()

    def move(self):
        """
        Move cat forward one tile or interact with obstacles.
        
        Movement priority:
        1. Check for game end (reached roommate)
        2. Pick up colorful balls if present
        3. Move to empty tiles
        4. Interact with contraptions
        5. Wait if another cat blocks the path
        """
        from src.contraptions import Contraption, ColorfulBall, SpaceHeater

        # Game over if cat reaches the end
        if self.tile().exit() is None:
            GameManager.manager().lose_game()
            return

        next_spot = self.tile().exit()
        
        # Pick up colorful balls and get distracted
        if isinstance(next_spot.actor(), ColorfulBall):
            next_spot.clear_actor()
            self.teleport(next_spot)
            self.distract(1)
            self._check_space_heater()
            return
        
        # Move to empty tiles
        if next_spot.is_empty():
            self.teleport(next_spot)
            self._check_space_heater()
            return
        
        # Interact with contraptions
        if isinstance(next_spot.actor(), Contraption):
            next_spot.actor().interact()
            return
        
        # Another cat blocks the path - wait

    def _check_space_heater(self):
        """
        Check for nearby space heaters and get distracted if found.
        
        Uses Manhattan distance calculation with range 2:
        - Same lane: distance 1-2 in both directions
        - Adjacent lanes: distance 0-1 in both directions
        
        This creates a diamond/ring pattern around each heater.
        """
        from src.contraptions import SpaceHeater
        
        # Check current lane - tiles to the right (distance 1-2)
        for i in range(1, 3):
            t = self._tile
            for j in range(i):
                if t is None:
                    break
                t = t.entrance()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
        
        # Check current lane - tiles to the left (distance 1-2)
        for i in range(1, 3):
            t = self._tile
            for j in range(i):
                if t is None:
                    break
                t = t.exit()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
        
        # Check lane above (distance 0-1 only for Manhattan distance 2)
        if self._tile.above():
            # Same column (distance 0)
            if isinstance(self._tile.above().actor(), SpaceHeater):
                self.distract(1)
                return
            # One tile right (distance 1)
            t = self._tile.above().entrance()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
            # One tile left (distance 1)
            t = self._tile.above().exit()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
        
        # Check lane below (distance 0-1 only for Manhattan distance 2)
        if self._tile.below():
            # Same column (distance 0)
            if isinstance(self._tile.below().actor(), SpaceHeater):
                self.distract(1)
                return
            # One tile right (distance 1)
            t = self._tile.below().entrance()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return
            # One tile left (distance 1)
            t = self._tile.below().exit()
            if t and isinstance(t.actor(), SpaceHeater):
                self.distract(1)
                return

    def rest(self):
        """
        Reduce rest time and attempt to return to board when ready.
        
        Cats spawn randomly on any empty entrance lane.
        If no lanes are available, they rest for one more round.
        """
        self._rest_time -= 1

        if self._rest_time == 0:
            board = GameManager.manager().board()
            empty_lanes = []
            
            # Find all empty entrance lanes
            for lane_index in range(board.get_lane_count()):
                lane = board.get_lane_entrance(lane_index)
                if lane.is_empty():
                    empty_lanes.append(lane)

            # If no lanes available, rest another round
            if len(empty_lanes) == 0:
                self._rest_time = 1
            else:
                # Spawn on random empty lane
                index = random.randint(0, len(empty_lanes)-1)
                lane_to_add = empty_lanes[index]
                self._attention = self._starting_attention
                self.teleport(lane_to_add)

    def distract(self, amount: int):
        """
        Reduce cat's attention by specified amount.
        
        Args:
            amount: Attention reduction (must be non-negative)
        
        When attention reaches zero, cat is removed from board and starts resting.
        """
        assert isinstance(amount, int) and amount >= 0
        self._attention -= amount
        if self._attention <= 0:
            self._attention = 0
            self._rest_time = self._needed_rest_time
            self.remove_from_board()


class Tabby(Cat):
    """
    Standard cat with balanced stats.
    
    Stats: 4 attention, 4 rest rounds
    Behavior: Moves forward each turn, no special abilities
    Strategy: Straightforward threat that's easy to defend against
    """

    def __init__(self, initial_rest_time: int):
        super().__init__('tabby', 4, 4, initial_rest_time)


# ========== Special Cat Types ==========

class Calico(Cat):
    """
    Intelligent cat that learns to dodge contraptions.
    
    Stats: 5 attention (harder to distract), 4 rest rounds
    Special Ability: Moves up one lane when distracted (if space available)
    Strategy: Creates multi-lane pressure, forcing defense across rows
    
    The dodging behavior makes Calicos particularly challenging as they
    avoid concentrated defenses and spread across the board.
    """

    def __init__(self, initial_rest_time: int):
        super().__init__('calico', 5, 4, initial_rest_time)

    def distract(self, amount: int):
        """
        Standard distraction with lane-switching behavior.
        After being distracted, attempts to move up one lane to dodge future attacks.
        """
        super().distract(amount)
        
        # If still on board, try to dodge up
        if self.is_on_board():
            tile_above = self._tile.above()
            if tile_above and tile_above.is_empty():
                self.teleport(tile_above)


class Kitten(Cat):
    """
    Highly energetic cat with rapid movement.
    
    Stats: 3 attention (easily distracted), 6 rest rounds (long naps)
    Special Ability: Takes two moves per turn instead of one
    Strategy: Fast-moving threat that can quickly overwhelm defenses
    
    The double-move makes kittens dangerous in open areas but they
    tire quickly when hitting obstacles like space heaters or snack dispensers.
    """

    def __init__(self, initial_rest_time: int):
        super().__init__('kitten', 3, 6, initial_rest_time)

    def end_round(self):
        """
        Take two moves per turn if on the board.
        Checks board status between moves since kitten may be distracted mid-turn.
        """
        if self.is_on_board():
            self.move()
            # Re-check board status (may have been distracted during first move)
            if self.is_on_board():
                self.move()
        else:
            self.rest()
