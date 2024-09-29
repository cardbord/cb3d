import pygame, requests, typing, os, pathlib, io
from pygame.font import get_default_font, Font
from pygame.gfxdraw import aacircle, filled_polygon
from math import sqrt, ceil
from enum import IntEnum, Enum

pygame.font.init()

def calc_rel_size() -> typing.Union[float,None]: #requies a running pyame display instance, errors if not initialized
    if not pygame.get_init():
        raise RuntimeError("No pygame display instance. Please use pygame.init() before running calc_rel_size()")
    else:
        winsize = pygame.display.get_desktop_sizes()[0]
        return round(sqrt((winsize[0]*winsize[1]))/1440,3)  #returns size scale factor
    
def scale_to_window(value:typing.Union[int,float]) -> float :
    return calc_rel_size() * value 


def CLOSE():
    if pygame.get_init():
        pygame.quit()
    exit()

class Anchor(IntEnum):
    TOP=0
    BOTTOM=1
    LEFT=2
    RIGHT=3
    TOPLEFT=4
    TOPRIGHT=5
    BOTTOMLEFT=6
    BOTTOMRIGHT=7
    CENTER = 8

class TextType(IntEnum):
    r'''
    Markup text types-
    
    h1: header 1
    h2: header 2
    h3: header 3
    
    p: paragraph text
    '''
    
    h1=64
    h2=48
    h3=32

    p=16


class GUIbaseClass: #provide attrs for other junk, because these things are included in everything
    def __init__(self):
        
        if pygame.get_init(): #small method to avoid no video system errors if GUIbaseClass is init before pygame
            self.window_size = pygame.display.get_desktop_sizes()[0]
        else:
            pygame.init() #we don't ideally want to init pygame here (that should be left to the main program), but just in case
            self.window_size = pygame.display.get_desktop_sizes()[0]
        self._fontSIZE = 50
        self._SIZE_SF = round(sqrt((self.window_size[0]*self.window_size[1]))/1440,3) #factor for monitor size, 1920x1080p default
        self.font = Font(get_default_font(),int(round(self._fontSIZE*self._SIZE_SF)))

        self._anchor = Anchor.CENTER #set through method


    def anchor(self, AnchorType:typing.Union[Anchor,int]):
        self._anchor = AnchorType.value if isinstance(AnchorType, Anchor) else AnchorType

        return self

class DisplayRows(GUIbaseClass):
    def __init__(self,
        objs,
        _parent_pos=None, #leave as None so that parents can auto-fill this later..
        _parent_window_size=None
    ):
        super().__init__()
        self.content = objs
        self.parent_pos = _parent_pos
        self.parent_window_size = _parent_window_size
        

    def _calc_obj_rel_pos(self,displace_height):
        avg_content_height = (self.parent_window_size[1] - displace_height)/len(self.content) #working out average height for each row
        for itemid in range(len(self.content)):
            if isinstance(self.content[itemid], (DisplayColumns,DisplayRows)):
                    self.content[itemid].parent_pos = [self.parent_pos[0], self.parent_pos[1]+ displace_height+(avg_content_height)*itemid]
                    self.content[itemid].parent_window_size = [self.parent_window_size[0],avg_content_height] #constrain window size to DisplayRow region allocated for each item
                    self.content[itemid]._calc_obj_rel_pos(0) #recursively call _calc_obj_rel_pos on children, with displace height of 0, since that's accounted for already
                    #this raises the oppurtunity for all sorts of content layout!
            else:
                if self.content[itemid]!=None:
                    match self.content[itemid]._anchor:
                        case 8: #center
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].button_rect.width)/2,
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].button_rect.height/2
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + 2*self._SIZE_SF),
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_box_height/2
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index, self.content[itemid]._textinput_id
                                ).anchor(self.content[itemid]._anchor)
                            #add support for raw images and raw text later...

                            elif isinstance(self.content[itemid], Image):
                                self.content[itemid].scale([1,avg_content_height],sticky_y=True)
                                self.content[itemid].pos = [
                                    self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].image_size[0])/2,
                                    self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].image_size[1]/2
                                ]

                            elif isinstance(self.content[itemid], Text):
                                self.content[itemid].pos = [
                                    self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].text_rect.w)/2,
                                    self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_rect.h/2
                                ]

                

                        case 7: #bottomright
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].button_rect.width),
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+1) - self.content[itemid].button_rect.height
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0]) + self.parent_window_size[0]-self.content[itemid].text_box_width-10*self._SIZE_SF,
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+1) - self.content[itemid].text_box_height
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                ).anchor(self.content[itemid]._anchor)

                        case 6: #bottomleft
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0],
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+1) - self.content[itemid].button_rect.height
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + 2*self._SIZE_SF),
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_box_height/2
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                ).anchor(self.content[itemid]._anchor)



                        case 5: #topright
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].button_rect.width),
                                        self.parent_pos[1] + displace_height + avg_content_height*itemid
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + self.parent_window_size[0]-self.content[itemid].user_text_width) ,
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_box_height/2
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                ).anchor(self.content[itemid]._anchor)


                        case 4: #topleft
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0],
                                        self.parent_pos[1] + displace_height + avg_content_height*itemid
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        self.parent_pos[0],
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_box_height/2
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                ).anchor(self.content[itemid]._anchor)

                        
                        case 2: #left
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0],
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].button_rect.height/2
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + 2*self._SIZE_SF),
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_box_height/2
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                ).anchor(self.content[itemid]._anchor)
                        
                            elif isinstance(self.content[itemid], Text):
                                self.content[itemid].pos = [
                                    self.parent_pos[0] + 12*self._SIZE_SF,
                                    self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_rect.h/2
                                ]
                        
                        case 1: #bottom
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].button_rect.width)/2,
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+1) - self.content[itemid].button_rect.height
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + 2*self._SIZE_SF),
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+1) - self.content[itemid].text_box_height
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                ).anchor(self.content[itemid]._anchor)

                        
                        case 0: #top
                            
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].button_rect.width)/2,
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid)
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                                
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + 2*self._SIZE_SF),
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid)
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                ).anchor(self.content[itemid]._anchor)
                                
                        case _: #default (center)
                            if isinstance(self.content[itemid], Button):
                            
                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].button_rect.width)/2,
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].button_rect.height/2
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    ).anchor(self.content[itemid]._anchor)
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + 2*self._SIZE_SF),
                                        self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_box_height/2
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                ).anchor(self.content[itemid]._anchor)

        


