__author__ = 'user'

import sys
import random
import logging
import time

from towerrpg.KWGameClasses import HighScoreTable


class Player():
    def __init__(self, name, x: int, y: int):
        self.name = name
        self._x = x
        self._y = y
        self.old_x = x
        self.old_y = y
        self.initialise()

    # Set player's attributes back to starting values
    def initialise(self):
        self.keys = 0
        self.exit_keys = 0
        self.boss_key = False
        self.treasure = 0
        self.trophies = 0
        self.kills = 0
        self.HP = 10
        self.sword = False
        self.shield = False

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        self.old_x = self._x
        self._x = new_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        self.old_y = self._y
        self._y = new_y

    def moved(self):
        return (self._x, self._y) != (self.old_x, self.old_y)

    # Go back to old position
    def back(self):
        self._x = self.old_x
        self._y = self.old_y

    def score(self):
        return self.kills + self.treasure + (self.trophies * 50)


class Floor:
    # Tiles
    BANG = "="
    BEACH = "s"
    BEHOLDER = ">"
    BITER = "A"
    BLUE_POTION = "l"
    BOMB = "b"
    BOMB_LIT = "B"
    BOSS_DOOR = "d"
    BOSS_KEY = "$"
    BRAZIER = "q"
    BRAZIER_LIT = "Q"
    CAVE_WALL = "#"
    CHAOS_PORTAL = "c"
    CHEQUER = "]"
    CHICKEN = "C"
    CLOUD = "."
    DEVIL = "£"
    DOOR = "D"
    EMPTY = " "
    ENTRANCE = "-"
    ENTRANCE_TELEPORT = "3"
    EXIT = "+"
    EXIT_KEY = "%"
    FAKE_EXIT = "}"
    FROST_TREE = "F"
    FROST_WAND = "J"
    GOAL = "G"
    GOBLIN = "X"
    GRAVE1 = "!"
    GRAVE2 = "|"
    HOUR_GLASS = "g"
    HP_POTION = "@"
    ICE = 'i'
    KEY = "?"
    KITTY = "K"
    LAVA = "H"
    LIGHTNING = "L"
    MAGNET = "U"
    PINK_POTION = "k"
    PLAYER = "&"
    RED_POTION = "S"
    SAFETY = "8"
    SECRET_WALL = ";"
    SHIELD = "O"
    SKELETON = "Z"
    SKY = "~"
    SLIME = "["
    SNOW = "I"
    SNOW_BEAST = "x"
    SNOW_TREE = "t"
    STONE = "0"
    SWITCH = ","
    SWITCH_LIT = "<"
    SWITCH_TILE = "_"
    SWORD = "/"
    TELEPORT1 = "1"
    TELEPORT2 = "2"
    TRAP = "^"
    TREASURE = "*"
    TREASURE_CHEST = "j"
    TREE = "T"
    WALL = ":"
    WATER = "W"
    WELL = "w"
    YELLOW_POTION = "Y"

    # Tile properties
    ENEMIES = (GOBLIN, SKELETON, BITER, CHICKEN, DEVIL, SNOW_BEAST, BEHOLDER)
    ENEMY_EMPTY_TILES = (EMPTY, LIGHTNING)
    PLAYER_BLOCKED_TILES = (WALL, TREE, GRAVE1, GRAVE2, CAVE_WALL, WATER, SNOW, SNOW_TREE, STONE)
    PLAYER_DOT_TILES = (LAVA, SLIME, ICE)
    INDESTRUCTIBLE_ITEMS = (KEY, BOSS_KEY, DOOR, BOSS_DOOR, EXIT_KEY, TELEPORT1, TELEPORT2, WATER, BEACH, WELL)
    MELTABLE_ITEMS = {ICE: EMPTY, SNOW: ICE}
    SWAP_TILES = {SECRET_WALL: EMPTY, BOMB: BOMB_LIT, BRAZIER: BRAZIER_LIT, PINK_POTION: KITTY, BLUE_POTION: LIGHTNING}

    # Enemy movement modes
    MOVE_RANDOM = "MOVE RANDOM"
    MOVE_MAGNET = "MOVE MAGNET"

    def __init__(self, width=10, height=10, treasures=10, enemies=10, enemy_type=None, traps=10, keys=1,
                 entrance=None,
                 exit=None,
                 switch_tiles=None,
                 name=None):

        self.height = height
        self.width = width
        self.treasures = treasures
        self.enemies = enemies
        self.enemy_type = enemy_type
        self.traps = traps
        self.keys = keys
        self.name = name
        self.switch_on = False
        self.trophies = 0
        self.switch_tiles = switch_tiles
        self.player = None
        self.exit_locked = True
        self.enemy_move_mode = Floor.MOVE_RANDOM

        if entrance is not None:
            self.entrance = entrance
        else:
            self.entrance = (1, 1)

        if exit is not None:
            self.exit = exit
        else:
            self.exit = (width - 2, height - 2)

        self.plan = []
        self.plan = [[Floor.EMPTY for x in range(self.height)] for x in range(self.width)]
        self.bombs = {}
        self.braziers = {}

        self.auto_build_plan()
        self.initialise()

        # print("Floor {0}, traps={1}".format(self.name, self.traps))

    def load_plan(self, plan):

        self.entrance = None
        self.exit = None
        self.height = len(plan)
        self.width = len(plan[0])
        self.plan = [[Floor.EMPTY for x in range(self.height)] for x in range(self.width)]

        fake_exits = []

        for y in range(0, len(plan)):
            row = plan[y]
            for x in range(0, min(self.width, len(row))):
                self.plan[x][y] = row[x]

                if row[x] == Floor.EXIT:
                    self.exit = (x, y)
                    print("Found the exit at {0},{1}".format(x, y))

                elif row[x] == Floor.ENTRANCE:
                    self.entrance = (x, y)
                    print("Found the entrance at {0},{1}".format(x, y))

                elif row[x] == Floor.ENTRANCE_TELEPORT and self.entrance is None:
                    self.entrance = (x, y)
                    print("Found the teleport entrance at {0},{1}".format(x, y))

                elif row[x] == Floor.GOAL:
                    self.trophies += 1
                    print("Found a trophy at {0},{1}".format(x, y))

                elif row[x] == Floor.FAKE_EXIT:
                    fake_exits.append((x, y))

        if self.entrance is None:
            self.entrance = (1, 1)

        # If no real exit exists and there are fake exits....
        if self.exit is None and len(fake_exits) > 0:
            # pick a random fake one and turn it into a real exit...
            self.exit = random.choice(fake_exits)
            x, y = self.exit
            self.plan[x][y] = Floor.EXIT
            print("Setting random real exit to {0},{1}".format(x, y))

        # Create safety zones around the entrance and exits
        if self.entrance is not None:
            self.safety_zone(self.entrance[0], self.entrance[1], 4, 4)

        if self.exit is not None:
            self.safety_zone(self.exit[0], self.exit[1], 4, 4)

        for fake_exit in fake_exits:
            self.safety_zone(fake_exit[0], fake_exit[1], 4, 4)

    # Build a safety zone around a specified location
    def safety_zone(self, x, y, height, width):
        for dx in range(-1 * int(width / 2), int(width / 2) + 1):
            for dy in range(-1 * int(height / 2), int(height / 2) + 1):
                if (x + dx) < self.width and (x + dx) >= 0 and (y + dy) < self.height and (y + dy) >= 0:
                    if self.plan[x + dx][y + dy] == Floor.EMPTY:
                        self.plan[x + dx][y + dy] = Floor.SAFETY
                        # print("Safety zone created at {0},{1}".format((x + dx), (y + dx)))

    # Build a very basic floor layout
    def auto_build_plan(self):

        x, y = self.entrance
        self.plan[x][y] = Floor.ENTRANCE

        x, y = self.exit
        self.plan[x][y] = Floor.EXIT

        for x in range(0, self.width):
            self.plan[x][0] = Floor.WALL
            self.plan[x][self.height - 1] = Floor.WALL

        for y in range(0, self.height):
            self.plan[0][y] = Floor.WALL
            self.plan[self.width - 1][y] = Floor.WALL

        # Create safety zones around the entrance and exits
        if self.entrance is not None:
            self.safety_zone(self.entrance[0], self.entrance[1], 4, 4)

        if self.exit is not None:
            self.safety_zone(self.exit[0], self.exit[1], 4, 4)

    def initialise(self):

        print("Start initialising {0}...".format(self.name))

        self.place_tiles(self.keys, Floor.EXIT_KEY, tries=20)
        self.place_tiles(self.treasures, Floor.TREASURE)
        self.place_tiles(self.enemies, self.enemy_type)
        self.place_tiles(self.traps, Floor.TRAP)

        print("Finished initialising {0}".format(self.name))

    # Find empty tiles to place items
    def place_tiles(self, item_count, item_type, tries=20):

        for i in range(0, item_count):
            attempts = 0
            while True:
                x = random.randint(1, self.width - 1)
                y = random.randint(1, self.height - 1)
                if self.plan[x][y] == Floor.EMPTY:
                    self.plan[x][y] = item_type
                    logging.info("Placed a {0} at {1},{2}".format(item_type, x, y))
                    break
                attempts += 1
                # We tried several times to find an empty square, time to give up!
                if attempts > tries:
                    print("Can't find an empty tile t place {0} after {1} tries".format(item_type, attempts))
                    break

    @property
    def current_tile(self):
        if self.player != None:
            return self.plan[self.player.x][self.player.y]
        else:
            return None

    def set_player_position(self, reference_point: str):

        if reference_point == Floor.EXIT:
            position = self.exit
        else:
            position = self.entrance

        self.player.x, self.player.y = position

    def set_tile(self, x: int, y: int, new_tile: str):
        self.plan[x][y] = new_tile

    def get_tile(self, x: int, y: int):
        tile = self.plan[x][y]

        if tile == Floor.SWITCH_TILE and self.switch_tiles is not None:
            if self.switch_on == True:
                tile = self.switch_tiles[1]
            else:
                tile = self.switch_tiles[0]

        return tile

    def set_current_tile(self, new_tile: str):
        self.set_tile(self.player.x, self.player.y, new_tile)

    def print(self):

        for y in range(0, self.height):
            for x in range(0, self.width):
                sys.stdout.write(self.plan[x][y])
            print()
        sys.stdout.flush()

    def move_player(self, dx: int, dy: int):

        if self.player is None:
            raise (Exception("No player on this floor to move."))

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            print("Hit the boundary!")
            new_x = self.player.x
            new_y = self.player.y

        elif self.get_tile(new_x, new_y) in Floor.PLAYER_BLOCKED_TILES:
            new_x = self.player.x
            new_y = self.player.y

        self.player.x = new_x
        self.player.y = new_y

    def is_collision(self):

        collision_items = list(Floor.ENEMIES)
        collision_items.append(Floor.TRAP)

        if self.get_tile(self.player.x, self.player.y) in collision_items:
            return True
        else:
            return False

    def switch(self, setting=None):
        if setting is None:
            self.switch_on = not self.switch_on
        else:
            self.switch_on = setting

    def tick(self):

        # If the player is on a damage tile then take damage
        if self.current_tile in Floor.PLAYER_DOT_TILES:
            self.player.HP -= 1

        enemy_count = 0
        new_enemy_positions = {}

        # Look for items across the floor plan
        for y in range(0, self.height):
            for x in range(0, self.width):

                tile = self.get_tile(x, y)

                # If we found a lit bomb...
                if tile == Floor.BOMB_LIT:
                    if (x, y) not in self.bombs:
                        self.bombs[(x, y)] = TowerRPG.BOMB_COUNT
                    else:
                        self.bombs[(x, y)] = self.bombs[(x, y)] - 1
                        if self.bombs[(x, y)] <= 0:
                            self.plan[x][y] = Floor.BANG
                            del self.bombs[(x, y)]

                # If we found a lit brazier...
                if tile == Floor.BRAZIER_LIT:
                    if (x, y) not in self.braziers:
                        self.braziers[(x, y)] = TowerRPG.BRAZIER_COUNT
                    else:
                        self.braziers[(x, y)] = self.braziers[(x, y)] - 1
                        if self.braziers[(x, y)] <= 0:
                            self.plan[x][y] = Floor.BRAZIER
                            del self.braziers[(x, y)]

                            for area_y in range(y - 1, y + 2):
                                for area_x in range(x - 1, x + 2):
                                    tile = self.plan[area_x][area_y]
                                    if tile in Floor.MELTABLE_ITEMS.keys():
                                        self.plan[area_x][area_y] = Floor.MELTABLE_ITEMS[tile]

                # If we found a bang...
                elif tile == Floor.BANG:
                    for area_y in range(y - 1, y + 2):
                        for area_x in range(x - 1, x + 2):
                            tile = self.plan[area_x][area_y]

                            if tile in Floor.ENEMIES:
                                self.player.kills += 1
                                print("You killed an enemy with a bomb!")

                            elif (self.player.x, self.player.y) == (area_x, area_y):
                                self.player.HP -= 3
                                print("You were hit by the bomb blast and lost health!")

                            if tile not in Floor.INDESTRUCTIBLE_ITEMS:
                                self.plan[area_x][area_y] = Floor.EMPTY

                # If we found an enemy...
                elif tile in Floor.ENEMIES:

                    enemy_count += 1

                    # If we are in random move mode then...
                    if self.enemy_move_mode == Floor.MOVE_RANDOM:
                        # ..look at a random square around the enemy...
                        new_x, new_y = random.choice(((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)))
                        new_x += x
                        new_y += y

                    # If we are in magnet move mode then..
                    elif self.enemy_move_mode == Floor.MOVE_MAGNET:

                        new_x = x
                        new_y = y

                        # first try and move horizontally towards the player...
                        if self.player.x > x:
                            new_x += 1
                        elif self.player.x < x:
                            new_x -= 1

                        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                            new_x = x
                            new_y = y

                        # if this square is not empty then try moving vertically towards the player...
                        if self.plan[new_x][new_y] not in Floor.ENEMY_EMPTY_TILES:
                            new_x = x
                            if self.player.y > y:
                                new_y += 1
                            elif self.player.y < y:
                                new_y -= 1

                    # If out of bounds...
                    if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                        print("Hit boundary")

                    # ...if the square is empty move the enemy to the new square
                    elif self.plan[new_x][new_y] == Floor.EMPTY and (new_x, new_y) not in new_enemy_positions:
                        self.plan[x][y] = Floor.EMPTY
                        new_enemy_positions[(new_x, new_y)] = tile

                    # ...else if the square contains lightning then kill the enemy
                    elif self.plan[new_x][new_y] == Floor.LIGHTNING:
                        print("You killed an enemy with lightning!")
                        self.player.kills += 1
                        self.plan[x][y] = Floor.EMPTY

        for key in new_enemy_positions.keys():
            new_x, new_y = key
            self.plan[new_x][new_y] = new_enemy_positions[key]


