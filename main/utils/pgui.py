import pygame #do we make enum class for types at some point? #no, are you stupid? - future me
from pygame.font import get_default_font, Font
import typing
from math import sqrt

pygame.font.init()

class GUIbaseClass: #provide attrs for other junk, because these things are included in everything
    def __init__(self):
        self.window_size = pygame.display.get_desktop_sizes()[0]        
        self._SIZE_SF = round(sqrt((self.window_size[0]*self.window_size[1]))/1440,1) #factor for monitor size, 1920x1080p default
        self.font = Font(get_default_font(),int(round(50*self._SIZE_SF)))

class GUIobj(GUIbaseClass):
    def __init__(self,pos,window_size):
        super().__init__()
        # change size sf for monitor size
        self.pos = pos #stored as raw coords
        self.window_size = [window_size[0]*self._SIZE_SF, window_size[1] * self._SIZE_SF] #stored as width/height
        self.border_colour = (0,0,0)
        self.clickableborder_pos = [self.window_size[0],50*self._SIZE_SF] #stored as width/height, syntax to check would be ``` if x in range(self.pos[0],self.clickableborder_pos[1]) ```
        self.parent_window_rect = pygame.Rect(self.pos[0],self.pos[1],self.window_size[0],self.window_size[1])
        self.clickableborder_area = pygame.Rect(self.pos[0],self.pos[1],self.clickableborder_pos[0],self.clickableborder_pos[1])
        self.clickable_cross = Button([self.pos[0]+self.clickableborder_pos[0]-50*self._SIZE_SF,self.pos[1]],"×",[50,50],(255,0,0)) # window size is corrected to _SIZE_SF automatically in Button.__init__()!
        #define other attrs in subclasses
        
    def move_window(self,mousepos): #should be called when a mouse click is detected on the window's clickable border, to change pos
        self.pos = mousepos
        self.clickableborder_pos = [self.window_size[0],50*self._SIZE_SF] #size sf is a pain with this one, it might not move the window properly
        self.clickableborder_area = pygame.Rect(self.pos[0],self.pos[1],self.clickableborder_pos[0],self.clickableborder_pos[1])
        self.parent_window_rect = pygame.Rect(self.pos[0],self.pos[1],self.window_size[0],self.window_size[1])
        self.clickable_cross = Button([self.pos[0]+self.clickableborder_pos[0]-50*self._SIZE_SF,self.pos[1]],"×",[50,50],(255,0,0)) #too many attributes to change in the old one, let's just make a new button with our updated pos and clickable border
        #render updates should change automatically from this, maybe?
        
    

    def display_window(self,dis:pygame.Surface):
        pygame.draw.rect(dis,(255,255,255),self.parent_window_rect)
        pygame.draw.rect(dis,(255,255,255),self.clickableborder_area)
        pygame.draw.rect(dis,(0,0,0),self.parent_window_rect,width=1)
        pygame.draw.rect(dis,(0,0,0),self.clickableborder_area,width=1)
        
        
        self.clickable_cross.display(dis)

    def check_windowcollide(self,xval,yval):
        return True if (xval in range(self.pos[0], int(round(self.pos[0]+self.clickableborder_pos[0]))) and yval in range(self.pos[1], int(round(self.pos[1]+self.clickableborder_pos[1])))) else False

    def check_closebuttoncollide(self,xval,yval):
        return True if (xval in range(int(round(self.clickable_cross.button_rect.left)), int(round(self.clickable_cross.button_rect.right))) and yval in range(int(round(self.clickable_cross.pos[1])), int(round(self.clickable_cross.button_rect.bottom)))) else False

class Button(GUIbaseClass):
    def __init__(self,pos,text_overlay,window_size:list = None,colourvalue:tuple=None): #if no window_size, we approximate with text_overlay (mainly used for guiobj x button)
        super().__init__()
        self.pos = pos
        self.text_overlay = text_overlay
        self.text = self.font.render(self.text_overlay,True,(0,0,0))
        self.text_box_width = max(42*self._SIZE_SF,self.text.get_width()*self._SIZE_SF*7) if not window_size else window_size[0] * self._SIZE_SF
        self.text_box_height = (self.font.get_height()+4)*self._SIZE_SF if not window_size else window_size[1] * self._SIZE_SF
        self.highlighted_colour = colourvalue if colourvalue else (0,0,0)
        self.button_rect = pygame.Rect(self.pos[0],self.pos[1],self.text_box_width ,self.text_box_height)
        self.highlighted = False #we change this at some point in the main program to highlight with our selected colour, just by doing ```Button.highlighted = True; Button.display(dis)```
    
    def display(self,dis:pygame.Surface):
        pygame.draw.rect(dis,(0,0,0) if not self.highlighted else self.highlighted_colour,self.button_rect,1 if not self.highlighted else 0)
        dis.blit(self.text,(self.pos[0]+11*self._SIZE_SF,self.pos[1]-3*self._SIZE_SF))


class TextInput(GUIbaseClass):
    def __init__(self,pos,text):
        super().__init__()
        self.pos = pos
        self.raw_text = text
        self.text = self.font.render(text,True,(0,0,0))
        self.to_input = False
        self.text_box_width = max(300*self._SIZE_SF,self.text.get_width()*self._SIZE_SF*len(text))
        self.text_box_height = (self.font.get_height()+4)*self._SIZE_SF
        
    
    @property
    def text_input_rect(self):
        return pygame.Rect(self.pos[0],self.pos[1],self.text_box_width,self.text_box_width)
        
    def display(self,dis:pygame.Surface):
        dis.blit(self.text,(self.pos))
    
    def update(self,text):
        self.raw_text = text
        self.text = self.font.render(text,True,(0,0,0))
        self.text_box_width = max(100*self._SIZE_SF,self.text.get_width()*self.text_box_width)



class TextInputBox(GUIobj):
    def __init__(self,pos,window_size,text_inputs:typing.List[TextInput]):
        self.text_inputs = text_inputs
        super().__init__(pos,window_size)
        self.height = len(self.text_inputs) * self.text_inputs[0].text_box_height + 60*self._SIZE_SF
        self.width = max(i.text_box_width for i in text_inputs) * len(self.text_inputs)
        self.confirm_button = Button(pos=[self.pos[0]+(window_size[0]-24)*self._SIZE_SF, self.pos[1]+(window_size[1]-self.text_inputs[0].font.get_height())*self._SIZE_SF],text_overlay="Confirm")

        
    @property
    def dis_rect(self):
        return pygame.Rect(self.pos[0],self.pos[1],self.width,self.height)



    #this might be right?
    def display(self,dis:pygame.Surface):
        self.display_window()
        
        
        for _ in range(len(self.text_inputs)):
            input_table = self.text_inputs[_]
            input_table.pos[1] += _*self._SIZE_SF #how do we handle this??!?!?!?!?!?!1?
            input_table.display(dis) #we need to init position again, as the original is it's own, but we're in an array here.
        


    
    #determine text input boxes properly through a class, initialized through a property
    #yeah yeah i know
    
class Drawing(GUIobj): #this one will be harder, I'll have to really think about how to implement this.
    def __init__(self,):
        pass