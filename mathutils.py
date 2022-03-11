import math
from ppb import Vector

def lerp(a,b,t):
    return a*(1-t)+b*t


def lerp_vector(a, b, t):
    c = Vector(lerp(a.x, b.x, t), lerp(a.y, b.y, t))
    return c

def rotated_vector(vector, angle_in_degrees):
    ang_in_rad = angle_in_degrees / 360.0 * math.tau
    new_vec = Vector(
        math.cos(ang_in_rad) * vector.x + math.sin(ang_in_rad) * vector.y,
        -math.sin(ang_in_rad) * vector.x + math.cos(ang_in_rad) * vector.y)
    return new_vec

def dot_product(vec1, vec2):
    return vec1.x * vec2.x + vec1.y*vec2.y

def dot_product_as_cos(vec1,vec2):
    return dot_product(vec1, vec2) / (vec1.length * vec2.length)
