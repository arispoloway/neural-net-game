import os
import pygame
from pygame.locals import *
import random
import numpy as np
import time
from math import *
import pickle


from neuralnetwork import *
from intersections import *

SCREEN_HEIGHT = 900
SCREEN_WIDTH = 1700
NEW_TRACK_SEPARATION_DIST = 50
NUM_OUTPUTS = 4

FPS = 30


black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 225)
purple   = ( 255,   0, 255)
grey     = ( 100, 100, 100)


background = black




class Player(object):
    MAX_SPEED = 120.0
    MAX_REVERSE_SPEED = -50.0
    MAX_OMEGA = pi / 2
    ALPHA_MAG = pi / 2
    ACCELERATION_MAG = 125.0
    BACKWARDS_ACCELERATION_MAG = -75.0
    DRAG = 5.0
    OMEGA_DRAG = pi
    DEFAULT_COLOR = blue
    WIDTH = 20.0
    HEIGHT = 40.0
    EDGE_WIDTH = 2
    INDICATOR_ANGLES = np.arange(-pi/2 - .01, pi/2 + .01, pi/8)
    EXTRA_INDICATORS = 1
    INDICATOR_LENGTH = 400.0



    def __init__(self, to_draw, nn = None, x=0, y=0, theta = 0, color=DEFAULT_COLOR):
        self.nn = nn
        self.to_draw = to_draw
        self.x = x
        self.y = y
        self.theta = 0
        self.omega = 0
        self.speed = 0
        self.tracks = []
        self.color = color
        self.crashed = False
        self.score = 0
        self.indicator_collisions = []


    def update(self, s):
        if self.crashed:
            return
        corners = self.get_corners()
        for track in self.tracks:
            for i in range(len(track.corners)-1):
                for j in range(len(corners) - 1):
                    if alt_intersect(track.corners[i][0],track.corners[i][1], track.corners[i+1][0], \
                        track.corners[i+1][1], corners[j][0],corners[j][1], corners[j+1][0], corners[j+1][1]):
                        self.crashed = True
                        return

        if self.nn is not None:
            i = self.nn.output(self.indicate())
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

    def indicate(self):
        o = []
        for a in Player.INDICATOR_ANGLES:
            indicated = False
            distance = 9999999.9
            saved_pos = ()
            for track in self.tracks:
                for i in range(len(track.corners)-1):
                    point = self.find_indicator_point(a)
                    inter = intersect_dist(self.x, self.y, point[0], point[1],track.corners[i][0], track.corners[i][1], track.corners[i+1][0], track.corners[i+1][1] )
                    if inter != None:
                        indicated = True
                        if dist(inter, [self.x, self.y]) < distance:
                            saved_pos = inter
                            distance = dist(inter, [self.x, self.y])
            if indicated:
                self.indicator_collisions.append(saved_pos)
                o.append( (Player.INDICATOR_LENGTH * 2)/(distance))
            else:
                o.append(0.0)
        o.append(self.speed / Player.MAX_SPEED * 3.0)
        return o

    def find_indicator_point(self, angle):
        return (self.x + Player.INDICATOR_LENGTH * cos(self.theta + angle), self.y + Player.INDICATOR_LENGTH * sin(self.theta + angle))


    def draw(self, screen):
        if not self.to_draw:
            return

        corners = self.get_corners()
        for i in range(len(corners) - 1):
            pygame.draw.line(screen, self.color, corners[i], corners[i+1], Player.EDGE_WIDTH)
        pygame.draw.line(screen, self.color, corners[0], corners[-1], Player.EDGE_WIDTH)
        self.draw_indicators(screen)
            

    def draw_indicators(self, screen):
        for angle in Player.INDICATOR_ANGLES:
            pygame.draw.line(screen, self.color, (self.x, self.y), self.find_indicator_point(angle))
        indicated = self.indicate()[0:-2]
        for indication in self.indicator_collisions:
            pygame.draw.circle(window, white, (int(indication[0]), int(indication[1])), 7)
        self.indicator_collisions = []


            
class Track(object):
    TRACK_COLOR = purple
    TRACK_WIDTH = 2
    def __init__(self, corners):
        self.corners = corners

    def draw(self, screen):
        for i in range(len(self.corners) - 1):
            pygame.draw.line(screen, Track.TRACK_COLOR, self.corners[i], self.corners[i+1], Track.TRACK_WIDTH)



