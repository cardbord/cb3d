import pygame #do we make enum class for types at some point?
from pygame.font import get_default_font, Font
import typing

pygame.font.init()

class GUIbaseClass: #provide attrs for other junk, because these things are included in everything
    def __init__(self):
        self.window_size = pygame.display.get_desktop_sizes()[0]        
        self._SIZE_SF = round((self.window_size[0]*self.window_size[1])/2073600,1) #factor for monitor size, 1920x1080p default
        self.font = Font(get_default_font(),int(round(12*self._SIZE_SF)))

class GUIobj(GUIbaseClass):
    def __init__(self,pos,window_size):
        super.__init__()
        # change size sf for monitor size
        self.pos = pos #stored as raw coords
        self.window_size = window_size #stored as width/height
        self.border_colour = (0,0,0)
        self.clickableborder_pos = [pos[0]+self.window_size[0],self.pos[1]+self._SIZE_SF*20] #stored as width/height, syntax to check would be ``` if x in range(self.pos[0],self.clickableborder_pos[1]) ```
        #define other attrs in subclasses

    def move_window(self,mousepos): #should be called when a mouse click is detected on the window's clickable border, to change pos
        self.pos = mousepos
        self.clickableborder_pos = [self.pos[0]+self.window_size[0],self.pos[1]+self._SIZE_SF*20]
        #render updates should change automatically from this, maybe?


class Button(GUIbaseClass):
    def __init__(self,pos,text_overlay,size_sf):
        super.__init__()
        self.pos = pos
        self.text_overlay = text_overlay
        self._SIZE_SF = size_sf
        self.text = self.font.render(self.text_overlay)
        self.text_box_width = max(42*self._SIZE_SF,self.text.get_width()*self._SIZE_SF)
        self.text_box_height = (self.font.get_height()+4)*self._SIZE_SF

    @property
    def button_rect(self):
        return pygame.Rect(self.pos[0],self.pos[1],self.text_box_width,self.text_box_width)
    
    def display(self,surface):
        with surface as dis:
            dis.blit(self.text,(self.text_box_width,self.text_box_height))
            dis.blit(self.button_rect,self.pos)
            
class TextInput(GUIbaseClass):
    def __init__(self,pos,text):
        self.pos = pos
        self.raw_text = text
        self.text = self.font.render(text,True,(0,0,0))
        self.to_input = False
        self.text_box_width = max(42*self._SIZE_SF,self.text.get_width()*self._SIZE_SF)
        self.text_box_height = (self.font.get_height()+4)*self._SIZE_SF
        
    
    @property
    def text_input_rect(self):
        return pygame.Rect(self.pos[0],self.pos[1],self.text_box_width,self.text_box_width)
        
    def display(self,surface):
        with surface as dis:
            dis.blit(self.text,(self.pos))
    
    def update(self,text):
        self.raw_text = text
        self.text = self.font.render(text,True,(0,0,0))
        self.text_box_width = max(42*self._SIZE_SF,self.text.get_width()*self.text_box_width)
        
            
    
class TextInputBox(GUIobj):
    def __init__(self,pos,window_size,text_inputs:typing.List[TextInput]):
        self.text_inputs = text_inputs
        super.__init__(pos,window_size)
    

        
    #determine text input boxes properly through a class, initialized through a property
    
class Drawing(GUIobj): #this one will be harder, I'll have to really think about how to implement this.
    def __init__(self):
        pass