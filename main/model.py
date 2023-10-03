import typing, pathlib



class Point:
    def __init__(self,xyz,colour=(0,0,0)):
        self.colour = colour
        self.xyz = xyz
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
    
    def __repr__(self):
        return self.xyz



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
        try:
            self.pointmap.pop(index)
            if len(self.connected_points) > 1:
                for _ in range(0,len(self.connected_points)-1,2):
                    if self.connected_points[_] == index or self.connected_points[_+1] == index:
                        self.connected_points.pop(_)
                        self.connected_points.pop(_+1)
                
        except:
            pass

    @classmethod
    def load(cls,name):
        try:
            path = pathlib.Path(__file__).parent
            with open(f'{path}/{name}.CBmodel','r') as model:
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
            path = pathlib.Path(__file__).parent
            with open(f'{path}/{name}.CBmodel','w') as writable:
                writable.write(str(self.pointmap) + '\n')
                writable.write(str(self.connected_points)+ '\n')
                writable.close()
        except:
            raise WindowsError("Could not save file.")
        
    def delete_all(self):
        self.pointmap=[]
        self.connected_points=[]
      
    