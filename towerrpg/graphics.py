__author__ = 'user'

import logging
import os.path
import time

import pygame

from towerrpg import game


class Colours:
    # set up the colours
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (237, 28, 36)
    GREEN = (34, 177, 76)
    BLUE = (63, 72, 204)
    GREY = (30, 30, 30)
    GREY = (40, 40, 40)
    GOLD = (255, 201, 14)


class TileFileNames:
    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    files = {

        game.Floor.BANG: "bang.png",
        game.Floor.BEACH: "beach.png",
        game.Floor.BEHOLDER: "beholder.png",
        game.Floor.BITER: "biter.png",
        game.Floor.BLUE_POTION: "blue_potion.png",
        game.Floor.BOMB: "bomb1.png",
        game.Floor.BOMB_LIT: "bomb2.png",
        game.Floor.BOSS_DOOR: "boss_door.png",
        game.Floor.BOSS_KEY: "boss_key.png",
        game.Floor.BRAZIER: "brazier.png",
        game.Floor.BRAZIER_LIT: "brazier_lit.png",
        game.Floor.CAVE_WALL: "cave_wall.png",
        game.Floor.CHAOS_PORTAL: "chaos_portal.png",
        game.Floor.CHEQUER: "cheque2.png",
        game.Floor.CHICKEN: "chicken.png",
        game.Floor.CLOUD: "cloud.png",
        game.Floor.DOOR: "door.png",
        game.Floor.DEVIL: "devil.png",
        game.Floor.EMPTY: None,
        game.Floor.ENTRANCE: "entrance.png",
        game.Floor.ENTRANCE_TELEPORT: None,
        game.Floor.EXIT: "exit.png",
        game.Floor.EXIT_KEY: "exit_key.png",
        game.Floor.FAKE_EXIT: "exit.png",
        game.Floor.FROST_TREE: "frost_tree.png",
        game.Floor.FROST_WAND: "frost_wand.png",
        game.Floor.GOAL: "goal.png",
        game.Floor.GOBLIN: "goblin.png",
        game.Floor.GRAVE1: "grave1.png",
        game.Floor.GRAVE2: "grave2.png",
        game.Floor.HOUR_GLASS: "hour_glass.png",
        game.Floor.HP_POTION: "green_potion.png",
        game.Floor.ICE: "ice.png",
        game.Floor.KEY: "key.png",
        game.Floor.KITTY: "kitty.png",
        game.Floor.LAVA: "lava.png",
        game.Floor.LIGHTNING: "lightning.png",
        game.Floor.MAGNET: "magnet.png",
        game.Floor.PINK_POTION: "pink_potion.png",
        game.Floor.PLAYER: "player.png",
        game.Floor.RED_POTION: "red_potion.png",
        game.Floor.SAFETY: None,
        game.Floor.SECRET_WALL: "brick.png",
        game.Floor.SHIELD: "shield.png",
        game.Floor.SKELETON: "skeleton.png",
        game.Floor.SKY: "sky.png",
        game.Floor.SLIME: "slime.png",
        game.Floor.SNOW: "snow.png",
        game.Floor.SNOW_BEAST: "snow_beast.png",
        game.Floor.SNOW_TREE: "snow_tree2.png",
        game.Floor.STONE: "stone.png",
        game.Floor.SWITCH: "switch.png",
        game.Floor.SWITCH_LIT: "switch_lit.png",
        game.Floor.SWORD: "sword.png",
        game.Floor.TELEPORT1: "teleport1.png",
        game.Floor.TELEPORT2: "teleport2.png",
        game.Floor.TRAP: "trap.png",
        game.Floor.TREASURE: "treasure.png",
        game.Floor.TREASURE_CHEST: "treasure_chest.png",
        game.Floor.TREE: "tree.png",
        game.Floor.WALL: "brick.png",
        game.Floor.WATER: "water.png",
        game.Floor.WELL: "well.png",
        game.Floor.YELLOW_POTION: "yellow_potion.png"

    }


class FloorView:
    images = {}
    tile_width = 32
    tile_height = 32

    def __init__(self, floor: game.Floor):
        self.floor = floor

    @staticmethod
    def initialise():

        for object in TileFileNames.files.keys():
            logging.info("Initialising %s", object)
            filename = TileFileNames.files[object]
            if filename is not None:
                filename = TileFileNames.RESOURCES_DIR + TileFileNames.files[object]
                image = pygame.image.load(filename)
                image = pygame.transform.scale(image, (FloorView.tile_width, FloorView.tile_height))
                FloorView.images[object] = image

                print("Loaded image {0} for object {1}".format(filename, object))
            else:
                FloorView.images[object] = None

    def draw(self, surface):

        player = self.floor.player

        for y in range(0, self.floor.height):
            for x in range(0, len(self.floor.plan[y])):

                tile = self.floor.get_tile(x, y)

                if tile not in FloorView.images.keys():
                    logging.warning("Found unknown tile '%s', using empty tile instead.", tile)
                    tile = game.Floor.EMPTY
                    self.floor.plan[x][y] = tile

                image = FloorView.images[tile]
                if image is not None:
                    surface.blit(image, (x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height))

                if tile == game.Floor.BOMB_LIT:
                    if (x, y) in self.floor.bombs.keys():
                        count = self.floor.bombs[(x, y)]
                        self.draw_text(surface, str(count), (x + 0.5) * self.tile_width, (y + 0.5) * self.tile_height,
                                       16)

        if self.floor.name is not None:
            self.draw_text(surface, "  " + self.floor.name + "  ", (self.floor.width * self.tile_width / 2),
                           surface.get_rect().top + 8, 24)

        if player is not None:
            if TileFileNames.files[game.Floor.PLAYER] is not None:
                image = self.images[game.Floor.PLAYER]
                surface.blit(image, (
                    player.x * self.tile_width, player.y * self.tile_height, self.tile_width, self.tile_height))

    def draw_text(self, surface, msg, x, y, size=32, fg_colour=Colours.WHITE, bg_colour=Colours.BLACK):
        font = pygame.font.Font(None, size)
        text = font.render(msg, 1, fg_colour, bg_colour)
        textpos = text.get_rect()
        textpos.centerx = x
        textpos.top = y
        surface.blit(text, textpos)


