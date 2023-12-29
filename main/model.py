import typing
from pathlib import Path



class Point:
    def __init__(self,xyz,colour=(0,0,0)):
        self.colour = colour
        self.xyz = xyz
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
    
    def __repr__(self):
        return str(self.xyz) # I forgot my zen of python for a minute there!



class CBModel:
    def __init__(self,pointmap:typing.List[Point]=[],connected_points:typing.List[int]=[]):
        self.pointmap = pointmap
        self.connected_points = connected_points

    def add(self,points:typing.Union[typing.List[Point],tuple,Point]):
        if isinstance(points,tuple):

            self.pointmap.append(Point(list(points)))

        elif isinstance(points[0],int):
            self.pointmap.append(Point(points))
        elif isinstance(points,Point):
            self.pointmap.append(points)
        else:
            for i in points:
                self.pointmap.append(i)
    
    def delete(self,index:int):  #we need a specific function for this otherwise the indexes will remain in the connected_points arr, leading to errors when rendering connections
        #1. go thru pointmap, delete index
        #2. go thru connected_points, delete pairs
        #3. go thru connected_points, -1 from every point above index

        print(self.pointmap)
        print(self.connected_points)
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
        
        print(self.pointmap)
        print(self.connected_points)

    @classmethod
    def load(cls,name):
        try:
            
            with open(name,'r') as model: #guizero.select_file will provide full path, so no pathlib needed here
                model_info = model.readlines()
                model_points = eval((model_info[0]).replace('\n',''))
                model_connections = eval((model_info[1]).replace('\n',''))

                
                model.close()
            connected_points = model_connections
            points = model_points

            return CBModel(points,connected_points)

        except Exception as e:
            print(e)
            print(f'Could not find file {name}.CBmodel; please check your local files.')

        

    def save(self,name):
        try:
            path = Path(__file__).parent
            with open(f'{path}/{name}.CBmodel','w') as writable:
                writable.write(str(self.pointmap) + '\n')
                writable.write(str(self.connected_points)+ '\n')
                writable.close()
        except:
            raise WindowsError("Could not save file.")
        
    def delete_all(self):
        self.pointmap=[]
        self.connected_points=[]
      
class Plane:
    def __init__(self,vertices:typing.List[Point],colour):
        self.vertices = vertices
        self.colour = colour