"""
Abdoul Rahim Ousseini

This module contains all contraption classes used to defend against cats.
Each contraption has unique behaviors and costs to provide strategic variety.
"""

from src.managers import GameManager, Actor, Tile
from src.cats import Cat


class Contraption(Actor):
    """
    Base class for all defensive contraptions.
    
    Contraptions are automated devices that help keep cats entertained
    and distracted from bothering the player's roommate.
    """

    _cost: int

    def __init__(self, image_name: str, cost: int):
        """
        Initialize a contraption with an image and battery cost.
        
        Args:
            image_name: Name of the image file (without extension)
            cost: Number of batteries required to place this contraption
        """
        super().__init__(image_name)
        assert isinstance(cost, int) and cost >= 0
        self._cost = cost

    def cost(self) -> int:
        """Return the battery cost of this contraption."""
        return self._cost

    def place(self, tile: 'Tile'):
        """
        Place this contraption on the game board.
        
        Args:
            tile: The tile where this contraption should be placed
        """
        assert isinstance(tile, Tile)
        GameManager.manager().add_contraption(self)
        self.teleport(tile)

    def end_round(self):
        """
        Execute contraption behavior at the end of each round.
        Override in subclasses to implement specific behaviors.
        """
        pass

    def interact(self):
        """
        Handle interaction when a cat reaches this contraption.
        By default, cats knock over contraptions, removing them from the board.
        """
        self.tile().clear_actor()
        self._tile = None
        GameManager.manager().remove_contraption(self)


class LaserPointer(Contraption):
    """
    Distracts the first cat in its lane using a laser pointer.
    
    Cost: 7 batteries
    Range: Entire lane
    Effect: Distracts first cat by 1 attention point
    """

    def __init__(self):
        super().__init__('laser', 7)

    def end_round(self):
        """Search forward in the lane and distract the first cat found."""
        next = self._tile.entrance()
        while next is not None:
            if isinstance(next.actor(), Cat):
                next.actor().distract(1)
                return
            next = next.entrance()


# === Basic Defensive Contraptions ===

class SnackDispenser(Contraption):
    """
    Provides snacks to cats, surviving multiple interactions.
    
    Cost: 4 batteries
    Durability: 5 interactions
    Strategy: Acts as a durable "wall" to block cat advancement
    """

    def __init__(self):
        super().__init__('snacks', 4)
        self._uses = 5

    def interact(self):
        """Decrease durability; remove only when fully depleted."""
        self._uses -= 1
        if self._uses == 0:
            super().interact()


class BatteryCharger(Contraption):
    """
    Generates batteries to sustain defense operations.
    
    Cost: 3 batteries
    Generation: 1 battery every other turn
    Strategy: Essential for long-term sustainability
    """

    def __init__(self):
        super().__init__('charger', 3)
        self._ready = False

    def end_round(self):
        """Generate a battery on alternating turns using toggle pattern."""
        if self._ready:
            GameManager.manager()._batteries += 1
            GameManager.manager().selection_manager().update_battery_text(GameManager.manager()._batteries)
        self._ready = not self._ready


class BallThrower(Contraption):
    """
    Throws a ball to distract the nearest cat within range.
    
    Cost: 3 batteries
    Range: 3 tiles forward
    Effect: Distracts nearest cat by 1 attention point
    """

    def __init__(self):
        super().__init__('thrower', 3)

    def end_round(self):
        """Search within 3 tiles and distract the nearest cat."""
        current = self._tile.entrance()
        tiles_checked = 0
        
        while current is not None and tiles_checked < 3:
            if isinstance(current.actor(), Cat):
                current.actor().distract(1)
                return
            current = current.entrance()
            tiles_checked += 1


# === Advanced Contraptions ===

class TripleLaserPointer(Contraption):
    """
    High-powered laser covering three lanes simultaneously.
    
    Cost: 12 batteries
    Coverage: Current lane + adjacent lanes above and below
    Effect: Distracts first cat in each covered lane by 1 attention
    Strategy: Expensive but provides excellent area coverage
    """

    def __init__(self):
        super().__init__('triple_laser', 12)

    def end_round(self):
        """Distract the first cat in current, above, and below lanes."""
        self._shoot_laser(self._tile)
        
        if self._tile.above() is not None:
            self._shoot_laser(self._tile.above())
        
        if self._tile.below() is not None:
            self._shoot_laser(self._tile.below())

    def _shoot_laser(self, start):
        """
        Helper method to distract first cat in a lane.
        
        Args:
            start: Starting tile for laser search
        """
        tile = start.entrance()
        while tile is not None:
            if isinstance(tile.actor(), Cat):
                tile.actor().distract(1)
                break
            tile = tile.entrance()


class ColorfulBall(Actor):
    """
    A colorful ball that cats find irresistible.
    
    Cats automatically pick up these balls when moving through tiles
    containing them, getting distracted in the process.
    """
    def __init__(self):
        super().__init__('colorful_ball')


class ColorfulBallThrower(Contraption):
    """
    Throws colorful balls that persist on the board until picked up.
    
    Cost: 5 batteries
    Range: 3 tiles forward
    Behavior: Throws at cat if present, otherwise places persistent ball
    Strategy: Creates lasting obstacles that distract cats over time
    """

    def __init__(self):
        super().__init__('colorful_thrower', 5)

    def end_round(self):
        """
        Throw ball at cat if in range, otherwise place persistent ball.
        Prioritizes immediate distraction over obstacle placement.
        """
        tile = self._tile.entrance()
        count = 0
        found_cat = False
        
        # First priority: distract nearby cat
        while tile and count < 3:
            if isinstance(tile.actor(), Cat):
                tile.actor().distract(1)
                found_cat = True
                break
            tile = tile.entrance()
            count += 1
        
        # Second priority: place persistent ball on furthest empty tile
        if not found_cat:
            tile = self._tile.entrance()
            count = 0
            last_empty = None
            
            while tile and count < 3:
                if tile.is_empty():
                    last_empty = tile
                tile = tile.entrance()
                count += 1
            
            if last_empty:
                new_ball = ColorfulBall()
                new_ball.teleport(last_empty)


class SpaceHeater(Contraption):
    """
    Creates a warm, cozy zone that passively distracts passing cats.
    
    Cost: 4 batteries
    Range: 2 tiles (Manhattan distance)
    Effect: Passive - cats check for heaters after each move
    Strategy: Excellent in corridors and choke points
    
    Note: Unlike active contraptions, the space heater doesn't take actions.
    Instead, cats detect nearby heaters and get distracted automatically.
    """

    def __init__(self):
        super().__init__('heater', 4)