class ScoreView():
    effect_to_icon_map = {

        game.TowerRPG.SWORD: game.Floor.SWORD,
        game.TowerRPG.SHIELD: game.Floor.SHIELD,
        game.TowerRPG.FAST: game.Floor.HOUR_GLASS,
        game.TowerRPG.SLOW: game.Floor.HOUR_GLASS,
        game.TowerRPG.MAGNET: game.Floor.MAGNET,
        game.TowerRPG.FROST: game.Floor.FROST_WAND

    }

    def __init__(self, rpg: game.TowerRPG):
        self.rpg = rpg

    def draw(self, surface):

        font = pygame.font.Font(None, 24)
        name_font = pygame.font.Font(None, 32)
        spacing = 20

        frame = pygame.Rect(FloorView.tile_width * 20, surface.get_rect().top, 800 - FloorView.tile_width * 20, 800)

        name = name_font.render(self.rpg.player.name, 1, Colours.WHITE)

        if self.rpg.player.HP <= 3:
            fg = Colours.GREY
            bg = Colours.RED
        elif self.rpg.player.HP <= 5:
            fg = Colours.BLACK
            bg = Colours.GOLD
        else:
            fg = Colours.GREEN
            bg = Colours.GREY

        HP = font.render("    HP: %i    " % self.rpg.player.HP, 1, fg, bg)

        treasure = font.render("Treasure: %03i" % self.rpg.player.treasure, 1, Colours.RED)
        kills = font.render("Kills: %i" % self.rpg.player.kills, 1, Colours.BLUE)
        score = font.render("Score: %i" % self.rpg.player.score(), 1, Colours.GOLD)
        level = font.render("Level: %02i" % (self.rpg.current_floor_level + 1), 1, Colours.WHITE)
        elapsed_time = font.render(time.strftime("Time:%H:%M:%S", self.rpg.elapsed_time), 1, Colours.GREEN)

        textpos = name.get_rect()
        textpos.centerx = frame.centerx
        textpos.top = frame.top + 8
        texttop = textpos.top
        surface.blit(name, textpos)

        texttop += spacing + 10

        textpos = HP.get_rect()
        textpos.centerx = frame.centerx
        textpos.top = texttop
        surface.blit(HP, textpos)

        texttop += spacing

        textpos = treasure.get_rect()
        textpos.centerx = frame.centerx
        textpos.top = texttop
        surface.blit(treasure, textpos)

        texttop += spacing

        textpos = kills.get_rect()
        textpos.centerx = frame.centerx
        textpos.top = texttop
        surface.blit(kills, textpos)

        texttop += spacing

        textpos = score.get_rect()
        textpos.centerx = frame.centerx
        textpos.top = texttop
        surface.blit(score, textpos)

        texttop += spacing

        textpos = level.get_rect()
        textpos.centerx = frame.centerx
        textpos.top = texttop
        surface.blit(level, textpos)

        texttop += spacing

        textpos = elapsed_time.get_rect()
        textpos.centerx = frame.centerx
        textpos.top = texttop
        surface.blit(elapsed_time, textpos)

        texttop += spacing

        icon_slot_width = 8 + FloorView.tile_width
        icon_left = frame.left + 8

        if self.rpg.player.keys > 0:
            self.draw_icon(surface, icon_left, texttop, game.Floor.KEY, self.rpg.player.keys)
            icon_left += icon_slot_width

        if self.rpg.player.exit_keys > 0:
            self.draw_icon(surface, icon_left, texttop, game.Floor.EXIT_KEY, self.rpg.player.exit_keys)
            icon_left += icon_slot_width

        if self.rpg.player.boss_key == True:
            self.draw_icon(surface, icon_left, texttop, game.Floor.BOSS_KEY)
            icon_left += icon_slot_width

        if self.rpg.player.trophies > 0:
            self.draw_icon(surface, icon_left, texttop, game.Floor.GOAL, self.rpg.player.trophies)
            icon_left += icon_slot_width

        for effect in self.rpg.effects.keys():

            if effect in ScoreView.effect_to_icon_map.keys():

                self.draw_icon(surface, icon_left, texttop, ScoreView.effect_to_icon_map[effect],
                               self.rpg.effects[effect])
                icon_left += icon_slot_width

            else:
                logging.WARN("Effect %s has no icon!" % effect)

        texttop += spacing + FloorView.tile_height
        entry = font.render("High Score Table", 1, Colours.GOLD)
        textpos = entry.get_rect()
        textpos.centerx = frame.centerx
        textpos.top = texttop
        surface.blit(entry, textpos)

        for i in range(0, len(self.rpg.hst.table)):
            texttop += spacing
            name, score = self.rpg.hst.table[i]
            entry = font.render(name + ":" + str(score), 1, Colours.GOLD)
            textpos = entry.get_rect()
            textpos.centerx = frame.centerx
            textpos.top = texttop
            surface.blit(entry, textpos)

        if self.rpg.state == game.TowerRPG.GAME_OVER:
            font = pygame.font.Font(None, 60)
            state = font.render("  G A M E   O V E R  ", 1, Colours.BLACK, Colours.RED)
            textpos = state.get_rect()
            textpos.centerx = (self.rpg.current_floor.width * FloorView.tile_width / 2)
            textpos.centery = (self.rpg.current_floor.height * FloorView.tile_height / 2)
            surface.blit(state, textpos)

            if self.rpg.is_high_score():
                self.draw_text(surface=surface, msg="  ** A New High Score **  ",
                               fg_colour=Colours.BLACK, bg_colour=Colours.GOLD,
                               size=50,
                               x=self.rpg.current_floor.width * FloorView.tile_width / 2,
                               y=self.rpg.current_floor.height * FloorView.tile_height / 2 + 60)

        elif self.rpg.state == game.TowerRPG.FINISHED:
            font = pygame.font.Font(None, 60)
            state = font.render("  C O N G R A T U L A T I O N S  ", 1, Colours.BLACK, Colours.GOLD)
            textpos = state.get_rect()
            textpos.centerx = (self.rpg.current_floor.width * FloorView.tile_width / 2)
            textpos.centery = (self.rpg.current_floor.height * FloorView.tile_height / 2)
            surface.blit(state, textpos)

        elif self.rpg.state == game.TowerRPG.READY:
            font = pygame.font.Font(None, 60)
            state = font.render("  R E A D Y ?  ", 1, Colours.BLACK, Colours.GREEN)
            textpos = state.get_rect()
            textpos.centerx = (self.rpg.current_floor.width * FloorView.tile_width / 2)
            textpos.centery = (self.rpg.current_floor.height * FloorView.tile_height / 2)
            surface.blit(state, textpos)

            self.draw_text(surface=surface, msg="  Press 'N' to change player's name  ",
                           fg_colour=Colours.WHITE, bg_colour=Colours.BLACK,
                           size=40,
                           x=self.rpg.current_floor.width * FloorView.tile_width / 2,
                           y=self.rpg.current_floor.height * FloorView.tile_height - 50)

        elif self.rpg.state == game.TowerRPG.PAUSED:
            font = pygame.font.Font(None, 60)
            state = font.render("  P A U S E D  ", 1, Colours.BLACK, Colours.GREEN)
            textpos = state.get_rect()
            textpos.centerx = (self.rpg.current_floor.width * FloorView.tile_width / 2)
            textpos.centery = (self.rpg.current_floor.height * FloorView.tile_height / 2)
            surface.blit(state, textpos)

        if self.rpg.state in (
        game.TowerRPG.READY, game.TowerRPG.FINISHED, game.TowerRPG.GAME_OVER, game.TowerRPG.PAUSED):
            font = pygame.font.Font(None, 40)
            press_space = font.render("  Press SPACE to continue  ", 1, Colours.WHITE, Colours.BLACK)
            textpos = press_space.get_rect()
            textpos.centerx = (self.rpg.current_floor.width * FloorView.tile_width / 2)
            textpos.bottom = (self.rpg.current_floor.height * FloorView.tile_height)
            surface.blit(press_space, textpos)

    def draw_icon(self, surface, x, y, icon_name, count=None):

        if icon_name in FloorView.images.keys():

            image = FloorView.images[icon_name]
            iconpos = image.get_rect()
            iconpos.left = x
            iconpos.top = y
            surface.blit(image, iconpos)

            if count is not None:
                small_font = pygame.font.Font(None, 20)
                icon_count = small_font.render(str(count), 1, Colours.BLACK, Colours.WHITE)
                count_pos = icon_count.get_rect()
                count_pos.bottom = iconpos.bottom
                count_pos.right = iconpos.right
                surface.blit(icon_count, count_pos)

        else:
            logging.WARN("I can't find icon %s!" % icon_name)

    def draw_text(self, surface, msg, x, y, size=32, fg_colour=Colours.WHITE, bg_colour=Colours.BLACK):
        font = pygame.font.Font(None, size)
        text = font.render(msg, 1, fg_colour, bg_colour)
        textpos = text.get_rect()
        textpos.centerx = x
        textpos.centery = y
        surface.blit(text, textpos)
