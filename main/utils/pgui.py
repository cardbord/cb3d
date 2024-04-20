import pygame #do we make enum class for types at some point? #no, are you stupid? - future me
from pygame.font import get_default_font, Font
import typing
from math import sqrt, ceil
from enum import IntEnum

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



class GUIbaseClass: #provide attrs for other junk, because these things are included in everything
    def __init__(self):
        
        if pygame.get_init(): #small method to avoid no video system errors if GUIbaseClass is init before pygame
            self.window_size = pygame.display.get_desktop_sizes()[0]
        else:
            pygame.init() #we don't ideally want to init pygame here (that should be left to the main program), but just in case
            self.window_size = pygame.display.get_desktop_sizes()[0]
        self._fontSIZE = 50
        self._SIZE_SF = round(sqrt((self.window_size[0]*self.window_size[1]))/1440,3) #factor for monitor size, 1920x1080p default
        self._ASIZE_SF = round((self.window_size[0]*self.window_size[1])/2073600,2) #whelp, our area-based size scaling returns
        self.font = Font(get_default_font(),int(round(self._fontSIZE*self._SIZE_SF)))

        self._anchor = Anchor.CENTER #set through method


    def anchor(self, AnchorType:typing.Union[Anchor,int]):
        self._anchor = AnchorType.value if isinstance(AnchorType, Anchor) else AnchorType

        return self

class  DisplayRows(GUIbaseClass):
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
        avg_content_height = (self.parent_window_size[1] - displace_height)/len(self.content) #just make sure parent_window_size is provided by the time this is called, then things work!
        for itemid in range(len(self.content)):
            if isinstance(self.content[itemid], (DisplayColumns,DisplayRows)):
                    self.content[itemid].parent_pos = [self.parent_pos[0], self.parent_pos[1]+ displace_height+(avg_content_height)*itemid]
                    self.content[itemid].parent_window_size = [self.parent_window_size[0],avg_content_height]
                    self.content[itemid]._calc_obj_rel_pos(displace_height) #recursively call _calc_obj_rel_pos on children, not before constraining scaling area to the current content block size.
                    #this raises the oppurtunity for all sorts of content layout!
            else:
                match self.content[itemid]._anchor:
                    case 8:
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
                        #add support for raw images and raw text later...
            

                    case 7:
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

                    case 6:
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
                                    self.parent_pos[0] + (self.parent_window_size[0]-self.content[itemid].button_rect.width)/2,
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
                                    (self.parent_pos[0] + self.content[itemid].user_text_width/2) ,
                                    self.parent_pos[1] + displace_height + avg_content_height*(itemid+0.5) - self.content[itemid].text_box_height/2
                                ],
                                self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                            ).anchor(self.content[itemid]._anchor)


                    
                    case 1:
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

                    
                    case 0:
                        
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
                            
                    case _:
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
                                self.content[itemid].raw_text, self.content[itemid].user_text, self.content[itemid].current_userinp_index
                            )







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

    Will be initialized automatically through other GUI objects. It is encouraged to use those instead, as they all inherit from this.
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
        self.title = title #init later
        self.content = [] #display content
        #define other attrs in subclasses
        


    def move_window(self,mousepos): #should be called when a mouse click is detected on the window's clickable border, to change pos
        self.pos = mousepos
        self.clickableborder_pos = [self.window_size[0],50*self._SIZE_SF] #size sf is a pain with this one, it might not move the window properly
        self.clickableborder_area = pygame.Rect(self.pos[0],self.pos[1],self.clickableborder_pos[0],self.clickableborder_pos[1])
        self.parent_window_rect = pygame.Rect(self.pos[0],self.pos[1],self.window_size[0],self.window_size[1])
        self.clickable_cross = Button([self.pos[0]+self.clickableborder_pos[0]-50*self._SIZE_SF,self.pos[1]],"×",[50,50],(255,0,0)) #too many attributes to change in the old one, let's just make a new button with our updated pos and clickable border
        #render updates should change automatically from this, maybe?
        
    def __recursive_Displayobj_display(self,obj,dis):
        for item in obj.content:
            if isinstance(item,(DisplayColumns,DisplayRows)):
                self.__recursive_Displayobj_display(item,dis)
            else:
                item.display(dis) if not isinstance(item,Button) else item._NSdis(dis)

    def display_window(self,dis:pygame.Surface):
        pygame.draw.rect(dis,(255,255,255),self.parent_window_rect)
        pygame.draw.rect(dis,(255,255,255),self.clickableborder_area)
        pygame.draw.rect(dis,(0,0,0),self.parent_window_rect,width=1)
        pygame.draw.rect(dis,(0,0,0),self.clickableborder_area,width=1)
        if self.title != None:
            trect = self.font.render(self.title,True,(0,0,0))
            dis.blit(trect,[(self.pos[0]+20*self._SIZE_SF), (self.pos[1]+5*self._SIZE_SF)])
        self.__recursive_Displayobj_display(self,dis)        
                
        
        self.clickable_cross.display(dis)

    def check_windowcollide(self,xval,yval):
        return True if (xval in range(self.pos[0], int(round(self.pos[0]+self.clickableborder_pos[0]))) and yval in range(self.pos[1], int(round(self.pos[1]+self.clickableborder_pos[1])))) else False

    def check_objcollide(self,xval,yval):
        return True if (xval in range(self.pos[0], int(round(self.pos[0]+self.window_size[0]))) and yval in range(self.pos[1], int(round(self.pos[1]+self.window_size[1])))) else False

    def check_closebuttoncollide(self,xval,yval):
        return True if (xval in range(int(round(self.clickable_cross.button_rect.left)), int(round(self.clickable_cross.button_rect.right))) and yval in range(int(round(self.clickable_cross.pos[1])), int(round(self.clickable_cross.button_rect.bottom)))) else False

    def add_content(self, display_obj: typing.Union[DisplayColumns, DisplayRows]):
        display_obj.parent_pos = self.pos
        display_obj.parent_window_size = self.window_size
        self.content = [display_obj]
        self.content[0]._calc_obj_rel_pos(self.clickableborder_pos[1])
        


