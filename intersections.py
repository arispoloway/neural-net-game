import numpy as np
from math import *


def det(E11, E12, E21, E22):
        return E11 * E22 - E21 * E12



def dist(p1, p2):
    return sqrt(pow(p2[0] - p1[0], 2.0) + pow(p2[1] - p1[1], 2.0))

def in_range(n1,n2,num):
    if n2 > n1:
        return n1 < num < n2
    return n2 < num < n1

def alt_intersect(X1, Y1, X2, Y2, X3, Y3, X4, Y4):
    A1 = Y1 - Y2
    B1 = X2 - X1
    A2 = Y3 - Y4
    B2 = X4 - X3
    C1 = -A1 * X1 - B1 * Y1
    C2 = -A2 * X3 - B2 * Y3
    if ((A1 * X3 + B1 * Y3 + C1 < 0) != (A1 * X4 + B1 * Y4 + C1 < 0 )):
        if ((A2 * X1 + B2 * Y1 + C2 < 0) != ( A2 * X2 + B2 * Y2 + C2 < 0)):
            return True
    return False


def intersect_dist(X1, Y1, X2, Y2, X3, Y3, X4, Y4):
    A1 = Y1 - Y2
    B1 = X2 - X1
    A2 = Y3 - Y4
    B2 = X4 - X3
    C1 = -A1 * X1 - B1 * Y1
    C2 = -A2 * X3 - B2 * Y3
    d = det(A1, B1, A2, B2)
    if d == 0:
        return None
    x = det(-C1, B1, -C2, B2) / d
    y = det(A1, -C1, A2, -C2) / d
    if in_range(X1,X2,x) and in_range(X3,X4,x) and in_range(Y1,Y2,y) and in_range(Y3,Y4,y):
        return (x,y)
    return None