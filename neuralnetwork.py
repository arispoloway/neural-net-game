import numpy as np
from math import *
import copy


def mod_sigmoid(x):
    return 1 / (1 + np.exp(-x))



def breed_networks(nn1, nn2, mutation_percent):
    new_nn = copy.deepcopy(nn1)
    for i in range(len(new_nn.weights)):
        new_nn.weights[i] = (nn1.weights[i]  + nn2.weights[i]) * (1 - mutation_percent) / 2 + mutation_percent * np.random.randn(nn1.weights[i].shape[0], nn1.weights[i].shape[1])
    return new_nn

class NeuralNetwork(object):
    def __init__(self, num_indicators, num_outputs, base_nn=None, hidden_layer_size=5, num_hidden_layers=2):
        self.num_indicators = num_indicators
        self.num_outputs = num_outputs
        self.weights = []
        if base_nn == None:
            self.weights.append(np.random.randn(num_indicators, hidden_layer_size))
            for i in range(num_hidden_layers-1):
                self.weights.append(np.random.randn(hidden_layer_size, hidden_layer_size))
            self.weights.append(np.random.randn(hidden_layer_size, num_outputs))
        else:
            for weight in base_nn.weights:
                self.weights.append(weight/2 + np.random.randn(weight.shape[0], weight.shape[1])/2)

    def output(self, indications):
        o = np.array(indications)
        for weight in self.weights:
            i = np.dot(o, weight)
            o = mod_sigmoid(i)

        return [1 if v > 0.5 else 0 for v in o]

    def set_weight_1(self, weights):
        self.w1 = weights

    def set_weight_2(self, weights):
        self.w2 = weights

    def draw(self, screen):
        for i in self.indicators:
            i.draw(screen)