class Button(GUIbaseClass):
    def __init__(self,pos,text_overlay,window_size:list = None,colourvalue:tuple=None,callback=None): #if no window_size, we approximate with text_overlay (mainly used for guiobj x button)
        super().__init__()
        self.pos = pos
        self.text_overlay = text_overlay
        self.text = self.font.render(self.text_overlay,True,(0,0,0))
        self.text_box_width = max(42*self._SIZE_SF,self.font.size(self.text_overlay)[0]) if not window_size else window_size[0] * self._SIZE_SF
        self.text_box_height = self.font.get_height() if not window_size else window_size[1] * self._SIZE_SF
        self.highlighted_colour = colourvalue if colourvalue else (0,0,0)
        self.button_rect = pygame.Rect(self.pos[0],self.pos[1],self.text_box_width ,self.text_box_height)
        self.highlighted = False #we change this at some point in the main program to highlight with our selected colour, just by doing ```Button.highlighted = True; Button.display(dis)```
        self.callback = callback #function to execute once button is clicked
        self._buttonblocksize = window_size #this might be required to satisfy the recursive nature of content blocks, so i might remove it later

    def display(self,dis:pygame.Surface):
        pygame.draw.rect(dis,(0,0,0) if not self.highlighted else self.highlighted_colour,self.button_rect,1 if not self.highlighted else 0)
        dis.blit(self.text,(self.pos[0]+11*self._SIZE_SF,self.pos[1]-3*self._SIZE_SF))

    def _NSdis(self,dis:pygame.Surface): #method for Button which displays uncentered, use this for confirm buttons
        pygame.draw.rect(dis,(0,0,0) if not self.highlighted else self.highlighted_colour,self.button_rect,1 if not self.highlighted else 0)
        dis.blit(self.text,(self.pos[0],self.pos[1]))
    
    def on_click(self,xval,yval):
        if (xval in range(int(round(self.button_rect.left)), int(round(self.button_rect.right))) and yval in range(int(round(self.pos[1])), int(round(self.button_rect.bottom)))):
            return self.callback() if self.callback else True #if no callback is provided, use this as a collider so the main program can handle it
        else:
            return False

