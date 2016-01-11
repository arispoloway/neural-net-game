import os
import pygame
from pygame.locals import *
import random
import numpy as np
import time
#from visual import *
#from physutil import *
from math import *

SCREEN_HEIGHT = 700
SCREEN_WIDTH = 1200
NEW_TRACK_SEPARATION_DIST = 20

FPS = 60


black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 225)
purple   = ( 255,   0, 255)
grey     = ( 100, 100, 100)


background = black




class Player(object):
    MAX_SPEED = 50.0
    MAX_REVERSE_SPEED = -25.0
    MAX_OMEGA = pi / 4
    ALPHA_MAG = pi / 8
    ACCELERATION_MAG = 30.0
    BACKWARDS_ACCELERATION_MAG = -15.0
    DRAG = 1.0
    OMEGA_DRAG = pi / 4
    DEFAULT_COLOR = blue
    WIDTH = 20.0
    HEIGHT = 40.0
    EDGE_WIDTH = 2



    def __init__(self, to_draw, nn = None, color=DEFAULT_COLOR, x=0, y=0, theta=0):
        self.nn = nn
        self.to_draw = to_draw
        self.x = x
        self.y = y
        self.theta = 0
        self.omega = 0
        self.speed = 0
        self.tracks = []
        self.color = color


    def update(self, s):
        corners = self.get_corners()
        for track in self.tracks:
            for i in range(len(track.corners)-1):
                for j in range(len(corners) - 1):
                    if intersect(track.corners[i][0],track.corners[i][1], track.corners[i+1][0],track.corners[i+1][1], corners[j][0],corners[j][1], corners[j+1][0], corners[j+1][1]):
                        return
        if self.nn is not None:
            i = self.nn.output()
        else:
            keys = pygame.key.get_pressed()
            i = [0,0,0,0]
            if keys[pygame.K_UP] == True:
                i[0] = 1
            if keys[pygame.K_DOWN] == True:
                i[1] = 1
            if keys[pygame.K_LEFT] == True:
                i[2] = 1
            if keys[pygame.K_RIGHT] == True:
                i[3] = 1

        if i[0]:
            if self.speed <= Player.MAX_SPEED:
                self.speed += Player.ACCELERATION_MAG / s
        if i[1]:
            if self.speed  >= Player.MAX_REVERSE_SPEED:
                self.speed += Player.BACKWARDS_ACCELERATION_MAG / s
        if not (i[0] or i[1]):
            old_speed = self.speed
            if(self.speed > 0):
                self.speed -= Player.DRAG * sqrt(abs(self.speed)) / s
            else:
                self.speed += Player.DRAG * sqrt(abs(self.speed)) / s
            if abs(old_speed + self.speed) < (abs(old_speed) + abs(self.speed)):
                self.speed = 0.0


        if i[3] and not i[2]:
            if not self.omega >= Player.MAX_OMEGA:
                self.omega += self.ALPHA_MAG / s
        if i[2] and not i[3]:
            if not self.omega <= -Player.MAX_OMEGA:
                self.omega -= self.ALPHA_MAG / s

        if i[2] == i[3]:
            old_omega = self.omega
            if(self.omega > 0):
                self.omega -= Player.OMEGA_DRAG * sqrt(abs(self.omega)) / s
            else:
                self.omega += Player.OMEGA_DRAG * sqrt(abs(self.omega)) / s
            if abs(old_omega + self.omega) < (abs(old_omega) + abs(self.omega)):
                self.omega = 0.0

        self.theta += self.omega / s
        self.x += cos(self.theta) * self.speed / s
        self.y += sin(self.theta) * self.speed / s

        


    def get_corners(self):
        return [ \
            (self.x - Player.WIDTH / 2 * sin(-self.theta) - Player.HEIGHT / 2 * cos(-self.theta),   \
            self.y - Player.WIDTH / 2 * cos(-self.theta) + Player.HEIGHT / 2 * sin(-self.theta)), \
            (self.x - Player.WIDTH / 2 * sin(-self.theta) + Player.HEIGHT / 2 * cos(-self.theta),  \
            self.y - Player.WIDTH / 2 * cos(-self.theta) - Player.HEIGHT / 2 * sin(-self.theta)), \
            (self.x + Player.WIDTH / 2 * sin(-self.theta) + Player.HEIGHT / 2 * cos(-self.theta),  \
            self.y + Player.WIDTH / 2 * cos(-self.theta) - Player.HEIGHT / 2 * sin(-self.theta)), \
            (self.x + Player.WIDTH / 2 * sin(-self.theta) - Player.HEIGHT / 2 * cos(-self.theta),  \
            self.y + Player.WIDTH / 2 * cos(-self.theta) + Player.HEIGHT / 2 * sin(-self.theta)), \
        ]


    def draw(self, screen):
        if not self.to_draw:
            return

        corners = self.get_corners()
        for i in range(len(corners) - 1):
            pygame.draw.line(screen, self.color, corners[i], corners[i+1], Player.EDGE_WIDTH)
        pygame.draw.line(screen, self.color, corners[0], corners[-1], Player.EDGE_WIDTH)


            
