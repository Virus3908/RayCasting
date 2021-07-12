import pygame
import sys
#import math
from settings import *
from player import Player
#from map import world_map
from sprite_drawning import *
from ray_casting import ray_casting_walls
from drawing import Drawing
from interaction import Interaction

pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT))
sc_map = pygame.Surface(MINIMAP_RES)
clock = pygame.time.Clock()


sprites = Sprites()
player = Player(sprites)
drawing = Drawing(sc, sc_map, player, clock)
interaction = Interaction(player, sprites, drawing)

drawing.menu()
pygame.mouse.set_visible(False)
interaction.play_music()


while True:
    player.movement()
    drawing.background(player.angle)
    walls, wall_shot = ray_casting_walls(player, drawing.textures)
    drawing.world(walls +[obj.object_locate(player, walls)for obj in sprites.list_of_objects])
    drawing.fps(clock)
    drawing.mini_map(player)
    drawing.player_weapon([wall_shot, sprites.sprite_shot])

    interaction.interaction_objects()
    interaction.npc_action()
    interaction.clear_world()
    interaction.check_win()

    pygame.display.update()
    clock.tick()
