import os
from pathlib import Path

class Textures:
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