class DisplayColumns(GUIbaseClass):
    def __init__(self,
        objs,
        _parent_pos=None,
        _parent_window_size=None
    ):
        super().__init__()
        self.content = objs
        self.parent_pos = _parent_pos
        self.parent_window_size = _parent_window_size
        self._anchors = None
        

    def _calc_obj_rel_pos(self,displace_height):
        avg_content_width = self.parent_window_size[0]/len(self.content)
        #justify position relative to the rest of the window, then calculate the position of everything else
        for itemid in range(len(self.content)):
            if isinstance(self.content[itemid], (DisplayColumns,DisplayRows)):
                    self.content[itemid].parent_pos = [self.parent_pos[0]+(itemid*avg_content_width), self.parent_pos[1]]
                    self.content[itemid].parent_window_size = [avg_content_width,self.parent_window_size[1]-displace_height]
                    self.content[itemid]._calc_obj_rel_pos(displace_height)
            else:
                if self.content[itemid]!=None:
                    match self.content[itemid]._anchor:
                        case 8:
                
                            if isinstance(self.content[itemid], Button):
                                

                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0] + avg_content_width*(itemid+0.5) - self.content[itemid].button_rect.width/2,
                                        self.parent_pos[1] + displace_height + (self.parent_window_size[1]/2 - self.content[itemid].button_rect.height/2)
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    )
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + (avg_content_width*itemid) + 2*self._SIZE_SF),
                                        self.parent_pos[1] + displace_height + (self.parent_window_size[1]-self.content[itemid].text_box_height)/2
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index, self.content[itemid]._textinput_id
                                )

                            elif isinstance(self.content[itemid],Text): 
                                self.content[itemid].pos = [
                                    self.parent_pos[0] + (avg_content_width*(itemid+0.5) - self.content[itemid].text_rect.w/2),
                                    self.parent_pos[1] + displace_height + (self.parent_window_size[1]-self.content[itemid].text_rect.h)/2
                                    
                                ]





                        case _:
                            if isinstance(self.content[itemid], Button):
                                

                                self.content[itemid]=Button(
                                    [
                                        self.parent_pos[0] + avg_content_width*(itemid+0.5) - self.content[itemid].button_rect.width/2,
                                        self.parent_pos[1] + displace_height + (self.parent_window_size[1]/2 - self.content[itemid].button_rect.height/2)
                                    ],
                                    self.content[itemid].text_overlay,
                                    self.content[itemid]._buttonblocksize,
                                    self.content[itemid].highlighted_colour,
                                    self.content[itemid].callback
                                    )
                            elif isinstance(self.content[itemid], TextInput):
                                self.content[itemid]=TextInput(
                                    [
                                        (self.parent_pos[0] + (avg_content_width*itemid) + 2*self._SIZE_SF),
                                        self.parent_pos[1] + displace_height + (self.parent_window_size[1]-self.content[itemid].text_box_height)/2
                                    ],
                                    self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                                )
                            
                
            