class TowerRPG:
    # Define Game States
    READY = 0
    PLAYING = 1
    GAME_OVER = 2
    FINISHED = 3
    PAUSED = 4

    # Level starting floors
    TRAINING_LEVEL = 11
    CAVE_ENTRANCE = 12
    FROST_WARD = 20
    CHAOS = 28
    STARTING_LEVEL = 0


    # Links between worlds
    TELEPORTS = {Floor.TELEPORT1: TRAINING_LEVEL,
                 Floor.TELEPORT2: STARTING_LEVEL,
                 Floor.WELL: CAVE_ENTRANCE,
                 Floor.FROST_TREE: FROST_WARD,
                 Floor.CHAOS_PORTAL: CHAOS}


    # Define effect constants
    NO_EFFECT = "NO EFFECT"
    SLOW = "SLOW ENEMIES"
    SLOW_COUNT = 20
    FAST = "QUICK ENEMIES"
    FAST_COUNT = 20
    SWORD = "SWORD"
    SWORD_COUNT = 20
    SHIELD = "SHIELD"
    SHIELD_COUNT = 20
    MAGNET = "MAGNET"
    MAGNET_COUNT = 20
    FROST = "FROST"
    FROST_COUNT = 20
    BOMB_COUNT = 5
    BRAZIER_COUNT = 5

    # Difficulty
    EASY = 700
    MEDIUM = 500
    HARD = 300

    def __init__(self, player: Player, difficulty=None):

        self.floors = []
        self._player = player

        if difficulty == None:
            difficulty = TowerRPG.MEDIUM

        self.difficulty = difficulty

        self.initialise()

        self.hst = HighScoreTable("Tower")
        self.hst.load()
        self.hst.print()

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        self._player = player
        self.initialise()

    def initialise(self):

        self.game_start = time.time()
        self.state = TowerRPG.READY
        self.tick_count = 0
        self.effect_count = 0
        self.effects = {}


        self.current_floor_level = 7
        self.current_floor_level = TowerRPG.CHAOS + 6
        self.current_floor_level = TowerRPG.STARTING_LEVEL

        self.player.initialise()

        builder = FloorBuilder()
        builder.initialise()
        self.floors = builder.floors
        self.trophies = builder.trophies

        self.current_floor.player = self.player
        self.current_floor.set_player_position(Floor.ENTRANCE)

    @property
    def elapsed_time(self):
        elapsed_seconds = time.time() - self.game_start
        return time.gmtime(elapsed_seconds)

    def print(self):
        for i in range(0, len(self.floors)):
            print("Floor {0}".format(i))
            self.floors[i].print()

    def is_high_score(self):
        if self.hst.is_high_score(self.player.score()):
            return True
        else:
            return False

    def change_floor(self, direction: int):
        new_floor = self.current_floor_level + direction

        if new_floor < 0 or new_floor >= len(self.floors):
            return
        else:
            self.current_floor_level = new_floor
            self.current_floor.player = self.player

            if direction > 0:
                self.current_floor.set_player_position(Floor.ENTRANCE)
            else:
                self.current_floor.set_player_position(Floor.EXIT)

    def set_floor(self, new_floor: int):

        if new_floor < 0 or new_floor >= len(self.floors):
            return
        else:
            self.current_floor_level = new_floor
            self.current_floor.player = self.player
            self.current_floor.set_player_position(Floor.ENTRANCE)

    @property
    def current_floor(self):
        return self.floors[self.current_floor_level]

    def check_collision(self):

        # Check if the player has collided with and enemy?
        if self.current_floor.is_collision() is True:

            print("collision!")

            if TowerRPG.SWORD in self.effects.keys():
                print("You killed an enemy with your sword")
                self.player.kills += 1
                self.current_floor.set_current_tile(Floor.EMPTY)

            elif TowerRPG.SHIELD in self.effects.keys():
                print("You defended yourself with your shield")

            else:
                self.player.HP -= 1
                self.current_floor.set_current_tile(Floor.EMPTY)
                print("HP down to %i" % self.player.HP)

    def slow_effect(self):

        print("Starting SLOW effect...")
        self.effects[TowerRPG.SLOW] = TowerRPG.SLOW_COUNT

    def fast_effect(self):

        print("Starting FAST effect...")
        self.effects[TowerRPG.FAST] = TowerRPG.FAST_COUNT

    def sword_effect(self):
        print("Starting SWORD effect...")
        self.player.sword = True
        self.effects[TowerRPG.SWORD] = TowerRPG.SWORD_COUNT

    def shield_effect(self):
        print("Starting SHIELD effect...")
        self.player.shield = True
        self.effects[TowerRPG.SHIELD] = TowerRPG.SHIELD_COUNT

    def magnet_effect(self):
        print("Starting MAGNET effect...")
        self.effects[TowerRPG.MAGNET] = TowerRPG.MAGNET_COUNT

    def frost_effect(self):
        print("Starting FROST effect...")
        self.effects[TowerRPG.FROST] = TowerRPG.FROST_COUNT

    def move_player(self, dx: int, dy: int):

        # If in a non-playing state then do nothing
        if self.state != TowerRPG.PLAYING:
            return

        self.current_floor.move_player(dx, dy)

        if self.current_floor.current_tile == Floor.EXIT:

            print("You found the exit!")

            if self.current_floor.exit_locked is True and self.player.exit_keys > 0:
                self.player.exit_keys -= 1
                self.current_floor.exit_locked = False
            else:
                self.player.back()
                print("...but the exit is locked!")

            if self.current_floor.exit_locked is False:
                self.change_floor(1)
                self.current_floor.player = self.player
                print("You moved up to floor {0}!".format(self.current_floor_level))

        elif self.current_floor.current_tile == Floor.ENTRANCE and self.player.moved() is True:
            self.change_floor(-1)
            self.current_floor.player = self.player
            print("You found the entrance and moved to floor {0}!".format(self.current_floor_level))

        elif self.current_floor.current_tile == Floor.SWITCH and self.player.moved() is True:
            self.current_floor.switch()
            self.current_floor.set_current_tile(Floor.SWITCH_LIT)
            print("You found a switch!!")

        elif self.current_floor.current_tile == Floor.SWITCH_LIT and self.player.moved() is True:
            self.current_floor.switch()
            self.current_floor.set_current_tile(Floor.SWITCH)
            print("You found a switch!!")

        elif self.current_floor.current_tile == Floor.TREASURE:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.player.treasure += 1
            print("Found some treasure!!")

        elif self.current_floor.current_tile == Floor.TREASURE_CHEST:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.player.treasure += 10
            print("Found a treasure chest!!")

        elif self.current_floor.current_tile == Floor.HP_POTION:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.player.HP += 1
            print("Found an HP potion!!")

        elif self.current_floor.current_tile == Floor.KEY:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.player.keys += 1
            print("Found a key!!")

        elif self.current_floor.current_tile == Floor.EXIT_KEY:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.player.exit_keys += 1
            print("Found an exit key!!")

        elif self.current_floor.current_tile == Floor.BOSS_KEY:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.player.boss_key = True
            print("Found a BOSS key!!")

        elif self.current_floor.current_tile == Floor.SWORD:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.sword_effect()
            print("Found a sword!!")

        elif self.current_floor.current_tile == Floor.FROST_WAND:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.frost_effect()
            print("Found a frost wand!!")

        elif self.current_floor.current_tile == Floor.SHIELD:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.shield_effect()
            print("Found a shield!!")

        elif self.current_floor.current_tile == Floor.MAGNET:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.magnet_effect()
            print("Found a magnet!!")

        elif self.current_floor.current_tile in Floor.SWAP_TILES.keys():
            print("You found a {0} to {1} swappable tile!!".format(self.current_floor.current_tile,
                                                                   Floor.SWAP_TILES[self.current_floor.current_tile]))
            self.current_floor.set_current_tile(Floor.SWAP_TILES[self.current_floor.current_tile])

        elif self.current_floor.current_tile == Floor.FAKE_EXIT:
            print("You found the exit!")
            if self.current_floor.exit_locked is True and self.player.exit_keys > 0:
                self.current_floor.set_current_tile(Floor.EMPTY)
                print("...but it is a fake exit!")
            else:
                self.player.back()
                print("...but the exit is locked!")

        elif self.current_floor.current_tile == Floor.RED_POTION:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.slow_effect()
            print("You found a red potion!!")

        elif self.current_floor.current_tile == Floor.YELLOW_POTION:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.fast_effect()
            print("You found a yellow potion!!")

        elif self.current_floor.current_tile in TowerRPG.TELEPORTS.keys():
            self.set_floor(TowerRPG.TELEPORTS[self.current_floor.current_tile])
            print("You found a teleporter!")

        elif self.current_floor.current_tile in Floor.PLAYER_DOT_TILES:
            if self.current_floor.current_tile == Floor.LAVA and TowerRPG.FROST in self.effects.keys():
                self.current_floor.set_current_tile(Floor.EMPTY)
            else:
                self.player.HP -= 1
                print("You walked into something nasty!")

        elif self.current_floor.current_tile == Floor.GOAL:
            self.current_floor.set_current_tile(Floor.EMPTY)
            self.player.treasure += 30
            self.player.trophies += 1
            print("You found a trophy!!")

            if self.player.trophies >= self.trophies:
                print("You finished the game!!")
                self.state = TowerRPG.FINISHED

        elif self.current_floor.current_tile == Floor.DOOR:

            print("You found a door...")
            if self.player.keys > 0:
                self.player.keys -= 1
                self.current_floor.set_current_tile(Floor.EMPTY)
                print("...and you opened it!")
            else:
                self.player.back()
                print("...but the door is locked!")

        elif self.current_floor.current_tile == Floor.BOSS_DOOR:

            print("You found a BOSS door...")
            if self.player.boss_key is True:
                self.player.boss_key = False
                self.current_floor.set_current_tile(Floor.EMPTY)
                print("...and you opened it!")
            else:
                self.player.back()
                print("...but the door is locked!")

    def tick(self):

        self.tick_count += 1
        do_a_tick = False

        if self.state == TowerRPG.PLAYING:

            # If we are in SLOW mode....
            if TowerRPG.SLOW in self.effects.keys():
                if self.tick_count % 4 == 0:
                    do_a_tick = True

            # If we are in FAST mode...
            elif TowerRPG.FAST in self.effects.keys():
                do_a_tick = True

            elif self.tick_count % 2 == 0:
                do_a_tick = True

            if TowerRPG.MAGNET in self.effects.keys():
                self.current_floor.enemy_move_mode = Floor.MOVE_MAGNET
            else:
                self.current_floor.enemy_move_mode = Floor.MOVE_RANDOM

            expired_effects = []
            for effect in self.effects.keys():
                if self.effects[effect] > 0:
                    self.effects[effect] -= 1
                elif self.effects[effect] == 0:
                    print("Stopping %s effect." % effect)
                    expired_effects.append(effect)

            for effect in expired_effects:
                del self.effects[effect]

            if do_a_tick is True:
                self.current_floor.tick()

            # See if the player is dead...
            if self.player.HP <= 0:
                self.game_over()

    def game_over(self):

        self.state = TowerRPG.GAME_OVER

        if self.hst.is_high_score(self.player.score()):
            self.hst.add(self.player.name, self.player.score())
            self.hst.save()


