import moderngl
import json
import numpy as np
from typing import Dict, Tuple
from vectors import *

# CAUTION Structs in arrays must be padded to a multiple of 16 bytes
# also vec3 is aligned to 16 bytes even tho it is only 12 (4 * 3)

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
    
LIGHT_SIZE_FLOATS = 7 # x, y, z, intensity, r, g, b
LIGHT_SIZE_BYTES = LIGHT_SIZE_FLOATS * 4

class Light:
    index: int = 0

    def __init__(self, index):
        self.index = index

    def setPosition(self, pos: vec3, lightArray):
        lightArray.data[self.index] = pos.x
        lightArray.data[self.index + 1] = pos.y
        lightArray.data[self.index + 2] = pos.z
    
    def getPosition(self, lightArray) -> vec3:
        return vec3(lightArray.data[self.index], lightArray.data[self.index + 1], lightArray.data[self.index + 2])
    
    def setIntensity(self, intensity: float, lightArray):
        lightArray.data[self.index + 3] = intensity
    
    def getIntensity(self, lightArray):
        return lightArray.data[self.index + 3]
    
    def setColor(self, color: vec3, lightArray):
        lightArray.data[self.index + 4] = color.x
        lightArray.data[self.index + 5] = color.y
        lightArray.data[self.index + 6] = color.z
    
    def getColor(self, lightArray) -> vec3:
        return vec3(lightArray.data[self.index + 4], lightArray.data[self.index + 5], lightArray.data[self.index + 6])

class LightArray:
    data = np.array([], dtype="f4")
    numLights: int = 0

    def __init__(self):
        self.data = np.array([], dtype="f4")
        self.numLights = 0
    
    def addLight(self) -> Light:
        ret = Light(self.numLights * LIGHT_SIZE_FLOATS)
        self.numLights += 1
        self.data.resize((self.numLights * LIGHT_SIZE_FLOATS))
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

class VoxelModel:
    _size: float = 1
    _pos: vec3 = vec3(0, 0, 0)
    posToBox: Dict[Tuple[float, float, float], Box] = {}

    def __init__(self, pos: vec3 = vec3(0, 0, 0), size: float = 1, posToBox: Dict[Tuple[float, float, float], Box] = {}):
        self._size = size
        self._pos = pos
        self.posToBox = posToBox
    
    def getBox(self, pos: vec3) -> Box:
        return self.posToBox[pos.tuple()]
    
    def setBox(self, pos: vec3, box: Box, boxArray: BoxArr):
        box.setPos(self._pos + pos, boxArray)
        box.setDimentions(vec3(self._size, self._size, self._size), boxArray)
        self.posToBox[pos.tuple()] = box

    def addBox(self, pos: vec3, boxArray: BoxArr) -> Box:
        box = boxArray.addBox()
        box.setPos(self._pos + pos, boxArray)
        box.setDimentions(vec3(self._size, self._size, self._size), boxArray)
        self.posToBox[pos.tuple()] = box
        return box
    
    def getPos(self) -> vec3:
        return self._pos
    
    def setPos(self, pos: vec3, boxArray: BoxArr):
        self._pos = pos
        for offset, box in self.posToBox.items():
            new_pos = vec3(offset[0], offset[1], offset[2]) + pos
            box.setPos(new_pos, boxArray)
    
    def getSize(self) -> float:
        return self._size

    def setSize(self, size: float, boxArray: BoxArr):
        self._size = size
        for box in self.posToBox.values():
            box.setDimentions(vec3(size, size, size), boxArray)

def hex_to_rgb_vec3(hex_color: str) -> vec3:
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return vec3(r / 255.0, g / 255.0, b / 255.0)

def loadVoxelModel(filepath: str, pos: vec3, size: float, boxArray: BoxArr, materialArray: MaterialArray, flipYZ: bool = True) -> VoxelModel:
    voxel_model = VoxelModel(pos, size)
    data = {}
    with open(filepath, "r") as file:
        data = json.load(file)

    material_dict: Dict[str, Material] = {}

    voxels = data["voxels"]
    for voxel in voxels:
        voxel_pos = vec3(voxel['x'], voxel['y'], voxel['z'])
        if flipYZ:
            temp = voxel_pos.z
            voxel_pos.z = voxel_pos.y
            voxel_pos.y = temp

        mat = Material(-1)
        color_hex = voxel['c']
        if color_hex in material_dict:
            mat = material_dict[color_hex]
        else:
            color = hex_to_rgb_vec3(color_hex)
            mat = materialArray.addMaterial()
            mat.setColor(color, materialArray)
            mat.setAmbientStrength(0.1, materialArray)
            mat.setDiffuseStrength(0.8, materialArray)
            mat.setSpecularStrength(0.5, materialArray)
            mat.setShininess(32.0, materialArray)
            material_dict[color_hex] = mat

        box = voxel_model.addBox(voxel_pos * size, boxArray)
        box.setMaterial(mat, boxArray)
    
    return voxel_model