class GUIobj(GUIbaseClass):

    r'''
    Base class for all window-based GUI objects.

    param  `pos`    position of the window to be drawn to the pygame display (it helps if the pygame display is fullscreen)
    param  `window_size`    size of the GUIobj window, stored as width/height
    param  `title`    title displayed at the top of the window

    '''

    def __init__(self,pos,window_size,title:str=None):
        super().__init__()
        # change size sf for monitor size
        self.pos = pos #stored as raw coords
        self.window_size = [ceil(window_size[0]*self._SIZE_SF), ceil(window_size[1] * self._SIZE_SF)] #stored as width/height, use ceil to ensure no small clipping
        self.border_colour = (0,0,0)
        self.clickableborder_pos = [self.window_size[0],50*self._SIZE_SF] #stored as width/height, syntax to check would be ``` if x in range(self.pos[0],self.clickableborder_pos[1]) ```
        self.parent_window_rect = pygame.Rect(self.pos[0],self.pos[1],self.window_size[0],self.window_size[1])
        self.clickableborder_area = pygame.Rect(self.pos[0],self.pos[1],self.clickableborder_pos[0],self.clickableborder_pos[1])
        self.clickable_cross = Button([self.pos[0]+self.clickableborder_pos[0]-50*self._SIZE_SF,self.pos[1]],"×",[50,50],(255,0,0)) # window size is corrected to _SIZE_SF automatically in Button.__init__()!
        self.title = title #display a title at the top of the window
        self.content = [] #display content
        #define other attrs in subclasses
        

    def move_window(self,mousepos): #should be called when a mouse click is detected on the window's clickable border, to change pos
        self.pos = mousepos
        self.clickableborder_pos = [self.window_size[0],50*self._SIZE_SF] #size sf is a pain with this one, it might not move the window properly
        self.clickableborder_area = pygame.Rect(self.pos[0],self.pos[1],self.clickableborder_pos[0],self.clickableborder_pos[1])
        self.parent_window_rect = pygame.Rect(self.pos[0],self.pos[1],self.window_size[0],self.window_size[1])
        self.clickable_cross = Button([self.pos[0]+self.clickableborder_pos[0]-50*self._SIZE_SF,self.pos[1]],"×",[50,50],(255,0,0)) #too many attributes to change in the old one, let's just make a new button with our updated pos and clickable border
        
        
    def __recursive_displayobj_display(self,obj,dis): #only accessed from GUIobj.display_window
        for item in obj.content: #provide self as the original obj parameter
            if isinstance(item,(DisplayColumns,DisplayRows)):
                self.__recursive_displayobj_display(item,dis) #carry on traversing, similar to a depth-first search
            else:
                if item!=None: #ensuring a NoneType.display error doesn't occur
                    item.display(dis)

    def display_window(self,dis:pygame.Surface): #draws all the window's rects to the screen, along with the close button
        pygame.draw.rect(dis,(255,255,255),self.parent_window_rect)
        pygame.draw.rect(dis,(255,255,255),self.clickableborder_area)
        pygame.draw.rect(dis,(0,0,0),self.parent_window_rect,width=1)
        pygame.draw.rect(dis,(0,0,0),self.clickableborder_area,width=1)

        self.__recursive_displayobj_display(self,dis) #calls recursive display, for contentblocks within the window

        self.clickable_cross._scaledis(dis)

        if self.title != None: 
            trect = self.font.render(self.title,True,(0,0,0))
            dis.blit(trect,[(self.pos[0]+20*self._SIZE_SF), (self.pos[1]+5*self._SIZE_SF)]) #displays title at 20px from the left, and 5px from the top of the window (px scaled)
             


    def check_windowcollide(self,xval,yval): #hover over window's top edge
        return True if (xval in range(self.pos[0], int(round(self.pos[0]+self.clickableborder_pos[0]))) and yval in range(self.pos[1], int(round(self.pos[1]+self.clickableborder_pos[1])))) else False

    def check_objcollide(self,xval,yval): #hover over entire window
        return True if (xval in range(self.pos[0], int(round(self.pos[0]+self.window_size[0]))) and yval in range(self.pos[1], int(round(self.pos[1]+self.window_size[1])))) else False

    def check_closebuttoncollide(self,xval,yval): #hover over window's close button in the top right corner
        return True if (xval in range(int(round(self.clickable_cross.button_rect.left)), int(round(self.clickable_cross.button_rect.right))) and yval in range(int(round(self.clickable_cross.pos[1])), int(round(self.clickable_cross.button_rect.bottom)))) else False

    def add_content(self, display_obj: typing.Union[DisplayColumns, DisplayRows]): #content addition function
        display_obj.parent_pos = self.pos 
        display_obj.parent_window_size = self.window_size #set parent_pos and parent_window_size post-init
        self.content = [display_obj] #set the current content to the object 
        self.content[0]._calc_obj_rel_pos(self.clickableborder_pos[1]) #arrange everything before displaying
        


class Button(GUIbaseClass):
    def __init__(self,pos,text_overlay,window_size:list = None,colourvalue:tuple=None,callback=None): #if no window_size, we approximate with text_overlay (mainly used for guiobj x button)
        super().__init__()
        self.pos = pos if isinstance(pos, (tuple,list)) else [0,0]
        self.text_overlay = text_overlay
        self.text = self.font.render(self.text_overlay,True,(0,0,0))
        self.text_box_width = max(42*self._SIZE_SF,self.font.size(self.text_overlay)[0]) if not window_size else window_size[0] * self._SIZE_SF
        self.text_box_height = self.font.get_height() if not window_size else window_size[1] * self._SIZE_SF
        self.highlighted_colour = colourvalue if colourvalue else (0,0,0)
        self.button_rect = pygame.Rect(self.pos[0],self.pos[1],self.text_box_width ,self.text_box_height)
        self.highlighted = False #we change this at some point in the main program to highlight with our selected colour, just by doing ```Button.highlighted = True; Button.display(dis)```
        self.callback = callback #function to execute once button is clicked
        self._buttonblocksize = window_size #this might be required to satisfy the recursive nature of content blocks, so i might remove it later

    def _scaledis(self,dis:pygame.Surface):
        pygame.draw.rect(dis,(0,0,0) if not self.highlighted else self.highlighted_colour,self.button_rect,1 if not self.highlighted else 0)
        dis.blit(self.text,(self.pos[0]+11*self._SIZE_SF,self.pos[1]-3*self._SIZE_SF))

    def display(self,dis:pygame.Surface): #method for Button which displays uncentered, use this for confirm buttons
        pygame.draw.rect(dis,(255,255,255),self.button_rect)
        pygame.draw.rect(dis,(0,0,0) if not self.highlighted else self.highlighted_colour,self.button_rect,1 if not self.highlighted else 0)
        dis.blit(self.text,(self.pos[0],self.pos[1]))
    
    def on_click(self,xval,yval):
        if (xval in range(int(round(self.button_rect.left)), int(round(self.button_rect.right))) and yval in range(int(round(self.pos[1])), int(round(self.button_rect.bottom)))):
            return (self.callback(), self.callback.__name__) if self.callback else True #if no callback is provided, use this as a collider so the main program can handle it
        else:
            return False
    

