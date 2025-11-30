"""
Last edited by Dietrich Geisler, May 2025

Setup script for Cats vs Homework game
"""

from src.main_menu import MainMenu

def main():
    menu = MainMenu()
    manager = menu.run()
    if manager is not None:
        manager.root().mainloop()

if __name__ == '__main__':
    main()
