import numpy as np
from math import *
import copy


def mod_sigmoid(x):
    return 1 / (1 + np.exp(-x))



def breed_networks(nn1, nn2, mutation_percent):
    new_nn = copy.copy(nn1)
    new_nn.w1 = (nn1.w1  + nn2.w1) * (1 - mutation_percent) / 2 + mutation_percent * np.random.randn(nn1.w1.shape[0], nn1.w1.shape[1])
    new_nn.w2 = (nn1.w2  + nn2.w2) * (1 - mutation_percent) / 2 + mutation_percent * np.random.randn(nn1.w2.shape[0], nn1.w2.shape[1])
    return new_nn

class NeuralNetwork(object):
    def __init__(self, num_indicators, num_outputs, base_nn=None, hidden_layer_size=5):
        self.num_indicators = num_indicators
        if base_nn == None:
            self.w1 = np.random.randn(num_indicators, hidden_layer_size)
            self.w2 = np.random.randn(hidden_layer_size, num_outputs)
        else:
            self.w1 = base_nn.w1/2 + np.random.randn(num_indicators, hidden_layer_size)/2
            self.w2 = base_nn.w2/2 + np.random.randn(hidden_layer_size, num_outputs)/2

    def output(self, indications):
        o0 = np.array(indications)
        i1 = np.dot(o0, self.w1)
        o1 = mod_sigmoid(i1)
        i2 = np.dot(o1, self.w2)

        of = [0,0,0,0]
        if i2[0] > 0:
            of[0] = 1
        if i2[1] > 0:
            of[1] = 1
        if i2[2] > 0:
            of[2] = 1
        if i2[3] > 0:
            of[3] = 1
        return of

    def set_weight_1(self, weights):
        self.w1 = weights

    def set_weight_2(self, weights):
        self.w2 = weights

    def draw(self, screen):
        for i in self.indicators:
            i.draw(screen)