class TextInput(GUIbaseClass):
    def __init__(self,pos,text, _user_text=None, _current_userinp_index=None, textInputID:str=None):
        super().__init__() #init above GUIbaseClass
        self.pos = pos
        self.raw_text = text
        self._textinput_id = textInputID
        self.text = self.font.render(text,True,(0,0,0))
        self.to_input = False
        __size_text = self.text.get_size()
        self._pipeline_size = self.font.size("|")[0]
        self.text_box_width = __size_text[0]
        self.text_box_height = __size_text[1]
        self.text_rect = pygame.Rect(self.pos[0],self.pos[1],self.text_box_width,self.text_box_height)
        self.current_userinp_index = _current_userinp_index or 0
        self.user_text = _user_text or ""
        #render within display method
        self.user_text_width = max(200*self._SIZE_SF,self.font.size(self.user_text)[0]+self._pipeline_size) #chooses between 200px (at 1080p) or the user text + the size of the pipeline
        self.user_text_rect = pygame.Rect(self.pos[0]+self.text_box_width+10*self._SIZE_SF,self.pos[1],self.user_text_width,__size_text[1])
        
        
    
        
    def display(self,dis:pygame.Surface): #draws the TextInput, normally called by TextInputBox
        dis.blit(self.text,(self.pos))
        pygame.draw.rect(dis,(0,0,0),self.user_text_rect,width=1)
        render_text = self.font.render(self.user_text,True,(90,90,90))
        
        if self.to_input: #render a pipeline symbol at the end of the text if the TextInput is active for inputs
            pos_sym = "|"
            pos_sym = self.font.render(pos_sym,True,(10,10,10))
            dis.blit(pos_sym,(self.user_text_rect.topleft[0]+render_text.get_size()[0],self.user_text_rect.topleft[1]))
            
        dis.blit(render_text,self.user_text_rect.topleft)
        

    def add_char(self,newletter:str): #adds a single character a time (multiple characters not required as the limit is adding once per loop through event.unicode)
        self.user_text = (self.user_text[:self.current_userinp_index]+newletter+self.user_text[self.current_userinp_index:] if self.current_userinp_index!=len(self.user_text)-1 else "") if len(self.user_text)>0 else newletter
        #inserts the character into the middle of the current position (you can move through the text with arrow keys)
        self.user_text_width = max(200*self._SIZE_SF,self.font.size(self.user_text)[0]+self._pipeline_size)
        self.user_text_rect.w = self.user_text_width
        self.current_userinp_index+=1

    def backspace(self): #removes a character at the current pipeline position
        self.user_text = self.user_text[:self.current_userinp_index-1] + self.user_text[self.current_userinp_index+1:] 
        self.user_text_width = max(200*self._SIZE_SF,self.font.size(self.user_text)[0])
        self.user_text_rect.w = self.user_text_width #shortens the user text width of the user text rect
        self.current_userinp_index = self.current_userinp_index-1 if self.current_userinp_index != 0 else 0 #can't have a negative index, so i've just added a small check

    
        
class TextInputBox(GUIobj): #this is a type of window, derived from GUIobj. it collates TextInputs together to be handled 
    def __init__(self,pos,window_size,text_inputs:typing.List[TextInput],title:str=None, _topdisplacement:float=None):
        self.text_inputs = text_inputs
        super().__init__(pos,window_size,title)
        self.height = len(self.text_inputs) * self.text_inputs[0].text_box_height + 60*self._SIZE_SF
        self.width = max(i.text_box_width for i in text_inputs) 
        
        self.__s = self.font.size("Confirm")
        self.confirm_button = Button([self.window_size[0]+self.pos[0]-(self.__s[0]), (self.window_size[1]+self.pos[1])-(self.__s[1]) ],
                                     "Confirm",
                                     [(self.__s[0]/self._SIZE_SF),self.__s[1]/self._SIZE_SF])
        self.__GUIobjWinTop_Displacement = _topdisplacement or 50*self._SIZE_SF
        
        for t_input in range(len(self.text_inputs)):
            self.text_inputs[t_input].pos[1] = self.pos[1] + (self.__GUIobjWinTop_Displacement) + 60*self._SIZE_SF*t_input
            self.text_inputs[t_input].pos[0] = (self.pos[0] + 10*self._SIZE_SF)
            self.text_inputs[t_input].text_rect.y = self.text_inputs[t_input].pos[1]
            self.text_inputs[t_input].text_rect.x = self.text_inputs[t_input].pos[0]
            
            self.text_inputs[t_input].user_text_rect.y = self.text_inputs[t_input].text_rect.y
            self.text_inputs[t_input].user_text_rect.x = self.text_inputs[t_input].pos[0] + self.text_inputs[t_input].text_rect.width + 20*self._SIZE_SF

 
    def move_window(self,mousepos):
        super().move_window(mousepos)
        self.confirm_button = Button([self.window_size[0]+self.pos[0]-(self.__s[0]), (self.window_size[1]+self.pos[1])-(self.__s[1]) ],
                                     "Confirm",
                                     [(self.__s[0]/self._SIZE_SF),self.__s[1]/self._SIZE_SF], None, self.confirm_button.callback)
        for t_input in range(len(self.text_inputs)):
            self.text_inputs[t_input].pos[1] = self.pos[1] + (self.__GUIobjWinTop_Displacement) + 60*self._SIZE_SF*t_input #adjust distance dependent multiple of font size (figure out later)
            self.text_inputs[t_input].pos[0] = (self.pos[0] + 10*self._SIZE_SF)

            self.text_inputs[t_input].text_rect.y = self.text_inputs[t_input].pos[1]
            self.text_inputs[t_input].text_rect.x = self.text_inputs[t_input].pos[0]
            
            self.text_inputs[t_input].user_text_rect.y = self.text_inputs[t_input].pos[1]
            self.text_inputs[t_input].user_text_rect.x = self.text_inputs[t_input].pos[0] + self.text_inputs[t_input].text_rect.width + 20*self._SIZE_SF
            
    def on_collide(self,xval,yval):
        
        if self.confirm_button.callback != None and xval in range(self.confirm_button.button_rect.left, self.confirm_button.button_rect.right) and yval in range(self.confirm_button.button_rect.top, self.confirm_button.button_rect.bottom):
            self.confirm_button.callback()

            
        for t_input in range(len(self.text_inputs)):
            if xval in range(self.text_inputs[t_input].user_text_rect.left,self.text_inputs[t_input].user_text_rect.right) and yval in range(self.text_inputs[t_input].user_text_rect.top,self.text_inputs[t_input].user_text_rect.bottom):
                self.text_inputs[t_input].to_input = True

                for t2_input in range(len(self.text_inputs)):
                    if t2_input != t_input:
                        self.text_inputs[t2_input].to_input = False
                break
            

        
    
    def display(self,dis:pygame.Surface):
        self.display_window(dis)
        
        self.confirm_button.display(dis)
        
        for _ in range(len(self.text_inputs)):
            self.text_inputs[_].display(dis)


    
    
    