class Game(object):
    speed = 3.0
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
        s = self.fps / Game.speed

        for player in self.players:
            player.update(s)
        self.update_scores()


    def update_scores(self):
        for i, player in enumerate(self.players):
            #score = 1 / dist((self.finish_point[0], self.finish_point[1]), (player.x, player.y))
            if not player.crashed:
                self.players[i].score += (player.speed - abs(player.omega) * player.MAX_SPEED / player.MAX_OMEGA / 4)

            if player.crashed or player.speed < Player.MAX_SPEED / 10:
                self.players[i].score -= Player.MAX_SPEED/3

            #if self.scores[i] < score:
            #    self.scores[i] = score
            #player.score = score




    
    #Check if x and y values are in the range of both line segments




def create_players(neurals, starting_point):
    return [Player(False, neurals[i], starting_point[0], starting_point[1]) for i in range(len(neurals))]

MIN_MUTATION_AMOUNT = .1
MAX_MUTATION_AMOUNT = .4

def calculate_mutation_amount(scores):
    consec = sum([1 if in_range(scores[-1]-1, scores[-1]+1, score) else 0 for score in scores])
    return MIN_MUTATION_AMOUNT + (MAX_MUTATION_AMOUNT - MIN_MUTATION_AMOUNT) / (1 + np.exp(-(consec - 4)))



generations = 10
starting_generation = 200
generation_size = 100
time_per_generation = 300
survivors = 25

starting_point = [300,100]
finish_point = [0,0]

best_neurals = []

best_neural = None
best_neural = pickle.load(open("bestnn.nn", "rb"))
mode = 0
# 0 - train from scratch
# 1 - train from best_neural
# 2 - play with best neural
# 3 - play the game


pygame.init()
pygame.display.set_caption("Neural Net Testing")
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.update()

clock = pygame.time.Clock()
pygame.mouse.set_visible(1)

running = True

stage = 0 # stage 0 = setting up track, stage 1 = racing
last_keys = pygame.key.get_pressed()
last_mouse = pygame.mouse.get_pressed() 
tracks = []
scores = []

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
            count = 0
            if mode < 2:
                if mode == 1:
                    work_from_best_neural = False
                    neurals = [NeuralNetwork(len(Player.INDICATOR_ANGLES) + Player.EXTRA_INDICATORS, NUM_OUTPUTS, best_neural) for i in range(starting_generation)]
                else:
                    neurals = [NeuralNetwork(len(Player.INDICATOR_ANGLES) + Player.EXTRA_INDICATORS, NUM_OUTPUTS) for i in range(starting_generation)]


                for i in range(0,generations+1):
                    print("Generation: " + str(i))

                    players = create_players(neurals, starting_point)
                    game = Game(FPS, tracks, players, finish_point)


                    for j in range(time_per_generation):
                        if j % 25 == 0:
                            print("Generation: "+ str(i) + " - Frame: " + str(j))
                        game.update()

                    players = sorted(game.players[:], key=lambda x: x.score, reverse=True)[0:survivors]
                    neurals = [player.nn for player in players]

                    scores.append(players[0].score)
                    best_neurals.append(neurals[0])
                    best_neural = neurals[0]

                    mutation_amount = calculate_mutation_amount(scores)
                    print(mutation_amount)
                    while len(neurals) < generation_size:
                        neurals.append(breed_networks(random.choice(neurals), random.choice(neurals), mutation_amount))
                        #neurals.append(breed_networks(random.choice(neurals[0:survivors]), random.choice(neurals[0:survivors])))
                        #neurals.append(NeuralNetwork(len(Player.INDICATOR_ANGLES) + Player.EXTRA_INDICATORS, NUM_OUTPUTS, neurals[random.randint(0,survivors)]))


                    print("Best Score of gen " + str(i) + " was: " + str(players[0].score))


                        #neurals.append(NeuralNetwork(len(Player.INDICATOR_ANGLES) + Player.EXTRA_INDICATORS, NUM_OUTPUTS, neurals[random.randint(0,survivors)]))


                pickle.dump(best_neural, open("bestnn.nn", "wb"))
            print(scores)
            if mode != 3:
                game = Game(FPS, tracks, [Player(True, best_neural, starting_point[0], starting_point[1])], finish_point)
            else:
                game = Game(FPS, tracks, [Player(True, None, starting_point[0], starting_point[1])], finish_point)

        game.update()
        game.draw(window)

    else:
        if mouse[0]:
            if not last_mouse[0]:
                tracks.append(Track([mouse_pos]))
            if dist(tracks[-1].corners[-1], mouse_pos) > NEW_TRACK_SEPARATION_DIST:
                tracks[-1].corners.append(mouse_pos)

        if mouse[2] and not last_mouse[2]:
            finish_point = mouse_pos
            stage += 1
            pickle.dump(tracks, open("track1.track", "wb"))
        for track in tracks:
            track.draw(window)
        pygame.draw.circle(window, red, starting_point, 20)

    clock.tick(FPS)
    pygame.display.update()

    last_mouse = mouse
    last_keys = keys
 







