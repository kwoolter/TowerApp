#The Tower
##Requirements
- Python 3.2 - https://www.python.org/downloads/release/python-326/
- PyGame for Python 3.2 - http://pygame.org/ftp/pygame-1.9.2a0.win32-py3.2.msi

##Getting Started
- Install the requirements
- Associate python32 with the project
- Use run.py to start the application
- Tower.hst contains the high score table

## Controls
- Move player - W,A,S,D or Cursor keys
- Pause - space bar

##Structure
The towerrpg module contains all of the files for the game:-
- towerrpg\game.py - main game engine (model) - Player, Floor, TowerRPG, FloorBuiler
- towerrpg\graphics.py - classes to diaplay the game (view) - FloorView, ScoreView
- towerrpg\main.py - the main pygame loop (controller)
- towerrpg\KWGameClasses.py - high score table code
- towerrpg\eztext.py - text input function for pygame
- towerrpg\resources\ - folder contains all of the graphics files (.png)