class Dropdown(GUIbaseClass): # as with TextInputBox and text inputs, we have a class that collates multiple buttons together
    def __init__(self,pos,placeholder:Button,buttons:typing.List[Button]):
        super().__init__()
        self.pos = pos
        self.placeholder = placeholder
        
        self.buttons = buttons #calcuate the buttons positions from this array
        self.__dropdown_displace_height = self.placeholder.button_rect.height
        self.is_dropped = False
        self._calc_button_rel_pos()
        self.placeholder.callback = self.__inv_drop


    def __inv_drop(self):
        self.is_dropped=not self.is_dropped

    def _calc_button_rel_pos(self):
        for b_index in range(len(self.buttons)):
            self.buttons[b_index].pos[1] += (self.__dropdown_displace_height if b_index == 0 else 0 + (self.buttons[b_index -1].button_rect.bottom if b_index > 0 else 0)) 
            self.buttons[b_index].pos[0] = self.pos[0] #overwrite x completely
            self.buttons[b_index].button_rect.y = self.buttons[b_index].pos[1]
            self.buttons[b_index].button_rect.x = self.buttons[b_index].pos[0]

    def display(self,dis:pygame.Surface):
        self.placeholder.display(dis)
        if self.is_dropped:
            for button in self.buttons:
                button.display(dis)

    def on_click(self,xval,yval):
        return self.placeholder.on_click(xval,yval) #just use our on_click method now





