# cats-vs-homework (A tower defense game built with Python and Tkinter)
Python-based tower defense game inspired from Plants vs. Zombies. 

In this version however, you must protect your roommate (who needs to submit a homework) from their adorable but distracting cats using various automated contraptions.

<img width="900" height="653" alt="Screenshot 2025-11-30 101156" src="https://github.com/user-attachments/assets/63508955-309f-439c-a3e8-8fc57caf088b" />
<img width="1835" height="966" alt="Screenshot 2025-11-30 102631" src="https://github.com/user-attachments/assets/56ff3454-d2e4-4f6d-a35e-00e4cf97396f" />

Game Overview:

Roommate is trying to finish their homework, but their cats keep demanding attention! We Deploy strategic contraptions to keep the cats entertained and away from our roommate long enough to complete the assignment.

# Difficulty Modes

Easy Mode: Simple cat patterns, great for learning

Medium Mode: Introduces clever Calico cats that dodge contraptions

Hard Mode: Fast-moving Kittens that take two actions per turn

# 🎮 Features

Contraptions (Defensive Units)

Laser Pointer (7 batteries): Distracts first cat in a lane

Snack Dispenser (4 batteries): Can withstand 5 cat interactions

Battery Charger (3 batteries): Generates batteries every other turn

Ball Thrower (3 batteries): Targets nearest cat within 3 tiles

Triple Laser Pointer (12 batteries): Covers three lanes simultaneously

Colorful Ball Thrower (5 batteries): Places persistent colorful balls on the board

Space Heater (4 batteries): Creates a passive distraction zone (range 2)

# Cat Types

Tabby: Standard cat with 4 attention, rests 4 rounds

Calico: Smart cat (5 attention) that moves up a lane when distracted

Kitten: Energetic cat (3 attention) that moves twice per turn but rests 6 rounds

# Installation & Setup
Prerequisites

Python 3.8 or higher
tkinter (usually comes with Python)

# Quick Start

Clone the repository:

bashgit clone https://github.com/abdoulousseini2028-droid/cats-vs-homework.git

cd cats-vs-homework

# Run the game:

bashpython catsvshomework.py
No external dependencies required! The game uses only Python standard libraries

# How to Play:

Select Difficulty: Choose Easy, Medium, or Hard

Place Contraptions: Click a contraption, then click an empty tile

Manage Resources: Each contraption costs batteries

End Turn (Click 'End Turn'): Let contraptions act and cats move

Strategy: Survive 40 rounds!

# Pro Tips

Place Battery Chargers early for sustainable defense

Use Snack Dispensers as "walls" - they survive 5 hits

Triple Laser Pointers cover 3 lanes but cost 12 batteries

Space Heaters work great in corridors

Watch out for Calicos that dodge up lanes!

# Technical Implementation
Design Patterns Used

Singleton Pattern: GameManager ensures single game state
Inheritance: Contraptions and cats use class hierarchies
Polymorphism: Different behaviors through method overriding
Observer Pattern: Tile system for actor placement

# Key Technologies

Tkinter: GUI framework
Object-Oriented Python: Clean class design
Event-Driven Architecture: Turn-based game loop

# Core Systems

Tile-based Grid: 8-tile lanes with entrance/exit connections
Manhattan Distance Calculations: For range-based effects
State Management: Tracks batteries, rounds, positions
Collision Detection: Handles cat-contraption interactions

Testing
bashpython test.py

🎨 Customization
Adding New Contraptions
pythonclass MyContraption(Contraption):
    def __init__(self):
        super().__init__('my_image', cost=5)
    
    def end_round(self):
        # Your custom behavior
        pass
Adding New Cat Types
pythonclass MyCat(Cat):
    def __init__(self, initial_rest_time: int):
        super().__init__('my_image', attention=4, rest=4, initial_rest_time)

📧 Contact
Abdoul Rahim Ousseini - GitHub