class FloorBuilder():
    def __init__(self):
        self.floor_settings = []
        self.floor_plans = []
        self.floors = []
        self.trophies = 0

    def initialise(self):
        self.load_floor_plans()

        self.floor_settings = [
            (5, Floor.SKELETON, 0, 0, 0, None, "The Decrepit Gate"),
            (5, Floor.SKELETON, 0, 0, 0, None, "The Ancient Tower"),
            (10, Floor.GOBLIN, 5, 10, 1, None, "Back and Forth"),
            (11, Floor.GOBLIN, 6, 10, 1, None, "The Armoury"),
            (12, Floor.GOBLIN, 7, 10, 1, None, "The Maze"),
            (13, Floor.GOBLIN, 8, 10, 1, None, "Guard House"),
            (0, Floor.GOBLIN, 0, 0, 0, None, "The Trap"),
            (0, Floor.GOBLIN, 0, 5, 0, None, "Bomb Alley"),
            (14, Floor.GOBLIN, 9, 10, 1, None, "Hello Kitty"),
            (15, Floor.GOBLIN, 10, 10, 1, None, "The Final Countdown"),
            (0, Floor.GOBLIN, 0, 0, 0, None, "The Tower Top"),
            (5, Floor.CHICKEN, 0, 0, 0, None, "The Training Room"),
            (10, Floor.BITER, 5, 10, 0, None, "Cave Entrance"),
            (10, Floor.BITER, 15, 10, 1, (Floor.WALL, Floor.EMPTY), "Underground River"),
            (10, Floor.DEVIL, 5, 0, 0, (Floor.LAVA, Floor.EMPTY), "Lava Flows"),
            (10, Floor.BITER, 15, 10, 1, None, "Collossal Cavern"),
            (6, Floor.BITER, 5, 5, 1, (Floor.WATER, Floor.BEACH), "The Ancient Lake"),
            (5, Floor.BITER, 5, 10, 0, (Floor.WALL, Floor.EMPTY), "The Switch Maze"),
            (0, Floor.BITER, 0, 0, 0, None, "Nowhere to go"),
            (3, Floor.SKELETON, 0, 15, 0, (Floor.WALL, Floor.EMPTY), "Marble Hall"),
            (8, Floor.SNOW_BEAST, 10, 5, 0, None, "Frost Ward"),
            (8, Floor.SNOW_BEAST, 5, 5, 1, None, "Ice Fort"),
            (10, Floor.SNOW_BEAST, 10, 5, 1, None, "Deception"),
            (10, Floor.SNOW_BEAST, 10, 5, 1, None, "The Ice Throne"),
            (10, Floor.SKELETON, 5, 10, 1, None, "The Prison of Ice"),
            (6, Floor.SKELETON, 5, 10, 0, (Floor.ICE, Floor.EMPTY), "Dungeon of the Damned"),
            (10, Floor.SNOW_BEAST, 5, 10, 0, (Floor.ICE, Floor.EMPTY), "Lair of the Ice Beast"),
            (2, Floor.SNOW_BEAST, 0, 0, 0, None, "Frost Top"),
            (8, Floor.DEVIL, 5, 5, 1, None, "Chaos"),
            (0, Floor.DEVIL, 0, 0, 0, None, "Ceaseless Discharge"),
            (8, Floor.DEVIL, 5, 5, 1, None, "Furnace Steps"),
            (8, Floor.BEHOLDER, 10, 10, 0, None, "Forge of Giants"),
            (8, Floor.DEVIL, 10, 10, 1, None, "The Crucible"),
            (5, Floor.BEHOLDER, 4, 10, 0, (Floor.BOMB, Floor.BOMB_LIT), "The Pyre"),
            (5, Floor.DEVIL, 4, 10, 0, (Floor.BOMB, Floor.BOMB_LIT), "Hell's Gate"),
            (5, Floor.DEVIL, 4, 5, 0, None, "Fire Throne")
        ]

        if len(self.floor_settings) > len(self.floor_plans):
            raise (
                Exception(
                    "Too many settings %i compared to floors %i" % (len(self.floor_settings), len(self.floor_plans))))

        for i in range(0, len(self.floor_settings)):
            print("Processing floor %i" % i)
            enemies, enemy_type, traps, treasures, keys, switch_tiles, name = self.floor_settings[i]
            new_floor = Floor(treasures=treasures, enemies=enemies, enemy_type=enemy_type, traps=traps, keys=keys,
                              switch_tiles=switch_tiles, name=name)
            new_floor.load_plan(self.floor_plans[i])
            new_floor.initialise()
            self.floors.append(new_floor)
            self.trophies += new_floor.trophies
            print("Completed floor {0}.{1}".format(i, name))

        print("{0} floors built!".format(len(self.floors)))

    def load_floor_plans(self):
        # Decrepit Gate
        new_floor_plan = (

            ' t tt   t   #######:',
            'tFt? t t !!! ###w##:',
            '   t  !       #  #::',
            'tt                 :',
            ' t        T        :',
            't           !  |  ::',
            ' T  T |            :',
            'T        |         :',
            'T            |   :::',
            'T3    !          D +',
            'T   !     :      :::',
            'T        :c:   !   :',
            ' T  :::::: :::     :',
            'T  ::         :   ::',
            'T   D         %:   :',
            ' T ::         :    :',
            ' !  :::::: :::  | ::',
            'T        : : !     :',
            ' T  T ! 1 :   |  !?:',
            '  TT ! !TT TTT TT ::',

        )

        self.floor_plans.append(new_floor_plan)

        # The Ancient Tower
        new_floor_plan = (
            ' T  T  T T   TT  TT ',
            'T TT TT T TT T TT  T',
            'T T   T   T T   TT ',
            'T                 T ',
            ' T       :::   T   T',
            'T   T   :::::     T',
            'T      ::   ::   TT ',
            ' TT   ::     ::    T',
            'T   :::   :%  :   T ',
            'TT    :   :   ::  T ',
            '-  ?  D ::::: +: T T',
            'T     :   :   ::   T',
            ' TT :::   :   :   T ',
            'T     ::     ::   T ',
            'T    T ::   ::  T  T',
            ' TT     :::::      T',
            'T     T  :::   T  T ',
            ' T  T            T  ',
            'T   T T T 1 T TT  T ',
            ' TTT T T TTT T  TTT ',
        )

        self.floor_plans.append(new_floor_plan)



        # Back and Forth
        new_floor_plan = (
            '::::::::::::::::::::',
            ':-    U           K:',
            ':                  :',
            ':                  :',
            ':     Y          k :',
            ':::::::::::::::    :',
            ':             :    :',
            ':  l          :    :',
            ':       :::   :    :',
            ':  :::   :    :    :',
            ':   :    :   :::   :',
            ':   :   :::        :',
            ':   :         S    :',
            ':   :              :',
            ':   :::::::::;::::::',
            ':                 @:',
            ':                  :',
            ':                  :',
            ':                 +:',
            '::::::::::::::::::::'
        )
        self.floor_plans.append(new_floor_plan)

        # The Armoury
        new_floor_plan = (
            '::::::::::::::::::::',
            ':@ :               :',
            ':  :               :',
            ': k:               :',
            ':  :+ :            :',
            ':  ::::       ::   :',
            ':     :       ::   :',
            ':                  :',
            ':                  :',
            ':          l       :',
            ':                  :',
            ':  ::         ::   :',
            ':  ::         ::   :',
            ':                  :',
            ':            S     :',
            ':        :         :',
            ':       :::        :',
            ':      :;/::       :',
            ':     ;;;::::     -:',
            '::::::::::::::::::::'
        )

        self.floor_plans.append(new_floor_plan)

        # The Maze
        new_floor_plan = (
            '~~~.~~~~~~~~~.~~~~~~',
            '~~~~~~~~~.~~~~~~~~~.',
            '~~:::::::::::::::~~~',
            '.~:       S  :  :.~~',
            '~~:  ::::    :  :~~~',
            '~~:  :- :    :  :~~~',
            '~.:  :     k    :~~~',
            '~~:  ::::     :::~~~',
            '.~:     ::      :~.~',
            '~~:     ::      :~~~',
            '~~::;:   ::::   :~~~',
            '.~: O:      :   :~~~',
            '~~::::   :  :   :.~~',
            '~~: @:   : +:   :~~~',
            '~~:  :   ::::   :~~.',
            '~.:         l   :~~~',
            '~~:::::::::::::::~~~',
            '~~~~~~~~~~~~~~~~~~.~',
            '~~.~~~.~~~~~~.~~~~~~',
            '~~~~~~~~~.~~~~~~~~~~',

        )

        self.floor_plans.append(new_floor_plan)

        # Guard House
        new_floor_plan = (
            '~~~.~~~~~.~.~~~~.~~~',
            '.~~~~~~.~~~~~~.~~~~.',
            '~~:::::::::::::::~~~',
            '~~:            @:~.~',
            '~~:             :~~~',
            '.~:  ::     ::  :.~~',
            '~~:  ::     ::  :~~~',
            '~~:  :  : :  :  :~~.',
            '~.:     :+:     :~~~',
            '~~:   l :::     :.~~',
            '~.:     :-:    S:~~~',
            '~~:  :  : :  :  :~.~',
            '.~:  ::     ::  :~~~',
            '~~:  ::  k  ::  :~~.',
            '~~:             :~~~',
            '~.:             :.~~',
            '~~:::::::::::::::~~~',
            '~~~~.~~~~~~.~~~.~~~.',
            '~~.~~~.~~~~~~~~~~~~~',
            '.~~~~~~~~~.~~.~~~.~~',

        )

        self.floor_plans.append(new_floor_plan)

        # The Trap
        new_floor_plan = (
            '::::::::::::::::::::',
            ':                  :',
            ':        ?         :',
            ':                  :',
            ':   ::::::::::::   :',
            ':   :?X X X X X:   :',
            ':   :XlX X X X :   :',
            ':   : X::::D:lX:   :',
            ':   :X :?***:X :   :',
            ':+  : X:****: X:  -:',
            ':   :X :@*:::X/:   :',
            ':   :lX:@@D%: X:   :',
            ':   :X ::::::Xl:   :',
            ':   : X X X X X:   :',
            ':   :X X l X X :   :',
            ':   :::::D::::::   :',
            ':                  :',
            ':   Y    U     S   :',
            ':                  :',
            '::::::::::::::::::::',

        )

        self.floor_plans.append(new_floor_plan)

        # Bomb Alley
        new_floor_plan = (

            '::::::::::::::::::::',
            ':- :    : X X:@ % +:',
            ':: :: ^ :X X::::   :',
            '::b:: :b::::b  : ^^:',
            ':^:::  :^:Y: : :   :',
            ': ^::: :b:   :D::: :',
            ': : :  :X:::::   : :',
            ':  b::::UX :@   ^: :',
            ':::::: :X X:  ^  : :',
            ':@:::  : X?:b   ^: :',
            ':     U ::::::::::D:',
            ':     : :  :U:/:U  :',
            '::;:  : :b     : ^^:',
            '::b:::::::XX^X :   :',
            '::::X X::::::::::  :',
            ':  :X X?:   :^  b:::',
            ':  ::j::  :::  :: X:',
            ':    :   b: :  : X :',
            ':^U  D  :::   : X ?:',
            '::::::::::::::::::::',

        )

        self.floor_plans.append(new_floor_plan)

        # Hello Kitty
        new_floor_plan = (

            '::::::::::::::::::::',
            ':+   ;             :',
            ':    :     :::     :',
            ':    :     ;       :',
            ':    :     :::  k  :',
            ':::::::::: :       :',
            ':          ::      :',
            ':          ::;::::::',
            '::::       :  :    :',
            ':- :::  l  :  ;    :',
            ':  :       :  :    :',
            ':  :      :::::    :',
            ':K :               :',
            ':  ;    S          :',
            ':  :       :::     :',
            ':  :   ::::: :::   :',
            ':  :   :   :       :',
            ':  :   :           :',
            ':  :   :          @:',
            '::::::::::::::::::::',

        )

        self.floor_plans.append(new_floor_plan)

        # The Final Countdown
        new_floor_plan = (
            '::::::::::::::::::::',
            ':+   ;             :',
            ':    :    ::       :',
            ':    :    ::       :',
            ':    ::::    ::    :',
            ':    :@ :    ::    :',
            ':K   :  :          :',
            '::::::  ;      S   :',
            ':-   :  :          :',
            ':::  :  :          :',
            ': :  ::::::::::::: :',
            ':    :        :    :',
            ': : l;        :    :',
            ': :  :        :    :',
            ': :  :::::::  k  :::',
            ': :        :   : :j:',
            ': :::::::::::: ::: :',
            ':                  :',
            ':                  :',
            '::::::::::::::::::::',

        )

        self.floor_plans.append(new_floor_plan)

        # The Tower Top
        new_floor_plan = (

            '~~~~~~~~~~~.~~~~~~~~',
            '~~.~~~~~.~~~~~~.~~~~',
            '~~~~~.~~~~~~.~~~~~~~',
            '~~~~~~~~~~~~~~~~~.~~',
            '.~~~~:::::::::~~~~~~',
            '~~~~::  :-:  ::~.~~~',
            '~.~~:   : :   :~~~~~',
            '~~~~:  :: ::  :~~~.~',
            '~~~~:         :~~~~~',
            '~~~~:         :~~.~~',
            '~~~~:         :~~~~~',
            '~~.~:    G    :~.~~~',
            '.~~~: @@:2:@@ :~~~.~',
            '~~~~:: ::::: ::~~~~~',
            '~~~~~:::::::::~~~~~~',
            '~~.~~~~~~~~~~~~~~.~~',
            '~~~~~~~.~~.~~~.~~~~~',
            '~~~~.~~~~~~~~~~~~~~~',
            '~.~~~~~~~~~.~~~~.~~~',
            '~~~~~~.~~~~~~~~~~~~~',

        )

        self.floor_plans.append(new_floor_plan)

        # Floor Test
        new_floor_plan = (
            '::::::::::::::::::::',
            ':      SYlk / UO$  :',
            ':       b      b   :',
            ':                  :',
            ':  :^:^::          :',
            ':  ::^::^         ##',
            ':  TTb:::b    A    #',
            ':  :::::^       ####',
            ':  ::^:^:      ## ##',
            ':   qi    2     #  #',
            ':   I              #',
            ':    Z        Z    :',
            ':                  :',
            ':        A         :',
            ':         i        :',
            ':        iqI   %   :',
            ':    b         b   :',
            ':     ::::d::::    :',
            ':3    :       :    :',
            '::::::::::::::::::::',
        )

        self.floor_plans.append(new_floor_plan)


        # Cave Entrance
        new_floor_plan = (
            '####################',
            '##   #######   :**##',
            '#     #  ##    :   #',
            '#  #  #   #  # D |%#',
            '## #      #W#  :   #',
            '##         #   :@  #',
            '##    ##      ###/##',
            '##U# ####    ##W####',
            '#  #  ##    ##     +',
            '#3 #  ##   ##     ##',
            '#2##   #  ##     ###',
            '###       #   # #W##',
            '##        #  # #   #',
            '##  #  #  #  #     #',
            '#  ## ## ##     ## #',
            '#  ## ##  ##   #   #',
            '#     #     ###    #',
            '##    #           ##',
            '#?   ### ##      ###',
            '####################',

        )
        self.floor_plans.append(new_floor_plan)

        # Underground River
        new_floor_plan = (
            '#############W######',
            '##         #WW#   ##',
            '#         :::::    #',
            '#          ___     #',
            '#         :::::  [ #',
            '##    [    WW    [ #',
            '##   [[   WW    [[[#',
            '#    [[  WW    [ [[#',
            '-       WWWW       +',
            '#        WWW      ##',
            '##      WWW      ###',
            '##       WWW      ##',
            '#         W       ##',
            '#         W    [   #',
            '#        WWW  [[   #',
            '#       WW#W   [[  #',
            '#      WW##WW      #',
            '#     WW####W      #',
            '##  ,#W#####W#     #',
            '######W#####W#######',

        )

        self.floor_plans.append(new_floor_plan)

        # Lava flow
        new_floor_plan = (
            '#########HH#########',
            '#-      HH        ##',
            '#       H          #',
            '#       HH  HH  HH #',
            '#        H   HHHH  #',
            '#        H    H    #',
            '##      HH  HHH   ##',
            '##     HH    H   ###',
            '##   HHH     HH  ###',
            '#   HH        HH  ##',
            '#  HHHH        H   #',
            '#  HHHH        H   #',
            '#   HH   H_H  HH   #',
            '#       HH_H  H    #',
            '##      HH HHHH  ###',
            '##     HHH HHH    ##',
            '#    HHHH   HH     #',
            '#   HHHH     HH    #',
            '#HHHHH@*****%HH,  +#',
            'HHH###########HH####',

        )

        self.floor_plans.append(new_floor_plan)

        # Collossal Cave
        new_floor_plan = (
            '####################',
            '####            ####',
            '###              ###',
            '##  W             ##',
            '#  WWW        W    #',
            '#    W       WW    #',
            '#       ##    WW   #',
            '#    [  ##    WW[[ #',
            '-   [[         W [ +',
            '#  [[[[    [[    [[#',
            '#     [   [[     [ #',
            '#             ##   #',
            '#  ##   W     ##   #',
            '#  ##   WW    ##   #',
            '#     WWWWWW       #',
            '#       W          #',
            '##                ##',
            '###         [[   ###',
            '####       [[[[ ####',
            '####################',

        )

        self.floor_plans.append(new_floor_plan)

        # Ancient Lake
        new_floor_plan = (
            '#########WWWWWWWWWWW',
            '#######sWWWWWWWWWWWW',
            '###   sWWWWWWWWWWWWW',
            '##    sWWWWWWWWWWWWW',
            '#    sWWWWWWWWWWWWWW',
            '#    sWWWWWWWWsssWWW',
            '#    sWWWWWWWss:ssWW',
            '#   sWWWWWWWss: :sWW',
            '#   sWWWWWWWs:: :sWW',
            '-   s,,_____ss +:sWW',
            '#   sWWWWWWWs:: :sWW',
            '#   sWWWWWWWss: :sWW',
            '#   sWWWWWWWWss:ssWW',
            '#   sWWWWWWWWWsssWWW',
            '#    sWWWWWWWWWWWWWW',
            '#    sWWWWWWWWWWWWWW',
            '#:   sWWWWWWWWWWWWWW',
            '#::   sWWWWWWWWWWWWW',
            '#,;;   sWWWWWWWWWWWW',
            '#########WWWWWWWWWWW',
        )

        self.floor_plans.append(new_floor_plan)

        # Switch Maze
        new_floor_plan = (
            '####################',
            '#  _, :    :     ::#',
            '# ::  :    :      :#',
            '#  :  :_::D: :::D::#',
            '#: :  :,:  :  :    #',
            '#  :    :  ;  :    #',
            '# :: ::::::::::    #',
            '#  :       :       #',
            '#: :       :  ::: :#',
            '-  :::::  :: :   : +',
            '#:,:XX::  :@ :   : #',
            '# ::XU b  :: : : : #',
            '# %:XX  :  : : : : #',
            '#  :,?@:?::: : : : #',
            '#   ::: ::   : :   #',
            '#            : :   #',
            '#  :::  ::: :   :Z:#',
            '#     ::   :     :@#',
            '#:  Z    Z    Z    #',
            '####################',

        )

        self.floor_plans.append(new_floor_plan)

        # No Where to go
        new_floor_plan = (
            '####################',
            '#;;;@:**::;;;:::;;;#',
            '#;::::::XXX:;;;;;:;#',
            '#;;;;;;:XXX::::::*;#',
            '#::;::;;XXX;::ZZZ:;#',
            '#;:;:*:;:::;::ZZZ:;#',
            '#;;;:::;;;:;:;ZZZ:;#',
            '#;::;;;::;:;:;:::;;#',
            '#;::;:;: / ::;::;;:#',
            '-;;;;;;: % ;;;::;:;+',
            '#;::::;: U ::;::;:;#',
            '#;::@:;::::::;;:;:;#',
            '#;:;;::*:;:;;;::;:;#',
            '#;:;::;::;:;::::;:;#',
            '#;:;:;;::;:;;;;:;:;#',
            '#;:;;;::AAA:::;:;;@#',
            '#;:::;::AAA::::*:*:#',
            '#;:;;;:;AAA:;;;:::;#',
            '#;;;:;;;::;;;:;;;;;#',
            '####################',
        )

        self.floor_plans.append(new_floor_plan)

        # Marble Hall
        new_floor_plan = (
            '::::::::::::ssWWWWWW',
            ':         ::ssWWWWWW',
            ':         :::ssWWWWW',
            ':     £    ::ssWWWWW',
            ':          :::ssWWWW',
            ':     :::::::::ssWWW',
            ':     :]]]]]]::sssWW',
            ':     :]]]]]]:::ssWW',
            ':     :]]]]]] ::ssWW',
            '-     _]]]]]]G2:ssWW',
            ':     :]]]]]] ::ssWW',
            ':     :]]]]]]:::ssWW',
            ':     :]]]]]]::ssWWW',
            ':     :::::::::ssWWW',
            ':          :::ssWWWW',
            ':          ::ssWWWWW',
            ':     ,    ::ssWWWWW',
            ':         :::ssWWWWW',
            ':         ::ssWWWWWW',
            '::::::::::::ssWWWWWW',
        )

        self.floor_plans.append(new_floor_plan)

        # Frost Ward
        new_floor_plan = (
            'IIIIIIIIIIIIIIIIIIII',
            'I3IIii  0000    iIII',
            'I iii  t0 %0   iiI I',
            'I i     0 00t iiII I',
            'I     t       IIII I',
            'I   t     t    II  0',
            'Ii                i0',
            'Iii         t    ii0',
            'IIi     ii      0000',
            'IIi  t iiiI        +',
            'IIi    qi2I     0000',
            'Iii     iii   t  ii0',
            'Ii        i       i0',
            'I    t             0',
            'I      t    t      I',
            'I  t           t   I',
            'Ii       t        iI',
            'Iii   t          iiI',
            'IIii           iiiII',
            'IIIIIIIIIIIIIIIIIIII',

        )

        self.floor_plans.append(new_floor_plan)

        # Ice Fort
        new_floor_plan = (
            'IIIIIIIIIIIIIIIIIIII',
            'IIIIIIIIiiiiiiiIIIII',
            'IIIIIiiii00000iiiIII',
            'IIIIiii000   000iiII',
            'IIIiii00       00iiI',
            'IIiii00         00iI',
            '0Iiii0           0iI',
            '0Iii00           00I',
            '00000     000    00I',
            '-         0t0    +0I',
            '00000     000    00I',
            '0Iii00           00I',
            '0Iiii0           0iI',
            'IIiii00         00iI',
            'IIIiii00       00iiI',
            'IIIIiii000   000iiII',
            'IIIIIiiii00000iiiIII',
            'IIIIIIIiiiiiiiiIIIII',
            'IIIIIIIIIIIIIIIIIIII',
            'IIIIIIIIIIIIIIIIIIII',
        )

        self.floor_plans.append(new_floor_plan)

        # Deception
        new_floor_plan = (
            '00000000000000000000',
            '0} D    iii    ii0}0',
            '0000            i0 0',
            '0ii  000000000   0D0',
            '0i   0?  0  ?0     0',
            '0        0         0',
            '0                  0',
            '0 0    00 00    0  0',
            '0 0i   0   0   i0  0',
            '0 000000 - 000000 i0',
            '0 0?  i0   0i  ?0 i0',
            '0 0    00000    0 i0',
            '0                  0',
            '0                  0',
            '0     0000000      0',
            '0i    0  0  0      0',
            '0ii      0       0D0',
            '0000    i0i     i0 0',
            '0} D   ii0ii   ii0}0',
            '00000000000000000000',

        )

        self.floor_plans.append(new_floor_plan)

        # Ice Throne
        new_floor_plan = (
            '00000000000000000000',
            '0                  0',
            '0}0             0 ?0',
            '000             0000',
            '0i  00  00  00    i0',
            '0   00  00  00     0',
            '0                  0',
            '0     ii      ]]0000',
            '00     iii    ]]iii0',
            '      ii i   ]]iiI00',
            '-    ii  iii ]]iiI00',
            '    ii    ii  ]]iii0',
            '00   i        ]]0000',
            '0                  0',
            '0   00  00  00     0',
            '0i  00  00  00    i0',
            '000             0000',
            '0}0             0 @0',
            '0               D  0',
            '00000000000000000000',

        )

        self.floor_plans.append(new_floor_plan)

        # Prison of Ice
        new_floor_plan = (
            '00000000000000000000',
            '0?               i?0',
            '0                 i0',
            '0  00D0000D00D000  0',
            '0  0   ii   0   0  0',
            '0  0   i    0  i0  0',
            '0  0   i   i0  i0  0',
            '0  0i }i  ii0  }0  0',
            '0  0000q0000q0000  0',
            '0                  0',
            '0                  0',
            '0  00000q000q0000  0',
            '0  0i  }0i @0} i0  0',
            '0  0   i0   0  i0  0',
            '0  0    0   0   0  0',
            '0  0?   0   0   0  0',
            '0  00D0000D0000D0  0',
            '0                  0',
            '0-                ?0',
            '00000000000000000000',

        )

        self.floor_plans.append(new_floor_plan)

        # Dungeon of the Damned
        new_floor_plan = (
            '00000000000000000000',
            '0-i0ii         0ii?0',
            '0  0i       q  0 ii0',
            '0  0      ii0i 0  q0',
            '0  0     ii 0iq0   0',
            '0    0 iiii 0iii   0',
            '0    0ii   ,0iiii i0',
            '0   i000000000000000',
            '0  iiiiiiiiiiiiiiii0',
            '0i  qi qi qi qi qii0',
            '000iiiiiiiiiiiiiiii0',
            '0i  i000000000000D00',
            '0   i0i      iii0 @0',
            '0   i0      iiiq0  0',
            '0    0   0 iiiii0  0',
            '0 0000   0 iiii%0  0',
            '0    0   0 iiiii0  0',
            '0        0  iiiq0  0',
            '0i      i0   ___0 +0',
            '00000000000000000000',

        )
        self.floor_plans.append(new_floor_plan)

        # Lair of the Ice Beast
        new_floor_plan = (
            '0000iiiiiiiiiiii0000',
            '0+ 00i    iiiii00  0',
            '0   0q     i  q0   0',
            '00  i             00',
            'i00ii   0 0      00i',
            'iiqii   0 0i     qii',
            'ii     00D000     ii',
            'i     i0i  @0ii    i',
            'ii  0000    0000   i',
            'iii 0000    0000   i',
            'i/i    0%  i0      i',
            'i8i    000000     ii',
            'i8i      00i      ii',
            'ii       00      iii',
            'iiq      00      qii',
            'i00i             00i',
            '00 ii             00',
            '0  i0qi    i  q0   0',
            '0? 00iiiiiii ii00 -0',
            '0000iiiiiiiiiiii0000',

        )

        self.floor_plans.append(new_floor_plan)


        # Frost Top
        new_floor_plan = (
            '~~~~~~~~~~~~~~~~~~.~',
            '~~~.~~~~~~~~.~~~.~~~',
            '.~~~~~~~~00~~~~~~~~~',
            '~~~~~.~~0000~~.~~~~.',
            '~.~~~~~00 -00~~~~~~~',
            '~~~.~~00j  j00~~~.~~',
            '~~~~~00      00~~~~~',
            '~~0000        0000~~',
            '~~0iiiq]]]]]]qiii0~~',
            '~~0iii]]]]]]]]iii0~~',
            '.~0iGi]]]]]]]]i2i0~~',
            '~~0iiiq]]]]]]qiii0~~',
            '~~0000        0000~~',
            '~~~~~00      00~~~~~',
            '~~~~~~00    00~~~~~~',
            '~.~~~~~00@@00~~.~~.~',
            '~~~~~~~~0000~~~~~~~~',
            '~~~~~~~~~00~~~.~~~~~',
            '~~.~~~~~~~~~~~~~~.~~',
            '~~~~~~~~~~~~~~~~~~~~',

        )

        self.floor_plans.append(new_floor_plan)

        # chaos
        new_floor_plan = (

            ':H::?  !::::   :::::',
            ':HH:::    :    :q j:',
            '::HHH    |:|       :',
            ':HHHH     :    H   :',
            ':H    H  ::   HHH:::',
            ':H    HH    HHHHHH::',
            'HHH    HH  H:::ssHH:',
            ' HH  HHHH   :q  ssHH',
            '      HHHH  D   sssH',
            '   !   HH   :   s+sH',
            '!     HHHH  :q  ssHH',
            '3      HH  H:::ssHH:',
            '!      H    HHHHHH::',
            '       H     HHHH:::',
            '  q q         HH   :',
            ' :: ::             :',
            'H:   :           ! :',
            'H:  2:H HH    ::   :',
            'H:::::HHHHH   :J  q:',
            'HHHHHHHHHHHHHH::::::',

        )

        self.floor_plans.append(new_floor_plan)

        # ceaseless discharge
        new_floor_plan = (
            '::::HHHH::::HHHHHHHH',
            '- :HHHHHH@:HHHHH:::H',
            '  :HHHHHHH:HHHHHD%:H',
            '  :jHH:HHHHHHHHH:::H',
            '  :::::HHHHHHHHHHH:H',
            '  :HHH:HHHHH::HHHH:H',
            '  :HHHHHH:HH::HHH::H',
            '  :HHHHHH::::::HHHHH',
            '  qHHHHHH: ?:HHHHHHH',
            'HHHHHHHHHH  :HHHHHHH',
            'HHHHHHHHHHH :HHHHHHH',
            'HHHHHHHHHHHH;HHHHHHH',
            'HHHHHHHHHHH:::HHHHHH',
            'HHHHHHHHHHHHHHHHHHHH',
            'HHHHHHHHHHHHHHHHHHHH',
            'HHHHHHH:HHHHHHH:HHHH',
            'H:HH::::HHH::HH::HH:',
            'H:J :HHHHHHH::H:::::',
            'H::::HHHHHHHHHHHH   ',
            'HHHHHHHHHHHHHHHH@: +',

        )

        self.floor_plans.append(new_floor_plan)

        # Furnace Steps
        new_floor_plan = (
            ':HH:::::::::::::::::',
            ':HH:@         @::HH:',
            'HH :           :HHH:',
            'HH             :HHH:',
            'HH             :HHH:',
            ':HH     :  ::  :::::',
            ':HH    ::   :H     :',
            '::HH   H:   :H     :',
            ' ::HH  H:  ::H     :',
            '+ ::HHHH:  :HHH    H',
            '   DHHHH:  :HHH    H',
            '  ::HHHH:  ::HH  HHH',
            ':::HH  ::   :HHH  HH',
            ':HHH    :   :H    HH',
            ':HH        ::     HH',
            'HHH             : :H',
            'HH   :::::    HH: :H',
            'HH   :HHH:   HHH: ::',
            'Hj  ?:HHH: HHHHH:   ',
            'H:::::::::::::HH:  -',

        )

        self.floor_plans.append(new_floor_plan)


        # Forge of Giants
        new_floor_plan = (
            'HH::::::HH::::::::HH',
            'HH:    ;HH:% £  £:HH',
            ':::    :HH:£   £ :HH',
            ':    :::HH::::£ ?:HH',
            ':    :HHHHHHH::D::::',
            ':    :HHH/HHH:     :',
            ':    :::::::::     :',
            ':                  :',
            ':                  :',
            ':::q  ::::      q:::',
            '-     :HH::      D +',
            ':::q  :HHH::    q:::',
            ':?    :HHHH:       :',
            ':     ::::::       :',
            ':                 J:',
            ':                 ::',
            ':::    q   q     ::H',
            'HH:    :::::     :HH',
            'HH:    :HHH:   :::HH',
            'HH::::::HHH:::::HHHH',

        )

        self.floor_plans.append(new_floor_plan)


        # The crucible
        new_floor_plan = (
            'HHHHHHHHHHHHHHHHHHHH',
            'HHHHHHHHHHHHHHHHHHHH',
            'HHHHHHHH:::::HHHHHHH',
            'HHHHH::::   :::HHHHH',
            'HHH:::        :::HHH',
            'HH::            ::HH',
            'HH:              :HH',
            'H::              ::H',
            'H:      :::::     :H',
            '::q     :HHH:    q::',
            '+        HjH       -',
            '::q     :HHH:    q::',
            'H:      :::::     :H',
            'H::              ::H',
            'HH:              :HH',
            'HH::            ::HH',
            'HHH:::        :::HHH',
            'HHHHH::::   :::HHHHH',
            'HHHHHHHH:::::HHHHHHH',
            'HHHHHHHHHHHHHHHHHHHH',

        )

        self.floor_plans.append(new_floor_plan)

        # The Pyre
        new_floor_plan = (
            ':::q        HH::HHHH',
            ':,:          ?:HHHH:',
            ': D   :::::  ::HHHH:',
            ':::   :      :%HHHH:',
            '- :  ::      :HHHj::',
            ': :  :   :H  ;HHH::H',
            ': :  ::  :HH::HH::HH',
            ': :   :  ::::HHH:HH:',
            '  :   :   HHHHH::H::',
            '  ::  :  HHHHHH:_H + ',
            ':  :  : HHHHHHH::H::',
            ':  :  :::::::HHH:HH:',
            ':  :        ::HH::HH',
            ':  :         :HHH::H',
            ': ::::q      :HHHH::',
            ':  :     ::: ::HHHH:',
            ':  q    ::_::::HHHH:',
            ':      ::HHH:::HHHH:',
            ':     ::HHJHH:::HHH:',
            ':::::::HHHHHHH:::HHH',

        )

        self.floor_plans.append(new_floor_plan)

        # Hell's Gate
        new_floor_plan = (
            ':::::::HH:::::::::::',
            '::   ::HH:@       ::',
            ':     :HH:        @:',
            ':     :HH:   ::::  :',
            ':    ::HH::  :HH:  :',
            ':   ::HHHH:: :HH:  :',
            ':   :jHHHHj: :HH:  :',
            ':   :HHHHHH: ::::  :',
            ':q q::_HH_::q ::   :',
            '::   ::::::      q::',
            '+    ::::::        -',
            ':: q::_HH_::q    q::',
            ':q  :HHHHHH:       :',
            ':   :jHHHHj:       :',
            ':   ::HHHH::     :::',
            ':    ::HHH:::::  :HH',
            ':     :HH::::H:: :HH',
            ':     :HH:::HHH: :::',
            '::   ::HH:::H,H:   :',
            ':::::::HH:::HHH;;:::',

        )

        self.floor_plans.append(new_floor_plan)


        # Fire Throne
        new_floor_plan = (
            'HHHHHHHHHH   HHHHH  ',
            ':HHHHHHHHHH HHHHHHH ',
            '::HHHHHHHHHHHHHHHHHH',
            ' ::HHHH::HHHHHH:HHHH',
            '  ::HH::::HHHHH:HHHH',
            '   :HH:  :HHHHH:HHHH',
            '   :HH:  :HHH:::::HH',
            '   :HH:  :HH::q]]:HH',
            '  q::::  :::::]]]:HH',
            '-             ]]2:HH',
            '              ]]G:HH',
            '  q::::  :::::]]]:HH',
            '   :HH:  :HH::q]]:HH',
            '   :HH:  :HHH:::::HH',
            '   :HH:  :HHHHH:HHHH',
            '  ::HH::::HHHHH:HHHH',
            ' ::HHHH::HHHHHH:HHHH',
            '::HHHHHHHHH HHHHHHH ',
            ':HHHHHHHHH   HHHHH  ',
            'HHHHHHHHH     HHHHH ',

        )

        self.floor_plans.append(new_floor_plan)