class Drawing(GUIobj):
    def __init__(self,pos,window_size,title=None):
        super().__init__(
            pos,
            window_size,
            title if title else "Drawing"
        )
        self.drawdata = []
        self.pos_on_grid = [0,0]
        self.zoom_scale = 40
        self.text_highlight_font = pygame.font.SysFont('Segoe UI', int(round(15*self._SIZE_SF)))
        self.grid_text = self.text_highlight_font.render(f'{self.pos_on_grid[0]}, {self.pos_on_grid[1]}', True, (100,100,100))
        self.hovered = False
        self.draw_button = Button([0,0],"Draw") #spawn child window from this, with x/y, y/z, and x/z planes, attach callback in main

        
        self.grid_size = [ (self.window_size[0]/self._SIZE_SF)//self.zoom_scale, (self.window_size[1]/self._SIZE_SF)//self.zoom_scale] 

    def add_content(self): #override content addition since there's nowhere for it to go!
        pass

    def _convert_x(self,value):
        return value*self.zoom_scale*self._SIZE_SF+self.pos[0]
    
    def _convert_y(self,value):
        return abs(value*self._SIZE_SF*self.zoom_scale-self.window_size[1]-self.pos[1])

    def display(self,dis:pygame.Surface): # override display_window functionality since parts need to be drawn without any clever components
        pygame.draw.rect(dis,(255,255,255),self.parent_window_rect)
        

        pos_converted = (int(round(self._convert_x(self.pos_on_grid[0]))), int(round(self._convert_y(self.pos_on_grid[1]))))

        
        aacircle(dis,pos_converted[0] , pos_converted[1], 7, (104,115,174))  
        
        for i in range(int(self.grid_size[0])):
            if i == 0:
                pygame.draw.line(dis,(0,0,0),[self._convert_x(i) , self.pos[1]+self.window_size[1]], [self._convert_x(i) , self.pos[1]], 3)    
            else:
                pygame.draw.aaline(dis,(150,150,150,(210)),[self._convert_x(i) , self.pos[1]+self.window_size[1]], [self._convert_x(i) , self.pos[1]])
        
        for j in range(int(self.grid_size[1])):
            if j == 0:
                pygame.draw.line(dis, (0,0,0), [self.pos[0], self._convert_y(j)], [self.pos[0]+self.window_size[0], self._convert_y(j)], 3)
            else:
                pygame.draw.aaline(dis, (150,150,150,(210)), [self.pos[0], self._convert_y(j)], [self.pos[0]+self.window_size[0], self._convert_y(j)])

        transformed_drawdata = [[self._convert_x(i[0]), self._convert_y(i[1])] for i in self.drawdata]
        valid = True
        for pointToCheck in self.drawdata:
            if pointToCheck[0] > self.grid_size[0] or pointToCheck[1] > self.grid_size[1]:
                valid = False

        if len(self.drawdata) > 0 and valid:
            if len(self.drawdata) > 2:
                filled_polygon(dis, transformed_drawdata, (251,198,207,(220)))

            if self.hovered:
                
                pygame.draw.aaline(dis,(100,100,100,(210)),[transformed_drawdata[-1][0], transformed_drawdata[-1][1]],[self._convert_x(self.pos_on_grid[0]), self._convert_y(self.pos_on_grid[1])])
                
            for point_index in range(1,len(self.drawdata)):
                _previous_point = transformed_drawdata[point_index-1]
                _current_point = transformed_drawdata[point_index]

                pygame.draw.line(dis,(0,0,150),[_previous_point[0],_previous_point[1]], [_current_point[0],_current_point[1]], 2)                

            


        dis.blit(self.grid_text,[pos_converted[0] + 5*self._SIZE_SF, pos_converted[1] - 20*self._SIZE_SF])

        for point in self.drawdata:
            if point[0] <= self.grid_size[1] and point[1] <= self.grid_size[1]:
                pygame.draw.circle(dis, (0,0,210), (self._convert_x(point[0]), self._convert_y(point[1])), 5)

        pygame.draw.rect(dis,(255,255,255),self.clickableborder_area)
        pygame.draw.rect(dis,(0,0,0),self.parent_window_rect,width=1)
        
        pygame.draw.rect(dis,(0,0,0),self.clickableborder_area,width=1)
        if self.title != None:
            trect = self.font.render(self.title,True,(0,0,0))
            dis.blit(trect,[(self.pos[0]+20*self._SIZE_SF), (self.pos[1]+5*self._SIZE_SF)])
        
        self.clickable_cross._scaledis(dis)
        
        self.draw_button.pos = [self.pos[0]+self.window_size[0]-self.draw_button.button_rect.w , self.pos[1]+self.window_size[1]-self.draw_button.button_rect.h]
        self.draw_button.button_rect.x = self.pos[0]+self.window_size[0]-self.draw_button.button_rect.w
        self.draw_button.button_rect.y = self.pos[1]+self.window_size[1]-self.draw_button.button_rect.h
        
        self.draw_button.display(dis)


    

    
    def scrolled_on(self,value,mx,my):
        if self.check_objcollide(mx,my) and not self.check_windowcollide(mx,my) and not self.draw_button.button_rect.collidepoint(mx,my) and self.zoom_scale+value/2 > 0:
            self.zoom_scale+=value/2 
            self.grid_size = [ (self.window_size[0]/self._SIZE_SF)//self.zoom_scale, (self.window_size[1]/self._SIZE_SF)//self.zoom_scale] 

    def on_hover(self,mx,my):
        
        self.hovered = True
        if self.check_objcollide(mx,my) and not self.check_windowcollide(mx,my) and not self.draw_button.button_rect.collidepoint(mx,my):
            pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
                
            self.pos_on_grid = [ ((mx-self.pos[0])/self._SIZE_SF)//self.zoom_scale , ((self.pos[1]-my+self.window_size[1])/self._SIZE_SF)//self.zoom_scale ]
            
            self.grid_text = self.text_highlight_font.render(f'{self.pos_on_grid[0]}, {self.pos_on_grid[1]}', True, (10,10,10))
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.hovered=False

    def on_click(self,mx,my):
        
        if self.check_objcollide(mx,my) and not self.check_windowcollide(mx,my):
            if self.draw_button.button_rect.collidepoint(mx,my):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return self.draw_button.callback(self.drawdata)
            else:
                self.drawdata.append(self.pos_on_grid)
                
        
            

class menu(GUIobj): # i wonder... will setting window size to 1080p remove any need to descale?
    def __init__(self, window_dropdowns:typing.List[Dropdown]): #maybe just add dropdowns as a param?
        super().__init__([0,0],(1920,1080))
        self.clickable_cross.callback = CLOSE
        #we don't need a custom closebutton, this comes included... we just provide it with a different callback

        self.dropdowns = window_dropdowns
    
    def move_window(self, mousepos):
        #return super().move_window(mousepos) <- this is overriden as the menu window should ideally not be moved around! 
        pass
    
    def display_window(self,dis): #override GUIobj display window for extra functionality
        super().display_window(dis)
        for dropdown in self.dropdowns:
            dropdown.display(dis)
        
#make more generalised `window` class for easier use of GUIobj, abstracting more from the end-user (working with GUIobj isn't ideal)

class window(GUIobj):
    ... #here!
    


class Text(GUIbaseClass): #standard text - no interaction
    def __init__(self,
                pos,
                text_str:str,
                type:TextType=None, #TextType is an enum for different font sizes
                *, #keyword args from here onwards, as they are only for customisation 
                colour:tuple=None,
                ul:bool=False,
                italic:bool=False,
                bold:bool=False,
                strikethrough:bool=False,
                font:str=None, #override font attr with a new one here

                ):
        super().__init__() #init GUIbaseClass

        if not pygame.font.get_init(): 
            pygame.font.init() #to avoid display error just in case font has not been initialised (somehow)
        
        self.pos = pos
        self.raw_text=text_str
        self.colour = colour or (0,0,0) #sets colour to black if it is None
        self.type=type or TextType.p
        
        if font:
            self.font = pygame.font.SysFont(font, round(self.type.value*self._SIZE_SF), bold, italic)
        else: #chooses the OS default font instead
            self.font = pygame.font.SysFont(get_default_font(),round(self.type.value*self._SIZE_SF), bold, italic)
            

        self.font.set_underline(ul)
        self.font.set_strikethrough(strikethrough)
            
        self.text = self.font.render(self.raw_text, True, self.colour)

        self.text_rect = self.text.get_rect() #for width and height values


    def display(self,dis:pygame.Surface): #display method for self.text
        dis.blit(self.text,self.pos)
        
 #callback=None #we can treat images as buttons by attaching the same callback functionality to them!   
    
    
class Image(GUIbaseClass):
    def __init__(self,
                 pos,
                 image:str | pygame.Surface,
                 scaling:list=None,
    ):
        super().__init__() #init above GUIbaseClass
        self.pos = pos
        path = str(pathlib.Path(__file__).parent)+'\\content\\' #path is constructed to cb3d/main/utils/content to grab image
        if isinstance(image,pygame.Surface):
            self.image=image
        else:
            if '\\' in image and os.path.exists(image): #image is most likely a full file path
                self.image=pygame.image.load(image)

            elif image.count('.') == 1 and os.path.exists(path+image): #image has only one . (for filetype)
                self.image=pygame.image.load(path+image)

            else:
                try: #try/except here as there can be network errors
                    r=requests.get(image)
                    if r.status_code in range(200,299): #http protocol's standard range of codes for success
                        _temp_stream=io.BytesIO(r.content) #loads the site's content into memory with a buffer
                        self.image=pygame.image.load(_temp_stream)

                    else:
                        raise ConnectionError(f"{image} could not be resolved. Status code {r.status_code}") #network error
                    
                except requests.exceptions.RequestException: #invalid url, format, or schema
                    raise ValueError(f"{image} is an invalid url. Please provide a url or valid file path for this image.")
                    
        self.image_size = scaling or self.image.get_size()
        if scaling:
            self.image=pygame.transform.scale(self.image,scaling) #scale the image to the target resolution if scaling is present


    def display(self,dis:pygame.Surface): #display method
        dis.blit(self.image,self.pos)


    def scale(self, new_size, *, sticky_x:bool=False,sticky_y:bool=False): #scaling method, used in displayrows/columns
        if new_size != self.image_size:
            if sticky_x:
                _scale_sf = self.image_size[0]/self.image_size[1] #div xlen by ylen for scaling
                new_size[1] = new_size[0]/_scale_sf #scale the 
            elif sticky_y:
                _scale_sf = self.image_size[1]/self.image_size[0] #rely on ylen instead for ratio
                new_size[0] = new_size[1]/_scale_sf

            self.image_size = new_size #update image size and transform image
            self.image=pygame.transform.scale(self.image,new_size)
        
        
        

    


    def on_click(self,mx,my):
        if mx in range(int(round(self.pos[0])), int(round(self.pos[0]+self.image_size[0]))) and my in range(int(round(self.pos[1])), int(round(self.pos[1]+self.image_size[1]))):
            if self.callback != None:
                return self.callback()
            else:
                return True
            
    def set_callback(self,callback):
        self.callback = callback
        return self
    
    
#HANDLER

class Handler:
    def __init__(self):
        self.GUIobjs_array = []
        self.wecheck = False
        self.previously_moved = 0
        self.moved_in_cycle = False
        self.eventLog: list = [] #update each cycle
        
        self.menu:menu = None
    
    class Event(Enum): #enums are lovely... using this to mimic pygame's event system, except for specifically listening to my own junk!
        
        
        move=1 #an obj's window is clicked and dragged by its clickable border
        click=2 #an obj's on_click method is called, or a click is handled somehow within it
        scroll=3 #the mouse scroll wheel has been used within an object's window

        type=4 #a keyboard character is registered whilst the highlighted object's to_input==True
        backspace=5 #a backspace is registered whilst the highlighted object's to_input==True

        remove=6 #an obj is removed from the Handler
        add=7 #an obj is added to the Handler via an external source
        create=8 #an obj is added to the Handler via an internal source, one of the current Handler objects




    def add(self, obj:GUIobj):
        self.GUIobjs_array.append(obj)
        self.eventLog.append((obj.title,self.Event.add))
    
    def __recursive_displayobj_texthandling(self, obj,unicode, _backspace=False):
        for item in obj.content:
            if isinstance(item, (DisplayColumns, DisplayRows)):
                self.__recursive_displayobj_texthandling(item,unicode,_backspace)
            else:
                if isinstance(item,TextInput) and item.to_input:
                    if not _backspace:
                        item.add_char(unicode)
                    else:
                        item.backspace()
    
    def __recursive_displayobj_disableinput(self,obj,hashval):
        for item in obj.content:
            if isinstance(item,(DisplayColumns,DisplayRows)):
                self.__recursive_displayobj_disableinput(item,hashval)
            else:
                if isinstance(item,TextInput) and hash(item) != hashval:
                    item.to_input = False
    
    def __recursive_displayobj_onclick(self,obj,xval,yval,_original_object=None):
        
        for item in obj.content:
            if isinstance(item,(DisplayRows,DisplayColumns)):
                self.__recursive_displayobj_onclick(item,xval,yval,obj)
                
            else:
                if isinstance(item,TextInput) and xval in range(item.user_text_rect.left,item.user_text_rect.right) and yval in range(item.user_text_rect.top,item.user_text_rect.bottom):
                    item.to_input = True
                    self.__recursive_displayobj_disableinput(_original_object,hash(item))
                    break
                elif isinstance(item,Button) and xval in range(item.button_rect.left,item.button_rect.right) and yval in range(item.button_rect.top,item.button_rect.bottom):
                    item.on_click(xval,yval)
                    break
                elif isinstance(item,Image) and xval in range(int(round(item.pos[0])), int(round(item.pos[0]+item.image_size[0]))) and yval in range(int(round(item.pos[1])), int(round(item.pos[1]+item.image_size[1]))):
                    item.on_click(xval,yval)
                    break


    def __recursive_textinput_itext(self,obj, _text_returns:dict={}):
        
        for item in obj.content:
            if isinstance(item, (DisplayColumns, DisplayRows)):
                _text_returns = self.__recursive_textinput_itext(item,_text_returns)
            else:
                if isinstance(item, TextInput):
                    
                    _text_returns[item._textinput_id if item._textinput_id != None else item.raw_text] = item.user_text
        return _text_returns        
        
    
    def display(self,dis):
        
        for i in range(len(self.GUIobjs_array),0,-1):
            self.GUIobjs_array[i-1].display(dis) if isinstance(self.GUIobjs_array[i-1],TextInputBox) or isinstance(self.GUIobjs_array[i-1],Drawing) else self.GUIobjs_array[i-1].display_window(dis)
        
            if isinstance(self.GUIobjs_array[0], Drawing):
                x,y = pygame.mouse.get_pos()
                self.GUIobjs_array[0].on_hover(x,y)
        
    def handle_event(self,event,x,y):
        self.eventLog = []
        
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_BACKSPACE:
                if len(self.GUIobjs_array)>0 and isinstance(self.GUIobjs_array[0],TextInputBox):
                    for t_input in self.GUIobjs_array[0].text_inputs:
                        if t_input.to_input:
                            t_input.backspace()
                else:
                    self.__recursive_displayobj_texthandling(self.GUIobjs_array[0],"absolutely nothing",True) #we can supply "absolutely" nothing to this as the funct handles both backspaces and text addition
                

                self.eventLog.append((self.GUIobjs_array[0].title,self.Event.backspace))

                        
            elif len(self.GUIobjs_array) > 0:
                self.addTIBtext(event.unicode)
                self.eventLog.append((self.GUIobjs_array[0].title,self.Event.type))

                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
            
                if len(self.GUIobjs_array) > 0 and self.GUIobjs_array[0].check_closebuttoncollide(x,y):
                    self.eventLog.append((self.GUIobjs_array[0].title,self.Event.remove)) #don't forget to do this early, otherwise we're reporting some other object's event! (or just IndexErroring)
                    self.GUIobjs_array.pop(0)
                    
                    
                    
                
                else:
                    for d in range(len(self.GUIobjs_array)):
                        if d==0:
                            returntype = None
                            if isinstance(self.GUIobjs_array[d], TextInputBox):
                                returntype = self.GUIobjs_array[d].on_collide(x,y)
                            elif isinstance(self.GUIobjs_array[0],Drawing): #drawing must be above GUIobj here, as it is a GUIobj itself
                                returntype = self.GUIobjs_array[d].on_click(x,y)
                            elif isinstance(self.GUIobjs_array[0],GUIobj):
                                returntype = self.__recursive_displayobj_onclick(self.GUIobjs_array[0],x,y)
                             

                            if returntype != None and isinstance(returntype, GUIobj): #check for object creator buttons
                                self.GUIobjs_array.insert(0,returntype)
                                self.eventLog.append((self.GUIobjs_array[0].title,self.Event.create))
                            else:
                                self.eventLog.append((self.GUIobjs_array[0].title,self.Event.click)) #let's seperate these two, otherwise different

                                
                        else:
                            if isinstance(self.GUIobjs_array[0],TextInputBox):
                                self.eventLog.append((self.GUIobjs_array[0].title,self.Event.click))
                                for t_input in self.GUIobjs_array[d].text_inputs:
                                    t_input.to_input = False
                            
                self.wecheck = True #check for collisions in this cycle
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.wecheck = False

        elif event.type == pygame.MOUSEWHEEL:
            for obj in self.GUIobjs_array:
                if isinstance(obj,Drawing):
                    obj.scrolled_on(event.y,x,y)
                    self.eventLog.append((obj.title,self.Event.scroll))
                    
        
        self.moved_in_cycle = False
        if len(self.GUIobjs_array) > 1 and self.previously_moved != 0:
            self.GUIobjs_array[0], self.GUIobjs_array[self.previously_moved] = self.GUIobjs_array[self.previously_moved], self.GUIobjs_array[0]
            self.previously_moved = 0
        
        
        for display_object in self.GUIobjs_array:
            if self.wecheck and display_object.check_windowcollide(x,y) and (not self.GUIobjs_array[0].check_objcollide(x,y) if self.GUIobjs_array.index(display_object) != 0 else True):
                if not self.moved_in_cycle:
                    
                    newx, newy = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                    display_object.move_window([display_object.pos[0]+(newx-x),display_object.pos[1]+(newy-y)]) #there's a hilarious logic problem here where you can merge windows by dragging them around, so we'll have to track one movement per cycle
                    self.moved_in_cycle = True
                    self.previously_moved = self.GUIobjs_array.index(display_object) # this is getting sketchy now, i'm smelling a big rewrite for optimisation in the future!
                    if hasattr(display_object,"content"):

                        for contentblock in display_object.content:
                            contentblock.parent_pos = display_object.pos
                            contentblock._calc_obj_rel_pos(50*display_object._SIZE_SF)

                    self.eventLog.append((display_object.title,self.Event.move))
                    
        for contentblock in self.GUIobjs_array:
                
            if contentblock.check_closebuttoncollide(x,y):
            
                contentblock.clickable_cross.highlighted = True
            else:
                contentblock.clickable_cross.highlighted = False
            
    def collate_textinput_inputs(self):
        return self.__recursive_textinput_itext(self.GUIobjs_array[0])
       
        
    def addTIBtext(self,unicode):
        
        if isinstance(self.GUIobjs_array[0],TextInputBox):
            for t_input in self.GUIobjs_array[0].text_inputs:
                if t_input.to_input:    
                    t_input.add_char(unicode)
                    
        elif hasattr(self.GUIobjs_array[0], "content"):
            for contentblock in self.GUIobjs_array[0].content:
                self.__recursive_displayobj_texthandling(contentblock,unicode)
                
                
                
    def handle_menu_event(self,event,x,y): #menu doesn't require logging, since it already yields everything it does.
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.menu.check_windowcollide(x,y):
                    
                        for dropdown in self.menu.dropdowns:
                            dropdown.on_click(x,y)
                        
                            
                        self.menu.clickable_cross.on_click(x,y)
                
                
                    for dropdown in self.menu.dropdowns:
                            if dropdown.is_dropped:
                                for button in dropdown.buttons:
                                    _record = button.on_click(x,y)
                                    if isinstance(_record,tuple):
                                        yield _record
                                        

                                        

        
        if self.menu.check_closebuttoncollide(x,y):
            self.menu.clickable_cross.highlighted=True
        else:
            self.menu.clickable_cross.highlighted=False
            
