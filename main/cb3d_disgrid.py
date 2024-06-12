import numpy as np
import math as m
import pygame
from typing import Tuple
from model import Point
from model import CBModel
from random import randrange
from utils.textures.catalogue import Textures


pygame.init()
default_font = pygame.font.get_default_font()


class Texture:
    def __init__(self, filename, transparency_level=1, tx=None, ty=None):
        self.filename = filename
        self.texture_map = pygame.image.load(filename).convert_alpha()
        self.transparency = transparency_level
        
        self.tx = tx or randrange(0,int(round(self.texture_map.get_width()/3))) #apply randomness to texture positions
        self.ty = ty or randrange(0,int(round(self.texture_map.get_height()/3)))
        
class TextureCatalogue:
    @property
    def textures(self):
        _textures = {}
        _texts = Textures()
        for t in _texts.tmap:
            imgpath = ''
            texture_transparency=1.0
            tx=None
            ty=None
            if _texts.tmap[t][0].endswith('.cbtx'):
                with open(_texts.tmap[t][0], "r") as readable:
                    texture_info = readable.readlines()
                    texture_transparency = float(texture_info[1].replace('\n'))
                    if len(texture_info) > 2:
                        tx = int(texture_info[2].replace('\n'))
                        ty = int(texture_info[3].replace('\n'))
                imgpath = _texts.tmap[t][1]
                

            else:
                with open(_texts.tmap[t][1], "r") as readable:
                    texture_info = readable.readlines()
                    texture_transparency = float(texture_info[1].replace('\n'))
                    if len(texture_info) > 2:
                        tx = int(texture_info[2].replace('\n'))
                        ty = int(texture_info[3].replace('\n'))
                
                imgpath = _texts.tmap[t][0]
            
            

            _textures[t] = Texture(imgpath,texture_transparency,tx,ty)

        return _textures


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
        self.position = [0,0,0] #init through calcpos
        
    def calcpos(self,angle_x,angle_y, scale):
        #nasty code, but it works!
        
        
        xlen = abs(scale)*m.cos(m.pi*2 - angle_x)
        zlen = abs(scale)*m.sin(m.pi*2 - angle_x)
        
        ylen = (abs(scale)*m.cos(m.pi*2 - angle_y))
        hidden_z = scale*m.sin(m.pi*2 - angle_y)
        
        sf = (scale**2)/hidden_z
        self.position = [xlen/sf, zlen/sf, ylen]

    def calc_dist_topoint(self,point):
        try:
            return m.sqrt(abs((self.position[0] - point[0][0])**2 + (self.position[1] - point[1][0])**2 + (self.position[2] - point[2][0])**2))
        except Exception as e:
            print(f"erred on here, here's why: {e}")
            return 10000

        


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
            mat_point = point.xyz #the point here is of the Point datatype, specified in model.py
            
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
            
            #furthest = self.point_map.index(point)
            
            
            
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