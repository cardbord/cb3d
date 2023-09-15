import typing

class Point:
    def __init__(self,xyz,colour):
        self.colour = colour
        self.xyz = xyz
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
    
    def __repr__(self):
        return self.xyz


class CBModel:
    def __init__(self,pointmap:typing.List[typing.List[int]]=None,connected_points:typing.List[int]=None):
        self.pointmap = pointmap
        self.connected_points = connected_points

    def add(self,points:typing.List[Point]):
        if len(points) == 1:
            self.pointmap.append(points)
        else:
            for i in points:
                self.pointmap.append(i)
    
    
    