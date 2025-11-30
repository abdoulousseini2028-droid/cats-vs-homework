"""
Author: Abdoul Rahim Ousseini
Starting Date: November 17, 2025

Implementation of various contraptions to distract cats from bothering my roommate
"""

from src.managers import GameManager, Actor, Tile
from src.cats import Cat


class Contraption(Actor):
    """
    Base class that represents all contraptions
    """

    _cost: int
    """
    Cost (in batteries) to place this contraption
    """

    def __init__(self, image_name: str, cost: int):
        """
        Initializes this contraption with a positive cost
        """
        super().__init__(image_name)
        assert isinstance(cost, int) and cost >= 0
        self._cost = cost

    def cost(self) -> int:
        """
        Returns the cost in batteries for this contraption
        """
        return self._cost

    def place(self, tile: 'Tile'):
        """
        Places this contraption on the board
        """
        assert isinstance(tile, Tile)

        GameManager.manager().add_contraption(self)
        self.teleport(tile)

    def end_round(self):
        """
        Takes some action as a contraption
        By default, a contraption does nothing at the end of the round
        """
        pass

    def interact(self):
        """
        A cat interacts with this contraption
        Any interaction immediately knocks the base contraption over
          and removes it from the board
        """
        self.tile().clear_actor()
        self._tile = None
        GameManager.manager().remove_contraption(self)


class LaserPointer(Contraption):
    """
    Each round, points a laser to attempt to distract the first cat in its lane
    """

    def __init__(self):
        """
        The constructor for a LaserPointer
        Laser pointers have an image name 'laser' and cost 7 batteries
        """
        super().__init__('laser', 7)

    def end_round(self):
        """
        A laser pointer distracts the first cat in its lane
        """
        next = self._tile.entrance()
        while next is not None:
            if isinstance(next.actor(), Cat):
                next.actor().distract(1)
                return  # when we find a cat
            next = next.entrance()

# Part 1

class SnackDispenser(Contraption):
    """
    A Snack dispenser does nothing by itself, but can be interacted with
      a total of 5 times before being knocked over
    """

    def __init__(self):
        super().__init__('snacks', 4)
        self._uses = 5  

    def interact(self):
        self._uses -= 1
        # only remove it if we're out of uses
        if self._uses == 0:
            super().interact()


class BatteryCharger(Contraption):
    """
    Every other round, charges a new battery
    Does not charge a battery the round it is placed
    """

    def __init__(self):
        super().__init__('charger', 3)
        self._ready = False  # not ready first turn

    def end_round(self):
        # if ready, give a battery (negative spend = gain)
        if self._ready:
            GameManager.manager()._batteries += 1
            GameManager.manager().selection_manager().update_battery_text(GameManager.manager()._batteries)
        # flip the ready state each turn
        self._ready = not self._ready


class BallThrower(Contraption):
    """
    Each round, throws a ball to distract the nearest Cat within 3 spaces
    If there is no such Cat, this contraption does nothing
    """

    def __init__(self):
        super().__init__('thrower', 3)

    def end_round(self):
        # look for cats in the next 3 tiles
        current = self._tile.entrance()
        tiles_checked = 0
        
        while current is not None and tiles_checked < 3:
            if isinstance(current.actor(), Cat):
                current.actor().distract(1)
                return  # found one, we're done
            current = current.entrance()
            tiles_checked += 1

# Part 3: 


class TripleLaserPointer(Contraption):
    """
    Each round, points a laser to attempt to distract the first cat in its lane
      _and_ a cat in both the lane above and below this contraption
    """

    def __init__(self):
        super().__init__('triple_laser', 12)

    def end_round(self):
        # distract cat in my lane
        self._shoot_laser(self._tile)
        
        # distract cat above me
        if self._tile.above() is not None:
            self._shoot_laser(self._tile.above())
        
        # distract cat below me
        if self._tile.below() is not None:
            self._shoot_laser(self._tile.below())

    def _shoot_laser(self, start):
        # helper function to shoot laser down a lane
        tile = start.entrance()
        while tile is not None:
            if isinstance(tile.actor(), Cat):
                tile.actor().distract(1)
                break  # stop after hitting first cat
            tile = tile.entrance()


class ColorfulBall(Actor):
    """Colorful ball that cats pick up"""
    def __init__(self):
        super().__init__('colorful_ball')


class ColorfulBallThrower(Contraption):
    """
    Each round, throws a ball to distract the nearest Cat within 3 spaces
    If there is no such Cat, adds a colorful ball to the furthest empty space
      within the 3-space range of this colorful ball thrower
    """

    def __init__(self):
        super().__init__('colorful_thrower', 5)

    def end_round(self):
        # first try to hit a cat with the ball
        tile = self._tile.entrance()
        count = 0
        found_cat = False
        
        while tile and count < 3:
            if isinstance(tile.actor(), Cat):
                tile.actor().distract(1)
                found_cat = True
                break
            tile = tile.entrance()
            count += 1
        
        # for no cat found, place a ball on the furthest empty spot
        if not found_cat:
            tile = self._tile.entrance()
            count = 0
            last_empty = None
            
            while tile and count < 3:
                if tile.is_empty():
                    last_empty = tile  # keep track of furthest empty
                tile = tile.entrance()
                count += 1
            
            # place ball if we found an empty spot
            if last_empty:
                new_ball = ColorfulBall()
                new_ball.teleport(last_empty)


class SpaceHeater(Contraption):
    """
    This Contraption, by itself, does nothing
    However, any cat that ends a move within a range of two of this Contraption
      is distracted for exactly one point
    """

    def __init__(self):
        """
        The constructor for a SpaceHeater
        Space heaters have an image name 'heater' and cost 4 batteries
        """
        super().__init__('heater', 4)
