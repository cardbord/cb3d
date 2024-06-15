from random import randrange
import pygame
import os
from pathlib import Path

class collated_images:
     def __init__(self):
          __path = Path(__file__).parent
          self.tmap = {}
          _texture_array = []
          _md_walk = os.walk(__path)
          for (dirpath,_,__) in _md_walk:
               if "__pycache__" not in dirpath:
                    _texture_array.append(dirpath)
          _texture_array.pop(0)

          
          for directory in _texture_array:
               dirfiles = os.listdir(directory)
               self.tmap[dirfiles[0][:dirfiles[0].find('.')]] = [(directory+'\\'+file) for file in dirfiles]




class Texture:
    def __init__(self, filename, name, transparency_level=1, tx=None, ty=None):
        self.filename = filename
        self.texture_map = pygame.image.load(filename).convert_alpha()
        self.transparency = transparency_level
        self.name = name
        self.tx = tx or randrange(0,int(round(self.texture_map.get_width()/3))) #apply randomness to texture positions
        self.ty = ty or randrange(0,int(round(self.texture_map.get_height()/3)))
        
class TextureCatalogue:
    @property
    def textures(self):
        _textures = {}
        _texts = collated_images()
        for t in _texts.tmap:
            imgpath = ''
            texture_transparency=1.0
            tx=None
            ty=None
            tm = _texts.tmap[t]
            
            if tm[0].endswith('.cbtx'):
                with open(tm[0], "r") as readable:
                    texture_info = readable.readlines()
                    texture_transparency = float(texture_info[1].replace('\n', ''))
                    if len(texture_info) > 2:
                        tx = int(texture_info[2].replace('\n', ''))
                        ty = int(texture_info[3].replace('\n', ''))
                imgpath = tm[1]
                

            else:
                with open(tm[1], "r") as readable:
                    texture_info = readable.readlines()
                    texture_transparency = float(texture_info[1].replace('\n', ''))
                    if len(texture_info) > 2:
                        tx = int(texture_info[2].replace('\n', ''))
                        ty = int(texture_info[3].replace('\n', ''))
                
                imgpath = tm[0]
            
            

            _textures[t] = Texture(imgpath,t,texture_transparency,tx,ty)

        return _textures
