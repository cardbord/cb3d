import typing
from pathlib import Path
from utils.textures.textureCatalogue import TextureCatalogue

class Point:
    def __init__(self,xyz,colour=(0,0,0)):
        self.colour = colour
        self._xyz = xyz
        
    
    def __repr__(self):
        return str(self._xyz) # I forgot my zen of python for a minute there!

    @property
    def x(self):
        return self._xyz[0]
    @property
    def y(self):
        return self._xyz[1]
    @property
    def z(self):
        return self._xyz[2]
    @property
    def xyz(self):
        return self._xyz
    @xyz.setter
    def xyz(self, value):
        self._xyz = value
    
    

    def rounded(self):
        return [round(self.x),round(self.y),round(self.z)]

class CBModel:
    def __init__(self,pointmap:typing.List[Point]=[],connected_points:typing.List[int]=[],__fname:str=None, __planes:typing.List[list]=None):
        self.pointmap = pointmap
        
        __textcat = TextureCatalogue()

        self.connected_points = connected_points
        self.__path = str(Path(__file__).parent).replace("\\","/")
        self.filename_modified = __fname #set when model opened, or saved. __fname should only be used by classmethods to maintain save data
        self.planes = [] # implement through add_plane method
        if __planes:
            for plane in __planes:
                
                self.planes.append(Plane(eval(plane[0]),eval(plane[1]),eval(plane[2]),__textcat.textures[plane[3]] if plane[3] != None else None))
        
        self.plane_points = []
        self.plane_connections_raw = []

    def add(self,points:typing.Union[typing.List[Point],tuple,Point]):
        self.filename_modified = None
        if isinstance(points,tuple):

            self.pointmap.append(Point(list(points)))

        elif isinstance(points[0],int):
            self.pointmap.append(Point(points))
        elif isinstance(points,Point):
            self.pointmap.append(points)
        else:
            for i in points:
                self.pointmap.append(i)

    def add_plane(self,points:typing.List[Point], connection_list:typing.List[int],colour:tuple=None, texture=None):
        
        #we also add point data and connection data to our connections and points array
        
        
        newplane = Plane(points,connection_list,colour if colour else (255,255,255), texture)
        
        self.planes.append(newplane)
        
        
    def save_on_exit(self): #our nice little recovery funct
        
        with open(f'{self.__path}/_savedata.cblog', 'w') as writable:
            if self.filename_modified:
                writable.write(self.filename_modified)
            else: #write model, just clone CBModel.save()
                writable.write(str(self.pointmap) + '\n')
                writable.write(str(self.connected_points)+ '\n')
                print([i.texture.name if i.texture else None for i in self.planes])
                writable.write(f"{[[str(i.points), str(i.connections), str(i.colour), i.texture.name if i.texture != None else None] for i in self.planes]}" + "\n")
            writable.close()
    
    @classmethod
    def from_cblog(cls):
        path = str(Path(__file__).parent).replace("\\","/") + "/_savedata.cblog"
        if Path(path).is_file():
            with open(path,'r') as readable:
                model_info = readable.readlines()
                model_planes = None
                if len(model_info) > 1: #this is a cbmodel file
                    model_points = eval((model_info[0]).replace('\n',''))
                    model_points = [Point(i) for i in model_points]
                    model_connections = eval((model_info[1]).replace('\n',''))
                    if len(model_info) > 2:
                        model_planes = eval(model_info[2].replace('\n',''))
                    readable.close()
                    
                    
                    return cls(model_points,model_connections,None,model_planes)
                else: #single line, so this is a path to a cbmodel
                    return CBModel.load(model_info[0].replace('\n',''))
        else:
            return cls()


    
    def delete(self,index:int):  #we need a specific function for this otherwise the indexes will remain in the connected_points arr, leading to errors when rendering connections
        #1. go thru pointmap, delete index
        #2. go thru connected_points, delete pairs
        #3. go thru connected_points, -1 from every point above index
        self.filename_modified = None
        counter = 0
        self.pointmap.pop(index)
        
        for i in range(len(self.connected_points)):
            i-=counter
            try:
                if self.connected_points[i] == index:
                    counter+=2
                    if i%2 == 0:
                        del self.connected_points[i:i+2]
                    else:
                        del self.connected_points[i-1:i+1]
            except:
                pass
                    

        for i in range(len(self.connected_points)):
            if self.connected_points[i] >= index:
                self.connected_points[i] -= 1
        
        

    @classmethod
    def load(cls,name):
        if Path(name).is_file():
            
            with open(name,'r') as model: #guizero.select_file will provide full path, so no pathlib needed here
                model_planes = None
                model_info = model.readlines()
                model_points = eval((model_info[0]).replace('\n',''))
                model_connections = eval((model_info[1]).replace('\n',''))
                if len(model_info) > 2:
                    model_planes = eval(model_info[2].replace('\n',''))
                
                
                model.close()
            return cls(model_points,model_connections,name,model_planes)

        else: #this is most likely to happen if an __fname is moved or deleted, and the old path is still saved in _savedata.cblog
            return cls()
            
        

    def save(self,name):
        try:
            
            with open(f'{name}.CBmodel','w') as writable:
                writable.write(str(self.pointmap) + '\n')
                writable.write(str(self.connected_points)+ '\n')
                writable.write(f"{[[str(i.points), str(i.connections), str(i.colour), i.texture.name if i.texture else None] for i in self.planes]}" + "\n")
                writable.close()
        except:
            raise WindowsError("Could not save file.")
        
    def delete_all(self):
        self.pointmap=[]
        self.connected_points=[]
        self.filename_modified = None
        self.planes = []
      
class Plane:
    def __init__(self,points:typing.List[Point],connections:typing.List[int],colour, texture=None):
        self.points = points
        self.colour = colour
        self.connections = connections
        self.rpoints = []
        self.render_points = []
        self.avg_distance = 100
        self.texture=texture