class TextInput(GUIbaseClass):
    def __init__(self,pos,text, _user_text=None, _current_userinp_index=None):
        super().__init__() #init above GUIbaseClass
        self.pos = pos
        self.raw_text = text
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
            

        
    #this might be right?
    def display(self,dis:pygame.Surface):
        self.display_window(dis)
        
        self.confirm_button._NSdis(dis)
        
        for _ in range(len(self.text_inputs)):
            self.text_inputs[_].display(dis)


    
    #determine text input boxes properly through a class, initialized through a property
    #yeah yeah i know

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





class Drawing(GUIobj): #this one will be harder, I'll have to really think about how to implement this.
    def __init__(self,):
        pass

class menu(GUIobj): # i wonder... will setting window size to 1080p remove any need to descale?
    def __init__(self, window_dropdowns:typing.List[Dropdown]): #maybe just add dropdowns as a param?
        self.content = [] #fill with columns/rows
        super().__init__([0,0],(1920,1080))
        self.clickable_cross.callback = CLOSE
        #we don't need a custom closebutton, this comes included... we just provide it with a different callback

        self.dropdowns = window_dropdowns
    
    def move_window(self, mousepos):
        #return super().move_window(mousepos) <- this is overrided as the menu window should ideally not be moved around! 
        pass
    
    def display_window(self,dis): #override GUIobj display window for extra functionality
        super().display_window(dis)
        for dropdown in self.dropdowns:
            dropdown.display(dis)
        
#make more generalised `window` class for easier use of GUIobj, abstracting more from the end-user (working with GUIobj isn't ideal)

class window(GUIobj):
    ... #here!
    
    
    
    
    
#HANDLER

class Handler:
    def __init__(self):
        self.GUIobjs_array = []
        self.wecheck = False
        self.previously_moved = 0
        self.moved_in_cycle = False
    
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


    
    def display(self,dis):
        dis.fill((255,255,255))
        for i in range(len(self.GUIobjs_array),0,-1):
            self.GUIobjs_array[i-1].display(dis) if isinstance(self.GUIobjs_array[i-1],TextInputBox) else self.GUIobjs_array[i-1].display_window(dis)
        
        
    def handle_event(self,event,x,y):
        
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            
            
            elif event.key == pygame.K_BACKSPACE:
                if len(self.GUIobjs_array)>0 and isinstance(self.GUIobjs_array[0],TextInputBox):
                    for t_input in self.GUIobjs_array[0].text_inputs:
                        if t_input.to_input:
                            t_input.backspace()
                self.__recursive_displayobj_texthandling(self.GUIobjs_array[0],"absolutely nothing",True)
                        
            else:
                self.addTIBtext(event.unicode)

                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            

            if len(self.GUIobjs_array) > 0 and self.GUIobjs_array[0].check_closebuttoncollide(x,y):
                self.GUIobjs_array.pop(0)
            
            else:
                for d in range(len(self.GUIobjs_array)):
                    if d==0:
                        if isinstance(self.GUIobjs_array[d], TextInputBox):
                            self.GUIobjs_array[d].on_collide(x,y)
                        elif isinstance(self.GUIobjs_array[0],GUIobj):
                            self.__recursive_displayobj_onclick(self.GUIobjs_array[0],x,y)
                            
                    else:
                        if isinstance(self.GUIobjs_array[0],TextInputBox):
                            for t_input in self.GUIobjs_array[d].text_inputs:
                                t_input.to_input = False
                        
                self.wecheck = True #check for collisions in this cycle
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.wecheck = False
        
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
                    
        for contentblock in self.GUIobjs_array:
                
            if contentblock.check_closebuttoncollide(x,y):
            
                contentblock.clickable_cross.highlighted = True
            else:
                contentblock.clickable_cross.highlighted = False
            
    
       
        
    def addTIBtext(self,unicode):
        
        if len(self.GUIobjs_array) > 0 and isinstance(self.GUIobjs_array[0],TextInputBox):
            for t_input in self.GUIobjs_array[0].text_inputs:
                if t_input.to_input:    
                    t_input.add_char(unicode)
                    
        elif len(self.GUIobjs_array) > 0 and hasattr(self.GUIobjs_array[0], "content"):
            for contentblock in self.GUIobjs_array[0].content:
                self.__recursive_displayobj_texthandling(contentblock,unicode)
                