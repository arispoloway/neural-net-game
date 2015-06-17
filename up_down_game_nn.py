import os
import pygame
from pygame.locals import *
import random
import numpy as np
import time
from visual import *
from physutil import *

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
	x = SCREEN_WIDTH
	y = 450
	h = 100
	w = 50
	color = purple
	def __init__(self):
		self.x = Block.x
		self.w = Block.w
		self.h = Block.h
		self.y = random.randint(50, Block.y)



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
	y = SCREEN_HEIGHT - 125
	h = 75
	w = 20
	yvel = -10
	color = blue

	def __init__(self):
		self.x = Player.x
		self.y = Player.y
		self.h = Player.h
		self.w = Player.w
		self.dy = 0

	def update(self, fps):
		self.y += self.dy
		if self.y > Player.y:
			self.y = Player.y
			self.dy = 0
		if self.y < Player.h:
			self.y = 75
			self.dy = 0

	def draw(self, screen):
		pygame.draw.rect(screen, Player.color, (self.x, self.y, self.w, self.h))

class Game(object):
	speed = 400
	min_distance = 200
	max_distance = 350

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
				if (block.y + block.h) > self.player.y > block.y or (block.y + block.h) > (self.player.y + self.player.h) > block.y:
					return True

		# To keep from stalling
		if self.distance > 300000:
			return True

		return False

	def manageInputs(self, i):
		if i[0] and i[1]:
			self.player.dy = 0
		elif i[0]:
			self.player.dy = Player.yvel
		elif i[1]:
			self.player.dy = -Player.yvel
		else:
			self.player.dy = 0


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

	def indicate(self, game):
		for block in game.blocks:
			if block.x < self.x < (block.x + block.w):
				if block.y < self.y < (block.y + block.h):
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
		n = nn.output(game)
		game.manageInputs(n)
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

		if nn_on:
			i = nn.output(game)
		else:
			i = [0,0]
			if keys[pygame.K_UP] == True:
				i[0] = 1
			if keys[pygame.K_DOWN] == True:
				i[1] = 1

		game.manageInputs(i)
		game.update()
		window.fill(white)
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
 





seed = 1

ai_on = True

if ai_on:

	first_generation_size = 20000
	generation_size = 2000
	top_choice_num = 6


	

	indicators = [PositionIndicator()]

	for x in range(150, 500, 75):
		for y in range(100, 550, 50):
			indicators.append(Indicator(x, y))


	t = [time.time()]

	i = [NeuralNetwork(indicators, None, 5) for j in range(first_generation_size)]
	i = sorted(i, key=lambda x: get_fitness(seed, x, FPS), reverse=True)
	n = i[0:top_choice_num]

	t.append(time.time())
	best = [get_fitness(seed,n[0],FPS)]
	consec = 0

	print(str(0) + " - " + str(t[-1] - t[-2]) + " - " + str(best[0]))

	for j in range(1,20):
		
		i = []
		for k in n:
			i.extend([NeuralNetwork(indicators, k, 5, consec) for q in range(int(generation_size/float(top_choice_num + 1)))])
			i.append(k)
		i.extend([NeuralNetwork(indicators, None, 5) for q in range(int(generation_size/float(top_choice_num + 1)))])

		i = sorted(i, key=lambda x: get_fitness(seed, x, FPS), reverse=True)
		n = i[0:top_choice_num]

		t.append(time.time())
		best.append(get_fitness(seed,n[0],FPS))
		if best[-1] == best[-2]:
			consec += 1
		else:
			consec = 0
		print(str(j) + " - " + str(t[-1] - t[-2]) + " - " + str(best[-1]))

	t1 = time.time()
	print("Time to execute: " + str(t[-1] - t[0]))
	print("Best distance:   " + str(get_fitness(seed,n[0],FPS)))
	#print(n[0].w1)
	#print(n[0].w2)


game = Game(seed, FPS)

if ai_on:
	run_game(game, FPS, n[0])
else:
	run_game(game, FPS)




