from random import randrange
import pygame
import os
from pathlib import Path

class Texture: #texture class, contains all necessary parts of the texture
    def __init__(self, filename, name, transparency_level:float=1.0, tx=None, ty=None):
        self.filename = filename
        self.texture_map = pygame.image.load(filename).convert_alpha()
        self.transparency = transparency_level
        self.name = name
        self.tx = tx or randrange(0,int(round(self.texture_map.get_width()/3))) #apply randomness to texture positions 
        self.ty = ty or randrange(0,int(round(self.texture_map.get_height()/3))) #so that the texture is not repeated on different sides of the object
        


def collated_images() -> dict:
    __path = Path(__file__).parent
    tmap = {}
    _texture_array = []
    _md_walk = os.walk(__path)
    for (dirpath,_,__) in _md_walk: #creates an array of paths to each texture folder
        if "__pycache__" not in dirpath:
            _texture_array.append(dirpath)
    _texture_array.pop(0) #this is the parent directory, no need for this!
    
    
    for directory in _texture_array: 
        dirfiles = os.listdir(directory) #creates subarrays of the contents of each folder

        tmap[dirfiles[0][:dirfiles[0].find('.')]] = [(directory+'\\'+file) for file in dirfiles]
        
        r'''
        the last line looks really complicated, but this is simply adding to a tmap dictionary with...
        key: filename with file extension removed
        value: an array of the full file path of each texture file in the contents subarray
        '''

    return tmap



class TextureCatalogue: #catalogue to access textures through
    def __init__(self):
        
        _textures = {}
        tmap = collated_images()
        for t in tmap:
            imgpath = ''
            texture_transparency=1.0
            tx=None
            ty=None
            tm = tmap[t]
            
            if tm[0].endswith('.cbtx'):
                with open(tm[0], "r") as readable: #extracting the data from the cbtx file
                    texture_info = readable.readlines()
                    texture_transparency = float(texture_info[1].replace('\n', ''))
                    if len(texture_info) > 2:
                        tx = int(texture_info[2].replace('\n', ''))
                        ty = int(texture_info[3].replace('\n', ''))

                imgpath = tm[1] #if the first file is a cbtx, the second is the image file
                

            else:
                with open(tm[1], "r") as readable:
                    texture_info = readable.readlines()
                    texture_transparency = float(texture_info[1].replace('\n', ''))
                    if len(texture_info) > 2:
                        tx = int(texture_info[2].replace('\n', ''))
                        ty = int(texture_info[3].replace('\n', ''))
                
                imgpath = tm[0] #if the second file is the cbtx, the first is the image file
            
            

            _textures[t] = Texture(imgpath,t,texture_transparency,tx,ty) #instantiating a texture object with the data extracted from the cbtx, along with the image file

        self.textures = _textures