class Track(object):
    TRACK_COLOR = purple
    TRACK_WIDTH = 2
    def __init__(self, corners):
        self.corners = corners

    def draw(self, screen):
        for i in range(len(self.corners) - 1):
            pygame.draw.line(screen, Track.TRACK_COLOR, self.corners[i], self.corners[i+1], Track.TRACK_WIDTH)



class Game(object):
    speed = 400
    min_distance = 200
    max_distance = 350


    def __init__(self, fps, tracks, players, finish_point, seed = 0):
        self.fps = fps
        self.seed = seed
        random.seed(seed)
        self.score = 0
        self.players = players
        self.tracks = tracks
        self.finish_point = finish_point
        for player in self.players:
            player.tracks = tracks

    def draw(self, screen):
        for track in self.tracks:
            track.draw(screen)
        for player in self.players:
            player.draw(screen)
        pygame.draw.line(screen, grey, (0, SCREEN_HEIGHT / 2), (SCREEN_WIDTH, SCREEN_HEIGHT / 2), 2)
        pygame.draw.line(screen, grey, (SCREEN_WIDTH/2, 0), (SCREEN_WIDTH/2, SCREEN_HEIGHT), 2)
        pygame.draw.circle(screen, green, self.finish_point, 20)

    def update(self):
        s = float(Game.speed) / self.fps

        for player in self.players:
            player.update(s)


    def isOver(self):
        return False


class Indicator(object):
    on_color = green
    off_color = red
    h = 10
    w = 10
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.h = Indicator.h
        self.w = Indicator.w
        self.indicated = False

    def indicate(self, game):
        self.indicated = False
        return -1

    def draw(self, screen):
        if self.indicated:
            c = Indicator.on_color
        else:
            c = Indicator.off_color
        pygame.draw.rect(screen, c, (self.x, self.y, self.w, self.h))

class PositionIndicator(object):
    def __init__(self):
        pass

    def indicate(self, game):
        return (game.player.y + game.player.h / float(2)) / 50

    def draw(self, screen):
        pass


def mod_sigmoid(x):
    return 1 / (1 + np.exp(-x))

class NeuralNetwork(object):
    def __init__(self, indicators, base_nn=None, hidden_layer_size=3, consec=0):
        self.indicators = indicators
        if base_nn == None:
            self.w1 = np.random.randn(len(self.indicators), hidden_layer_size)
            self.w2 = np.random.randn(hidden_layer_size, 2)
        else:
            if consec > 4:
                consec = 4
            self.w1 = base_nn.w1/(1 + consec) + np.random.randn(len(self.indicators), hidden_layer_size)/(5-consec)
            self.w2 = base_nn.w2/(1 + consec) + np.random.randn(hidden_layer_size, 2)/(5-consec)

    def output(self, game):
        o0 = np.array([j.indicate(game) for j in self.indicators])
        i1 = np.dot(o0, self.w1)
        o1 = mod_sigmoid(i1)
        i2 = np.dot(o1, self.w2)

        of = [0,0]
        if i2[0] > 0:
            of[0] = 1
        if i2[1] > 0:
            of[1] = 1
        return of

    def set_weight_1(self, weights):
        self.w1 = weights

    def set_weight_2(self, weights):
        self.w2 = weights

    def draw(self, screen):
        for i in self.indicators:
            i.draw(screen)

def get_fitness(seed, nn, fps):
    game = Game(seed, fps)
    while True:
        game.update()
        if game.isOver():
            return game.score


def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

def intersect(p0,p1,p2,p3):
    xdiff = (p0[0] - p1[0], p2[0] - p3[0])
    ydiff = (p0[1] - p1[1], p2[1] - p3[1]) #Typo was here

    div = det(xdiff, ydiff)
    if div == 0:
       return False
    return True


def dist(p1, p2):
    return sqrt(pow(p2[0] - p1[0], 2.0) + pow(p2[1] - p1[1], 2.0))

