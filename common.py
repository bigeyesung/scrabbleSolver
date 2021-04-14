from enum import Enum

#x,y coordinate system
class Coord(Enum):
    X=0
    Y=1
    
#vertical and horizontal movement
class Move(Enum):
    Vert=0
    Hori=1

class Dirs():
    def __init__(self):
        self.leftDir=[0,-1]
        self.rightDir=[0,1]
        self.upDir=[-1,0]
        self.downDir=[1,0]