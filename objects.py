import moderngl
import numpy as np
from vectors import *

SPHERE_SIZE_FLOATS = 4
SPHERE_SIZE_BYTES = SPHERE_SIZE_FLOATS * 4

class Sphere:
    index: int = 0

    def __init__(self, index: int):
        self.index = index
    
    def setPos(self, pos: vec3, sphereArr):
        sphereArr.data[self.index] = pos.x
        sphereArr.data[self.index + 1] = pos.y
        sphereArr.data[self.index + 2] = pos.z
    
    def getPos(self, sphereArr) -> vec3:
        return vec3(sphereArr.data[self.index], sphereArr.data[self.index + 1], sphereArr.data[self.index + 2])
    
    def setRadius(self, radius: float, sphereArr):
        sphereArr.data[self.index + 3] = radius
    
    def getRadius(self, sphereArr) -> float:
        return sphereArr.data[self.index + 3]

class SphereArr: 
    data = np.array([], dtype="f4")
    numSpheres: int = 0

    def __init__(self):
        self.data = np.array([], dtype="f4")
        self.numSpheres = 0
    
    def addSphere(self) -> Sphere: # returns a sphere
        ret = Sphere(self.numSpheres * SPHERE_SIZE_FLOATS)
        self.numSpheres += 1
        self.data.resize((self.numSpheres * SPHERE_SIZE_FLOATS))
        return ret
    
    def toBytes(self) -> bytes:
        return self.data.tobytes()