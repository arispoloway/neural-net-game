import os
import pygame
from pygame.locals import *
import random
import numpy as np
import time

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
FPS = 60


black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 225)
purple   = ( 255,   0, 255)




class Block(object):
	TOP = 1
	BOTTOM = 0
	x = SCREEN_WIDTH
	y = 470
	h = 80
	w = 50
	color = purple
	def __init__(self, t):
		self.x = Block.x
		self.w = Block.w
		self.h = Block.h
		if t == Block.BOTTOM:
			self.y = Block.y
		elif t == Block.TOP:
			self.y = 50



	def draw(self, screen):
		pygame.draw.rect(screen, Block.color, (self.x, self.y, self.w, self.h))

	def move(self, distance):
		self.x -= distance

	def isOffScreen(self):
		if (self.x + self.w) < 0:
			return True
		if (self.x) > SCREEN_WIDTH:
			return True
		if (self.y + self.h) < 0:
			return True
		if (self.y) > SCREEN_HEIGHT:
			return True
		return False

class Player(object):
	x = 100
	y = SCREEN_HEIGHT - 100
	h = 50
	w = 20
	gravity = 40
	color = blue

	def __init__(self):
		self.x = Player.x
		self.y = Player.y
		self.h = Player.h
		self.w = Player.w
		self.gravity = Player.gravity
		self.dy = 0

	def grav_change(self):
		self.gravity = -self.gravity

	def update(self, fps):
		self.dy += self.gravity / float(fps)
		self.y += self.dy
		if self.y > Player.y:
			self.y = Player.y
			self.dy = 0
		if self.y < 50:
			self.y = 50
			self.dy = 0


	def draw(self, screen):
		pygame.draw.rect(screen, Player.color, (self.x, self.y, self.w, self.h))

class Game(object):
	speed = 300
	min_distance = 150
	max_distance = 500

	def __init__(self, seed, fps):
		self.fps = fps
		self.seed = seed
		random.seed(seed)
		self.distance = 0
		self.player = Player()
		self.blocks = [Block(Block.TOP), Block(Block.BOTTOM)]
		self.next_block = random.randint(Game.min_distance, Game.max_distance)


	def draw(self, screen):
		for block in self.blocks:
			block.draw(screen)
		self.player.draw(screen)

	def update(self):
		d = float(Game.speed) / self.fps
		self.distance += d

		block_buffer = []
		for block in self.blocks:
			block.move(d)
			if not block.isOffScreen():
				block_buffer.append(block)
		self.blocks = block_buffer


		self.player.update(self.fps)

		if self.next_block < (SCREEN_WIDTH - self.blocks[-1].x):
			self.blocks.append(Block(Block.TOP))
			self.blocks.append(Block(Block.BOTTOM))
			self.next_block = random.randint(Game.min_distance, Game.max_distance)

	def isColliding(self):
		for block in self.blocks:
			if (block.x + block.w) > self.player.x and (self.player.x + self.player.w) > block.x:
				if (block.y + block.h) > self.player.y > block.y or (block.y + block.h) > (self.player.y + self.player.h) > block.y:
					return True

		# To keep from stalling
		if self.distance > 300000:
			return True

		return False

class Indicator(object):
	on_color = green
	off_color = red
	y = 0
	h = SCREEN_HEIGHT
	w = 2
	def __init__(self, x):
		self.x = x
		self.y = Indicator.y
		self.h = Indicator.h
		self.w = Indicator.w

	def indicate(self, game):
		for block in game.blocks:
			if block.x < self.x < (block.x + block.w):
				self.indicated = True
				return 1
		self.indicated = False
		return -1

	def draw(self, screen):
		if self.indicated:
			c = Indicator.on_color
		else:
			c = Indicator.off_color
		pygame.draw.rect(screen, c, (self.x, self.y, self.w, self.h))

def mod_sigmoid(x):
	return 1 / (1 + np.exp(-x))

class NeuralNetwork(object):
	def __init__(self, indicators, hidden_layer_size=3):
		self.indicators = indicators
		self.w1 = np.random.randn(len(self.indicators), hidden_layer_size)
		self.w2 = np.random.randn(hidden_layer_size, 1)

	def output(self, game):
		o0 = np.array([j.indicate(game) for j in self.indicators])
		i1 = np.dot(o0, self.w1)
		o1 = mod_sigmoid(i1)
		i2 = np.dot(o1, self.w2)
		return i2.sum()

	def set_weight_1(self, weights):
		self.w1 = weights

	def set_weight_2(self, weights):
		self.w2 = weights

	def draw(self, screen):
		for i in self.indicators:
			i.draw(screen)

def get_fitness(seed, nn, fps):
	running = True
	game = Game(seed, fps)
	pressed_last_frame = False

	while running:
		if nn.output(game) > 0:
			nn_to_press = True
		else:
			nn_to_press = False

		if nn_to_press:
			if not pressed_last_frame:
				game.player.grav_change()
			pressed_last_frame = True
		else:
			pressed_last_frame = False

		game.update()

		if game.isColliding():
			return game.distance



def run_game(game, fps, nn=None):
	pygame.init()
	pygame.display.set_caption("Neural Net Testing")
	window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.update()

	clock = pygame.time.Clock()
	pygame.mouse.set_visible(1)

	nn_on = (nn != None)
	running = True

	pressed_last_frame = False

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		keys = pygame.key.get_pressed()

		nn_to_press = False
		if nn_on:
			n = nn.output(game)
			if n > 0:
				nn_to_press = True

		if keys[pygame.K_UP] == True or (nn_to_press and nn_on):
			if not pressed_last_frame:
				game.player.grav_change()
			pressed_last_frame = True
		else:
			pressed_last_frame = False

		window.fill(white)
		game.update()
		game.draw(window)

		if nn_on:
			nn.draw(window)

		if game.isColliding():
			running = False
			print(game.distance)

		pygame.draw.rect(window, black, (0, 550, SCREEN_WIDTH, 50))
		pygame.draw.rect(window, black, (0, 0, SCREEN_WIDTH, 50))
		clock.tick(fps)
		pygame.display.update()
 
seed = 4

t0 = time.time()

x_indicators = [Indicator(x) for x in range(150, SCREEN_WIDTH, 50)]
i = [NeuralNetwork(x_indicators, 3) for j in range(1000)]
scores = [get_fitness(seed, z, FPS) for z in i]
nn = i[scores.index(max(scores))]

t1 = time.time()
print("Time to execute: " + str(t1-t0))
print("Best distance:   " + str(max(scores)))
print(nn.w1)
print(nn.w2)
game = Game(seed, FPS)

run_game(game, FPS, nn)

# run_game(game, FPS)





