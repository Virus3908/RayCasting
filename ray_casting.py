import pygame
from settings import *
from map import world_map, WORLD_WIDTH, WORLD_HEIGHT
from numba import njit



'''def ray_casting(sc, player_pos, player_angle):
    cur_angle = player_angle - HALF_FOV
    xo, yo = player_pos
    for ray in range(NUM_RAYS):
        sin_a = math.sin(cur_angle)
        cos_a = math.cos(cur_angle)
        for depth in range(MAX_DEPTH):
            x = xo + depth * cos_a
            y = yo + depth * sin_a
            #pygame.draw.line(sc, DARKGRAY, player_pos, (x,y))
            if (x// TILE * TILE, y// TILE * TILE) in world_map:
                depth *= math.cos(player_angle - cur_angle)
                proj_height = PROJ_COEF / depth
                c = 255/ (1 + depth * depth * 0.00002)
                color = (c, c // 2, c // 3)
                pygame.draw.rect(sc, color, (ray * SCALE,
                                             HALF_HEIGHT - proj_height // 2,
                                             SCALE, proj_height))
                break
        cur_angle += DELTA_ANGLE'''
@njit(fastmath = True)
def mapping(a,b):
    return (a // TILE) * TILE, (b // TILE) * TILE

@njit(fastmath = True)
def ray_casting(player_pos, player_angle, world_map):
    casted_walls = []
    ox, oy = player_pos#
    texture_v, texture_h = 1, 1
    xm, ym = mapping(ox,oy)
    cur_angle = player_angle - HALF_FOV#
    for ray in range(NUM_RAYS):
        sin_a = math.sin(cur_angle)
        sin_a = sin_a if sin_a else 0.000001
        cos_a = math.cos(cur_angle)
        cos_a = cos_a if cos_a else 0.000001
        x, dx = (xm+TILE, 1) if cos_a >=0 else (xm, -1)
        for i in range(0, WORLD_WIDTH, TILE):##
            depth_v = (x - ox) / cos_a
            yv = oy + depth_v * sin_a#
            tile_v = mapping(x + dx, yv)####
            if tile_v in world_map:#####
                texture_v = world_map[tile_v]####
                break
            x += dx * TILE

        y, dy = (ym+TILE, 1) if sin_a >=0 else (ym, -1)
        for i in range(0, WORLD_HEIGHT, TILE):##
            depth_h = (y - oy) / sin_a
            xh = ox + depth_h * cos_a#
            tile_h = mapping(xh, y + dy)####
            if tile_h in world_map:####
                texture_h = world_map[tile_h]###
                break
            y += dy * TILE

        depth, offset, texture = (depth_v, yv,
                         texture_v) if depth_v < depth_h else (depth_h,
                                                               xh, texture_h)
        offset = int(offset) % TILE
        depth *= math.cos(player_angle - cur_angle)
        depth = max(depth, 0.000001)
        proj_height = int(PROJ_COEF / depth)# изменение

        

        casted_walls.append((depth, offset, proj_height, texture))
        
        cur_angle += DELTA_ANGLE
    return casted_walls

def ray_casting_walls(player, textures):
    casted_walls = ray_casting(player.pos, player.angle, world_map)
    wall_shot = casted_walls[CENTER_RAY][0], casted_walls[CENTER_RAY][2]
    walls = []
    for ray, casted_values in enumerate(casted_walls):
        depth, offset, proj_height, texture = casted_values
        if proj_height > HEIGHT:
            coeff = proj_height / HEIGHT
            texture_height = TEXTURE_HEIGHT / coeff
            wall_column = textures[texture].subsurface(offset * TEXTURE_SCALE,
                                                       HALF_TEXTURE_HEIGHT - texture_height//2,
                                                       TEXTURE_SCALE, texture_height)
            wall_column = pygame.transform.scale(wall_column,
                                                     (SCALE, HEIGHT))
            wall_pos =(ray * SCALE, 0)
        else:
            wall_column = textures[texture].subsurface(offset * TEXTURE_SCALE, 0,
                                                 TEXTURE_SCALE, TEXTURE_HEIGHT)
            wall_column = pygame.transform.scale(wall_column,
                                                     (SCALE, proj_height))
            wall_pos =(ray * SCALE, HALF_HEIGHT - proj_height//2)
        walls.append((depth, wall_column, wall_pos))
    return walls, wall_shot
    