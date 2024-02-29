import numpy as np
import math as m
import pygame
from typing import Tuple
from model import Point
from model import CBModel

pygame.init()
default_font = pygame.font.get_default_font()

class Button:
    def __init__(self,x,y,width,height,text,command):
        self._command = command
        self.rect = pygame.Rect(x,y,width,height)
        self.text = text
    def display(self,dis):
        pygame.draw.rect(dis,(60,60,60),self.rect)
        text = pygame.font.SysFont(default_font,46)
        text = text.render(self.text,True,(255,255,255))
        text_rect = text.get_rect(center=self.rect.center)
        dis.blit(text,text_rect)

    def when_clicked(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self._command()

class menu_screen:
    def __init__(self,active, commands):
        self.active = active
        self._commands = commands
        self.menurect =  pygame.Rect(100,100,600,600)

    def display(self,dis):
        for command in self._commands:
            command.display(dis)

class Observer:
    def __init__(self):
        self.position = [0,0] #init through calcpos
        
    def calcpos(self,angle_x,angle_y, scale):
        #nasty code, but it works!
        
        
        xlen = scale*m.cos(m.pi*2 - angle_x)
        zlen = scale*m.sin(m.pi*2 - angle_x)
        
        ylen = abs(scale*m.cos(m.pi*2 - angle_y))
        hidden_z = scale*m.sin(m.pi*2 - angle_y)
        
        sf = scale/hidden_z
        self.position = [xlen/sf, zlen/sf, ylen]

    def calc_dist_topoint(self,point):
        try:
            return m.sqrt(abs((self.position[0] - point[0][0])**2 + (self.position[1] - point[1][0])**2 + (self.position[2] - point[2][0])**2))
        except:
            return 10000
        

class display_3Dgrid:
    def __init__(self,points,angle_x,angle_y,angle_z,scale):
        self.observer = Observer()
        
        self.cbmods = []

        self.point_map = points
        
        self.raw_rotations = []
        
        self.furthest_point = [] #remove in a sec
        
        
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
        self.observer.calcpos(self.angle_y,self.angle_x,self.scale)

    def update_scale(self,scale):
        self.scale = scale
        self.observer.calcpos(self.angle_y,self.angle_z,self.scale)
        
    
    
    def project_points(self,position:tuple, debug:bool=False) -> list: #setter for rendered pointmap
        pointmap = []
        
        
        for point in self.point_map:
            if isinstance(point,Point): #my versioning isn't great, so as we shift to encapsulated point objects i'll prevent error here
                mat_point = point.xyz
            else:
                mat_point = point
            
            mat_point = np.matrix(mat_point)
            
            rotationalz, rotationaly, rotationalx = self.rotation()
            rotate = np.dot(rotationaly, mat_point.reshape((3,1)))
            
            
            rotate = np.dot(rotationalz, rotate)
            rotate = np.dot(rotationalx,rotate)
            self.raw_rotations.append(rotate)
            
            
            
            #furthest = self.point_map.index(point)
            
            
            
            projection = np.dot(self.manipulation_matrix,rotate)
            x = int(projection[0][0]*(200-self.scale)) + position[0] + self.movable_position[0]
            y = self.window_size[1] - (int(projection[1][0]*(200-self.scale)) + position[1]) + self.movable_position[1]
            pointmap.append((x,y))
        
        #DELETE LATER
        if debug:

            sc = 100 
            print(sc)
            projection = np.dot(self.manipulation_matrix,np.matrix(self.observer.position).reshape((3,1)))
            x = int(projection[0][0])*sc + position[0] + self.movable_position[0]
            y = self.window_size[1] - (int(projection[1][0])*sc + position[1]) + self.movable_position[1]
            pointmap.append((x,y))
            #
        self.rendered_pointmap = pointmap
        
        
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
            
            #furthest = self.point_map.index(point)
            
            
            
            projection = np.dot(self.manipulation_matrix,rotate)
            x = int(projection[0][0]*(200-self.scale)) + position[0] + self.movable_position[0]
            y = self.window_size[1] - (int(projection[1][0]*(200-self.scale)) + position[1]) + self.movable_position[1]
            pointmap.append((x,y))
        return raw_rotates, pointmap

    def rotation(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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