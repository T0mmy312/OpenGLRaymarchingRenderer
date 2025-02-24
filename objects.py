import moderngl
import numpy as np
from vectors import *

MATERIAL_SIZE_FLOATS = 7 # r, g, b, ambientStrenght, diffuseStrenght, specularStrenght, shininess
MATERIAL_SIZE_BYTES = MATERIAL_SIZE_FLOATS * 4

class Material:
    index: int = 0

    def __init__(self, index):
        self.index = index
    
    def setColor(self, color: vec3, materialArray):
        materialArray.data[self.index] = color.x
        materialArray.data[self.index + 1] = color.y
        materialArray.data[self.index + 2] = color.z
    
    def getColor(self, materialArray) -> vec3:
        return vec3(materialArray.data[self.index], materialArray.data[self.index + 1], materialArray.data[self.index + 2])
    
    def setAmbientStrength(self, ambientStrength: float, materialArray):
        materialArray.data[self.index + 3] = ambientStrength
    
    def getAmbientStrength(self, materialArray) -> float:
        return materialArray.data[self.index + 3]
    
    def setDiffuseStrength(self, diffuseStrenght: float, materialArray):
        materialArray.data[self.index + 4] = diffuseStrenght
    
    def getDiffuseStrength(self, materialArray) -> float:
        return materialArray.data[self.index + 4]

    def setSpecularStrength(self, specularStrength: float, materialArray):
        materialArray.data[self.index + 5] = specularStrength
    
    def getSpecularStrength(self, materialArray) -> float:
        return materialArray.data[self.index + 5]
    
    def setShininess(self, shininess: float, materialArray):
        materialArray.data[self.index + 6] = shininess
    
    def getShininess(self, materialArray) -> float:
        return materialArray.data[self.index + 6]

class MaterialArray:
    data = np.array([], dtype="f4")
    numMaterials: int = 0

    def __init__(self):
        self.data = np.array([], dtype="f4")
        self.numMaterials = 0
    
    def addMaterial(self) -> Material:
        ret = Material(self.numMaterials * MATERIAL_SIZE_FLOATS)
        self.numMaterials += 1
        self.data.resize((self.numMaterials * MATERIAL_SIZE_FLOATS))
        return ret
    
    def toBytes(self) -> bytes:
        return self.data.tobytes()

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

BOX_SIZE_FLOATS = 7 # x, y, z, width, height, depth, materialIndex
BOX_SIZE_BYTES = BOX_SIZE_FLOATS * 4   

class Box:
    index: int = 0
    material_index: int = 0

    def  __init__(self, index, material_index):
        self.index = index
        self.material_index = material_index
    
    def setPos(self, pos: vec3, boxArray):
        boxArray.data[self.index] = pos.x
        boxArray.data[self.index + 1] = pos.y
        boxArray.data[self.index + 2] = pos.z
    
    def getPos(self, boxArray) -> vec3:
        return vec3(boxArray.data[self.index], boxArray.data[self.index + 1], boxArray.data[self.index + 2])
    
    def setDimentions(self, dim: vec3, boxArray):
        boxArray.data[self.index + 3] = dim.x
        boxArray.data[self.index + 4] = dim.y
        boxArray.data[self.index + 5] = dim.z
    
    def getDimentions(self, boxArray) -> vec3:
        return vec3(boxArray.data[self.index + 3], boxArray.data[self.index + 4], boxArray.data[self.index + 5])
    
    def setMaterial(self, material: Material, boxArray):
        boxArray.material_data[self.material_index] = material.index

    def getMaterial(self, boxArray) -> Material:
        return boxArray.material_data[self.material_index]
    
class BoxArr: 
    data = np.array([], dtype="f4")
    material_data = np.array([], dtype="i4")
    numBoxes: int = 0

    def __init__(self):
        self.data = np.array([], dtype="f4")
        self.material_data = np.array([], dtype="i4")
        self.numBoxes = 0
    
    def addBox(self) -> Box:
        ret = Box(self.numBoxes * BOX_SIZE_FLOATS, self.numBoxes)
        self.numBoxes += 1
        self.data.resize((self.numBoxes * BOX_SIZE_FLOATS))
        self.material_data.resize((self.numBoxes))
        return ret
    
    def boxDataToBytes(self) -> bytes:
        return self.data.tobytes()

    def materialDataToBytes(self) -> bytes:
        return self.material_data.tobytes()