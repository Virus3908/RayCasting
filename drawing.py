import pygame
from settings import *
from ray_casting import ray_casting
from map import mini_map
from os import path
from collections import deque
from random import randrange
import sys


img_dir = path.join(path.dirname(__file__), 'img')
sprite_dir = path.join(path.dirname(__file__), 'sprites')
snd_dir = path.join(path.dirname(__file__), 'sound')
font_dir = path.join(path.dirname(__file__), 'font')

class Drawing:
    def __init__(self, sc, sc_map, player, clock):
        self.sc = sc
        self.sc_map = sc_map
        self.player = player
        self.clock = clock
        self.font = pygame.font.SysFont('Arial', 36, bold = True)
        self.font_win = pygame.font.Font(path.join(font_dir, 'font.ttf'), 144)
        self.textures = {1:pygame.image.load(path.join(img_dir,'wall3.png')).convert(),
                         2:pygame.image.load(path.join(img_dir,'wall4.png')).convert(),
                         3:pygame.image.load(path.join(img_dir,'wall5.png')).convert(),
                         4:pygame.image.load(path.join(img_dir,'wall6.png')).convert(),
                         'S':pygame.image.load(path.join(img_dir,'sky1.png')).convert()
                          }
        # menu
        self.menu_trigger = True
        self.menu_picture = pygame.image.load(path.join(img_dir, 'bg.jpg')).convert()
        # weapon parameters
        self.weapon_base_sprite = pygame.image.load(path.join(sprite_dir,'weapons/shotgun/base/0.png')).convert_alpha()
        self.weapon_shot_animation = deque([
            pygame.image.load(path.join(sprite_dir,
                                        f'weapons/shotgun/shot/{i}.png')).convert_alpha()
                                           for i in range(20)])
        self.weapon_rect = self.weapon_base_sprite.get_rect()
        self.weapon_pos = (HALF_WIDTH - self.weapon_rect.width//2, HEIGHT - self.weapon_rect.height)
        self.shot_lenght = len(self.weapon_shot_animation)
        self.shot_lenght_count = 0
        self.shot_animation_speed = 3
        self.shot_animation_count = 0
        self.shot_animation_trigger = True
        self.shot_sound = pygame.mixer.Sound(path.join(snd_dir, 'shotgun.wav'))
        #sfx parameters
        self.sfx = deque([pygame.image.load(path.join(sprite_dir,
    f'weapons/sfx/{i}.png')).convert_alpha() for i in range(9)])
        self.sfx_lenght_count = 0
        self.sfx_lenght = len(self.sfx)
                         

    def background(self, angle):
        sky_offset = -20 * math.degrees(angle) % WIDTH
        self.sc.blit(self.textures['S'], (sky_offset, 0))
        self.sc.blit(self.textures['S'], (sky_offset + WIDTH, 0))
        self.sc.blit(self.textures['S'], (sky_offset - WIDTH, 0))
        pygame.draw.rect(self.sc, DARKGRAY, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    def world(self, world_objects):
        #ray_casting(self.sc, player_pos, player_angle, self.textures)
        for obj in sorted(world_objects, key=lambda n: n[0], reverse=True):
            if obj[0]:
                _, object, object_pos = obj
                self.sc.blit(object, object_pos)
    def fps(self, clock):
        display_fps = str(int(clock.get_fps()))
        render = self.font.render(display_fps, 0, RED)
        self.sc.blit(render, (WIDTH - 60, 5))

    def mini_map(self, player):
        map_x, map_y = player.x // MAP_SCALE, player.y // MAP_SCALE
        self.sc_map.fill(BLACK)
        pygame.draw.line(self.sc_map, YELLOW, (map_x, map_y),
                         (map_x + 30 * math.cos(player.angle),
                          map_y + 30 * math.sin(player.angle)),2)
        pygame.draw.circle(self.sc_map, RED, (int(map_x),int(map_y)), 4)
        for x, y in mini_map:
            pygame.draw.rect(self.sc_map, GREEN,(x, y, MAP_TILE, MAP_TILE))
        self.sc.blit(self.sc_map, MAP_POS)

    def player_weapon(self, shots):
        if self.player.shot:
            if not self.shot_lenght_count:
                self.shot_sound.play()               
            self.shot_projection = min(shots)[1] // 2
            self.bullet_sfx()
            shot_sprite = self.weapon_shot_animation[0]
            self.sc.blit(shot_sprite, self.weapon_pos)
            self.shot_animation_count += 1
            if self.shot_animation_count == self.shot_animation_speed:
                self.weapon_shot_animation.rotate(-1)
                self.shot_animation_count = 0
                self.shot_lenght_count += 1
                self.shot_animation_trigger = False
            if self.shot_lenght_count == self.shot_lenght:
                self.player.shot = False
                self.shot_lenght_count = 0
                self.sfx_lenght_count = 0##
                self.shot_animation_trigger = True
        else:
            self.sc.blit(self.weapon_base_sprite, self.weapon_pos)

    def bullet_sfx(self):
        if self.sfx_lenght_count < self.sfx_lenght:
            sfx = pygame.transform.scale(self.sfx[0], (self.shot_projection,
                                                       self.shot_projection))
            sfx_rect = sfx.get_rect()
            self.sc.blit(sfx, (HALF_WIDTH - sfx_rect.w//2,
                               HALF_HEIGHT - sfx_rect.h//2))
            self.sfx_lenght_count += 1
            self.sfx.rotate(-1)

    def win(self):
        render = self.font_win.render('YOU WIN!!!', 1, (randrange(40,120), 0, 0))
        rect = pygame.Rect(0,0, 1000, 300)
        rect.center = HALF_WIDTH, HALF_HEIGHT
        pygame.draw.rect(self.sc, BLACK, rect)
        render_rect = render.get_rect()
        render_rect.center = HALF_WIDTH, HALF_HEIGHT
        self.sc.blit(render, render_rect)
        pygame.display.update()
        self.clock.tick(15)

    def menu(self):
        x = 0
        button_font = pygame.font.Font(path.join(font_dir, 'font.ttf'), 72)
        label_font = pygame.font.Font(path.join(font_dir, 'font1.otf'), 400)
        start = button_font.render('START', 1, pygame.Color('lightgray'))
        button_start = pygame.Rect(0,0, 400, 150)
        button_start.center = HALF_WIDTH, HALF_HEIGHT
        exit = button_font.render('EXIT', 1, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0,0, 400, 150)
        button_exit.center = HALF_WIDTH, HALF_HEIGHT + 200

        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            start = button_font.render('START', 1, pygame.Color('lightgray'))
            exit = button_font.render('EXIT', 1, pygame.Color('lightgray'))
            
            self.sc.blit(self.menu_picture, (0,0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            x += 1

            pygame.draw.rect(self.sc, BLACK, button_start)
            self.sc.blit(start, (button_start.centerx - 130, button_start.centery - 70))

            pygame.draw.rect(self.sc, BLACK, button_exit)
            self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))

            color = randrange(40)
            label = label_font.render('DOOMPy', 1, (color, color, color))

            self.sc.blit(label, (15, -50))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if button_start.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_start)
                start = button_font.render('START', 1, WHITE)
                self.sc.blit(start, (button_start.centerx - 130, button_start.centery - 70))
                if mouse_click[0]:
                    self.menu_trigger = False
            elif button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_exit)
                exit = button_font.render('EXIT', 1, WHITE)
                self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()
                    
            pygame.display.update()
            self.clock.tick(30)


            
