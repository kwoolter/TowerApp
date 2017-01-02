#The Tower
by kwoolter
(c) 2016

##Requirements
- Python 3.2 - https://www.python.org/downloads/release/python-326/
- PyGame for Python 3.2 - http://pygame.org/ftp/pygame-1.9.2a0.win32-py3.2.msi

##Getting Started
- Install the requirements
- Associate python32 with the project
- Use run.py to start the application
- Tower.hst contains the high score table

##The Story
Find the golden chalices hidden in the four worlds of the dying realm.
Use speed, skill, patience and magical items to find your way.  Collect treasures to boost your score.
Watch out for your health level!  Game over if it gets to 0.

Good luck!

## Controls
- Move player - W,A,S,D or Cursor keys
- Pause - space bar
- Change player name - "N" from title screen

##Structure
The towerrpg module contains all of the files for the game:-
- towerrpg\game.py - main game engine (model) - Player, Floor, TowerRPG, FloorBuilder
- towerrpg\graphics.py - classes to display the game (view) - FloorView, ScoreView
- towerrpg\main.py - the main pygame loop (controller)
- towerrpg\KWGameClasses.py - high score table code
- towerrpg\eztext.py - text input function for pygame.  Used to enter player's name
- towerrpg\resources\ - folder contains all of the graphics files (.png)


