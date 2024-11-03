import numpy as np
import math as m
import pygame
from model import Point

pygame.init()
default_font = pygame.font.get_default_font()


class Observer: #used as part of the depth algo to find a relative position between everything and a camera
    def __init__(self):
        self.position = [0,0,0] #init through calcpos
        
    def calcpos(self,angle_x,angle_y, scale): #setter for Observer.position
        
        xlen = abs(scale)*m.cos(m.pi*2 - angle_x)
        zlen = abs(scale)*m.sin(m.pi*2 - angle_x)
        
        ylen = abs(scale)*m.cos(m.pi*2 - angle_y)
        hidden_z = scale*m.sin(m.pi*2 - angle_y)
        
        sf = (scale**2)/hidden_z
        self.position = [xlen/sf, zlen/sf, ylen]

    def calc_dist_topoint(self,point) -> float: #distance calc between another point
        return m.sqrt(abs((self.position[0] - point[0][0])**2 + (self.position[1] - point[1][0])**2 + (self.position[2] - point[2][0])**2))
    
    #good idea to keep position private through getter/setters like these as other position vars exist in main program

        


class display_3Dgrid:
    def __init__(self,points,angle_x,angle_y,angle_z,scale):
        
        self.observer = Observer() 

        self.point_map = points

        self.angle_x = angle_x
        self.angle_z = angle_z
        self.angle_y = angle_y
        self.scale = scale
        self.movable_position = [0,0]

        self.window_size = pygame.display.get_desktop_sizes()[0]

        self.rendered_pointmap = [] #edited once rendered

        self.manipulation_matrix = np.matrix([[1,0,0],[0,1,0]])

    def update_angles(self,angle_x,angle_y):
        self.angle_x =  angle_x
        self.angle_y = angle_y
        self.observer.calcpos(self.angle_y,self.angle_z,self.scale)

    def update_scale(self,scale):
        self.scale = scale
        self.observer.calcpos(self.angle_y,self.angle_z,self.scale)
        
    
    def project_points(self): #setter for rendered pointmap
        

        pointmap = []
        
        
        for point in self.point_map:
            if isinstance(point, Point):
                mat_point = point.xyz #the point here is of the Point datatype, specified in model.py
            else:
                mat_point = point
            mat_point = np.matrix(mat_point)
            
            rotationalz, rotationaly, rotationalx = self.rotation() #generates rotation matrices based on x,y,z angles
            
            rotate = np.dot(rotationaly, mat_point.reshape((3,1))) #applies rotation matrices one by one
            rotate = np.dot(rotationalz, rotate)
            rotate = np.dot(rotationalx,rotate)
            
            projection = np.dot(self.manipulation_matrix,rotate) #calcs product to cast to a 2D form

            x = int(projection[0][0]*(200-self.scale)) + self.window_size[0]/2 + self.movable_position[0] 
            y = self.window_size[1]/2 - (int(projection[1][0]*(200-self.scale))) + self.movable_position[1]
            pointmap.append((x,y))
        

        self.rendered_pointmap = pointmap #this will be referenced in main loop to render everything...
        
        
    def plane_project(self,points,position:tuple) -> list: #returns arr of points, used for rendering planes seperately
        pointmap = []
        raw_rotates = []
        
        for point in points:
            if isinstance(point,Point): #my versioning isn't great, so as we shift to encapsulated point objects i'll prevent error here
                mat_point = point.xyz
            else:
                mat_point = point
            
            mat_point = np.matrix(mat_point)
            rotationalz, rotationaly, rotationalx = self.rotation()
            rotate = np.dot(rotationaly, mat_point.reshape((3,1)))
            
            
            rotate = np.dot(rotationalz, rotate)
            rotate = np.dot(rotationalx,rotate)
            
            
            raw_rotates.append(rotate)
            
            projection = np.dot(self.manipulation_matrix,rotate)
            x = int(projection[0][0]*(200-self.scale)) + position[0] + self.movable_position[0]
            y = self.window_size[1] - (int(projection[1][0]*(200-self.scale)) + position[1]) + self.movable_position[1]
            pointmap.append((x,y))
            
        return raw_rotates, pointmap

    def rotation(self):
        #returns 3 unique rotation matrices based on the x,y,z angles
        
        rotationalz = np.array([
            [m.cos(self.angle_z), -m.sin(self.angle_z),0],
            [m.sin(self.angle_z), m.cos(self.angle_z),0],
            [0,0,1]
        ])
        rotationaly = np.array([
            [m.cos(self.angle_y),0, m.sin(self.angle_y)],
            [0,1,0],
            [-m.sin(self.angle_y),0, m.cos(self.angle_y)]
        ])
        rotationalx = np.array([
            [1,0,0],
            [0,m.cos(self.angle_x), -m.sin(self.angle_x)],
            [0,m.sin(self.angle_x), m.cos(self.angle_x)]
        ])
        return rotationalz, rotationaly, rotationalx