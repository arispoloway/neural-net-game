import os
import pygame
from pygame.locals import *
import random
import numpy as np
import time

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
FPS = 60

pygame.init()
pygame.display.set_caption("Neural Net Testing")
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.update()

clock = pygame.time.Clock()
pygame.mouse.set_visible(1)


black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = (   0, 255,   0)
red      = ( 255,   0,   0)
blue     = (   0,   0, 225)
purple   = ( 255,   0, 255)



class Block(object):
	x = 800
	y = 470
	h = 130
	w = 80
	color = purple
	def __init__(self):
		self.x = Block.x
		self.y = Block.y
		self.h = Block.h
		self.w = Block.w

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
	y = 500
	h = 50
	w = 20
	jump_speed = -20
	gravity = 100
	color = blue

	def __init__(self):
		self.x = Player.x
		self.y = Player.y
		self.h = Player.h
		self.w = Player.w
		self.dy = 0

	def jump(self):
		if not self.dy and self.y == Player.y:
			self.dy = Player.jump_speed

	def update(self, fps):
		self.dy += Player.gravity / fps
		self.y += self.dy
		if self.y > Player.y:
			self.y = Player.y
			self.dy = 0


	def draw(self, screen):
		pygame.draw.rect(screen, Player.color, (self.x, self.y, self.w, self.h))

class Game(object):
	speed = 400
	min_distance = 225
	max_distance = 400

	def __init__(self, seed, fps):
		self.fps = fps
		self.seed = seed
		random.seed(seed)
		self.distance = 0
		self.player = Player()
		self.blocks = [Block()]
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
			self.blocks.append(Block())
			self.next_block = random.randint(Game.min_distance, Game.max_distance)

	def isColliding(self):
		for block in self.blocks:
			if (block.x + block.w) > self.player.x and (self.player.x + self.player.w) > block.x:
				if (self.player.y + self.player.h) > block.y:
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
	def __init__(self, indicators):
		self.indicators = indicators
		self.w1 = np.random.randn(len(self.indicators), 3)
		self.w2 = np.random.randn(3, 1)

	def output(self, game):
		o0 = np.array([j.indicate(game) for j in self.indicators])
		i1 = np.dot(o0, self.w1)
		o1 = mod_sigmoid(i1)
		i2 = np.dot(o1, self.w2)
		return i2.sum()

	def draw(self, screen):
		for i in self.indicators:
			i.draw(screen)

def get_fitness(seed, nn, fps):
	running = True
	game = Game(seed, fps)
	while running:
		if nn.output(game) > 0:
			nn_to_press = True
		else:
			nn_to_press = False

		if nn_to_press:
			game.player.jump()
		game.update()

		if game.isColliding():
			return game.distance


seed = 3

t0 = time.time()

x_indicators = [Indicator(x) for x in range(200, 800, 75)]
nn = NeuralNetwork(x_indicators)

i = [NeuralNetwork(x_indicators) for j in range(1000)]
scores = [get_fitness(seed, z, FPS) for z in i]

nn = i[scores.index(max(scores))]

print(nn.w1)
print(nn.w2)

t1 = time.time()
print("Time to execute: " + str(t1-t0))



game = Game(seed, FPS)

nn_on = True
running = True

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
		game.player.jump()

	window.fill(white)
	game.update()
	game.draw(window)

	if nn_on:
		nn.draw(window)

	if game.isColliding():
		running = False
		print(game.distance)

	pygame.draw.rect(window, black, (0, 550, SCREEN_WIDTH, 50))
	clock.tick(FPS)
	pygame.display.update()





