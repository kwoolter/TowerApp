__author__ = 'user'

import sys

import pygame
from pygame.locals import *
import logging

from .graphics import *
from .game import *
from towerrpg import eztext

def main():

    logging.basicConfig(level = logging.WARN)
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()

    # Set-up the game window
    pygame.display.set_caption('The Tower')
    filename = TileFileNames.RESOURCES_DIR + "tower.png"
    image = pygame.image.load(filename)
    image = pygame.transform.scale(image, (FloorView.tile_width, FloorView.tile_height))
    pygame.display.set_icon(image)

    DISPLAYSURF = pygame.display.set_mode((800, 640))

    player = game.Player("Doran", 1, 2)
    rpg = game.TowerRPG(player, difficulty=game.TowerRPG.MEDIUM)
    FloorView.initialise()

    pygame.time.set_timer(USEREVENT + 1, rpg.difficulty)


    # main game loop
    while True:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    rpg.move_player(0, -1)
                elif event.key in (K_DOWN, K_s):
                    rpg.move_player(0, 1)
                elif event.key in (K_LEFT, K_a):
                    rpg.move_player(-1, 0)
                elif event.key in (K_RIGHT, K_d):
                    rpg.move_player(1, 0)
                elif event.key == K_SPACE:
                    if rpg.state in (game.TowerRPG.FINISHED, game.TowerRPG.GAME_OVER ):
                        rpg.initialise()
                    elif rpg.state == game.TowerRPG.READY:
                        rpg.state = game.TowerRPG.PLAYING
                    elif rpg.state == game.TowerRPG.PLAYING:
                        rpg.state = game.TowerRPG.PAUSED
                    elif rpg.state == game.TowerRPG.PAUSED:
                        rpg.state = game.TowerRPG.PLAYING
                elif event.key == (K_n) and rpg.state == game.TowerRPG.READY:
                    print("Change Character Name...")
                    txtbx = eztext.Input(maxlength=10, color=Colours.WHITE, font=pygame.font.Font(None, 24),
                                         x = (FloorView.tile_width * 20) + 8,
                                         y = 440,
                                         prompt='Name? ')
                    # create the pygame clock
                    clock = pygame.time.Clock()
                    # main loop!
                    loop = True
                    while loop:
                        # make sure the program is running at 30 fps
                        clock.tick(30)

                        # events for txtbx
                        events = pygame.event.get()
                        # process other events
                        for event in events:
                            # close it x button is pressed
                            if event.type == QUIT:
                                loop = False
                                break
                            elif event.type == KEYDOWN and event.key == K_RETURN:
                                print("Finished. Value={0}".format(txtbx.value))
                                player = game.Player(txtbx.value, 0, 0)
                                rpg.player = player
                                loop = False
                                break

                        # update txtbx
                        txtbx.update(events)
                        # blit txtbx on the sceen
                        txtbx.draw(DISPLAYSURF)
                        # refresh the display
                        pygame.display.flip()


            elif event.type == USEREVENT + 1:
                rpg.tick()

        # Now see if there has been a collision
        rpg.check_collision()

        # draw on the surface object
        DISPLAYSURF.fill(Colours.GREY)
        view = FloorView(rpg.current_floor)
        view.draw(DISPLAYSURF)

        score = ScoreView(rpg)
        score.draw(DISPLAYSURF)

        pygame.display.update()

    return


if __name__ == "__main__":
    main()