#copied from https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
def intersect(X1, Y1, X2, Y2, X3, Y3, X4, Y4):
    try:
        I1 = [min(X1,X2), max(X1,X2)]
        I2 = [min(X3,X4), max(X3,X4)]
        #Ia = [max( min(X1,X2), min(X3,X4) ), min( max(X1,X2), max(X3,X4))]
        if (max(X1,X2) < min(X3,X4)):
            return False
        A1 = (Y1-Y2)/(X1-X2) 
        A2 = (Y3-Y4)/(X3-X4)
        b1 = Y1-A1*X1
        b2 = Y3-A2*X3
        if (A1 == A2):
            return False
        #Ya = A1 * Xa + b1
        #Ya = A2 * Xa + b2
        #A1 * Xa + b1 = A2 * Xa + b2
        Xa = (b2 - b1) / (A1 - A2)
        if ( (Xa < max( min(X1,X2), min(X3,X4) )) or (Xa > min( max(X1,X2), max(X3,X4) )) ):
            return False
        else:
            return True
    except:
        return False


def run_game(players, fps, nn=None):
    pygame.init()
    pygame.display.set_caption("Neural Net Testing")
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.update()

    clock = pygame.time.Clock()
    pygame.mouse.set_visible(1)

    nn_on = (nn != None)
    running = True


    stage = 0 # stage 0 = setting up track, stage 1 = racing
    last_keys = pygame.key.get_pressed()
    last_mouse = pygame.mouse.get_pressed()
    tracks = []
    current_track = Track([])
    finish_point = [0,0]

    game = None


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()




        
        window.fill(background)

        if(stage > 0):
            if (game == None):
                game = Game(FPS, tracks, players, finish_point)
            game.update()
            game.draw(window)

            if game.isOver():
                running = False
                print(game.score)
        else:
            if mouse[0]:
                if not last_mouse[0]:
                    tracks.append(Track([mouse_pos]))
                if dist(tracks[-1].corners[-1], mouse_pos) > NEW_TRACK_SEPARATION_DIST:
                    tracks[-1].corners.append(mouse_pos)

            if mouse[1] and not last_mouse[1]:
                finish_point = mouse_pos

            if mouse[2] and not last_mouse[2]:
                stage += 1
            for track in tracks:
                track.draw(window)

        clock.tick(fps)
        pygame.display.update()

        last_mouse = mouse
        last_keys = keys
 


# seed = 1

# ai_on = True

# if ai_on:

#   first_generation_size = 20000
#   generation_size = 2000
#   top_choice_num = 6


    

#   indicators = [PositionIndicator()]

#   for x in range(150, 500, 75):
#       for y in range(100, 550, 50):
#           indicators.append(Indicator(x, y))


#   t = [time.time()]

#   i = [NeuralNetwork(indicators, None, 5) for j in range(first_generation_size)]
#   i = sorted(i, key=lambda x: get_fitness(seed, x, FPS), reverse=True)
#   n = i[0:top_choice_num]

#   t.append(time.time())
#   best = [get_fitness(seed,n[0],FPS)]
#   consec = 0

#   print(str(0) + " - " + str(t[-1] - t[-2]) + " - " + str(best[0]))

#   for j in range(1,20):
        
#       i = []
#       for k in n:
#           i.extend([NeuralNetwork(indicators, k, 5, consec) for q in range(int(generation_size/float(top_choice_num + 1)))])
#           i.append(k)
#       i.extend([NeuralNetwork(indicators, None, 5) for q in range(int(generation_size/float(top_choice_num + 1)))])

#       i = sorted(i, key=lambda x: get_fitness(seed, x, FPS), reverse=True)
#       n = i[0:top_choice_num]

#       t.append(time.time())
#       best.append(get_fitness(seed,n[0],FPS))
#       if best[-1] == best[-2]:
#           consec += 1
#       else:
#           consec = 0
#       print(str(j) + " - " + str(t[-1] - t[-2]) + " - " + str(best[-1]))

#   t1 = time.time()
#   print("Time to execute: " + str(t[-1] - t[0]))
#   print("Best distance:   " + str(get_fitness(seed,n[0],FPS)))
#   #print(n[0].w1)
#   #print(n[0].w2)


# game = Game(seed, FPS)

# if ai_on:
#   run_game(game, FPS, n[0])
# else:




run_game([Player(True, None, blue, SCREEN_WIDTH/2,SCREEN_HEIGHT/2,0)], FPS)




