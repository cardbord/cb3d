import pygame #do we make enum class for types at some point? #no, are you stupid? - future me
from pygame.font import get_default_font, Font
import typing
from math import sqrt, ceil

pygame.font.init()

def calc_rel_size() -> typing.Union[float,None]: #requies a running pyame display instance, errors if not initialized
    if not pygame.get_init():
        raise RuntimeError("No pygame display instance. Please use pygame.init() before running calc_rel_size()")
    else:
        winsize = pygame.display.get_desktop_sizes()[0]
        return round(sqrt((winsize[0]*winsize[1]))/1440,3)  #returns size scale factor
    
def scale_to_window(value:typing.Union[int,float]) -> float:
    return calc_rel_size() * value


def CLOSE():
    if pygame.get_init():
        pygame.quit()
    exit()



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


class DisplayColumn(GUIbaseClass):
    def __init__(self,
        parent_pos,
        parent_window_size,
        objs
    ):
        super().__init__()
        self.content = objs
        

    def _calc_obj_rel_pos(self,displace_height):
        #justify position relative to the rest of the window, then calculate the position of everything else
        for item in self.content:
            pass #i'm not sure how i'll manage this, maybe some sort of clever spacing?



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
        
    

    def display_window(self,dis:pygame.Surface):
        pygame.draw.rect(dis,(255,255,255),self.parent_window_rect)
        pygame.draw.rect(dis,(255,255,255),self.clickableborder_area)
        pygame.draw.rect(dis,(0,0,0),self.parent_window_rect,width=1)
        pygame.draw.rect(dis,(0,0,0),self.clickableborder_area,width=1)
        if self.title != None:
            trect = self.font.render(self.title,True,(0,0,0))
            dis.blit(trect,[(self.pos[0]+20*self._SIZE_SF), (self.pos[1]+5*self._SIZE_SF)])
        for display_obj in self.content:
            for content_obj in display_obj.content:
                content_obj.display() 
        
        self.clickable_cross.display(dis)

    def check_windowcollide(self,xval,yval):
        return True if (xval in range(self.pos[0], int(round(self.pos[0]+self.clickableborder_pos[0]))) and yval in range(self.pos[1], int(round(self.pos[1]+self.clickableborder_pos[1])))) else False

    def check_objcollide(self,xval,yval):
        return True if (xval in range(self.pos[0], int(round(self.pos[0]+self.window_size[0]))) and yval in range(self.pos[1], int(round(self.pos[1]+self.window_size[1])))) else False

    def check_closebuttoncollide(self,xval,yval):
        return True if (xval in range(int(round(self.clickable_cross.button_rect.left)), int(round(self.clickable_cross.button_rect.right))) and yval in range(int(round(self.clickable_cross.pos[1])), int(round(self.clickable_cross.button_rect.bottom)))) else False

class Button(GUIbaseClass):
    def __init__(self,pos,text_overlay,window_size:list = None,colourvalue:tuple=None,callback=None): #if no window_size, we approximate with text_overlay (mainly used for guiobj x button)
        super().__init__()
        self.pos = pos
        self.text_overlay = text_overlay
        self.text = self.font.render(self.text_overlay,True,(0,0,0))
        self.text_box_width = max(42*self._SIZE_SF,self.text.get_width()*self._SIZE_SF*7) if not window_size else window_size[0] * self._SIZE_SF
        self.text_box_height = (self.font.get_height()+4)*self._SIZE_SF if not window_size else window_size[1] * self._SIZE_SF
        self.highlighted_colour = colourvalue if colourvalue else (0,0,0)
        self.button_rect = pygame.Rect(self.pos[0],self.pos[1],self.text_box_width ,self.text_box_height)
        self.highlighted = False #we change this at some point in the main program to highlight with our selected colour, just by doing ```Button.highlighted = True; Button.display(dis)```
        self.callback = callback #function to execute once button is clicked


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
    def __init__(self,pos,text):
        super().__init__()
        self.pos = pos
        self.raw_text = text
        self.text = self.font.render(text,True,(0,0,0))
        self.to_input = False
        __s = self.text.get_size()
        self.text_box_width = __s[0]
        self.text_box_height = __s[1]
        self.text_rect = pygame.Rect(self.pos[0],self.pos[1],self.text_box_width,self.text_box_height)
        
        self.user_text = ""
        #render within display method
        self.user_text_width = max(200*self._SIZE_SF,self.font.size(self.user_text)[0])
        self.user_text_rect = pygame.Rect(self.pos[0]+self.text_box_width+10*self._SIZE_SF,self.pos[1],self.user_text_width,__s[1])
        
        
        
        
    def display(self,dis:pygame.Surface):
        dis.blit(self.text,(self.pos))
        pygame.draw.rect(dis,(0,0,0),self.user_text_rect,width=1)
        render_text = self.font.render(self.user_text,True,(90,90,90))
        dis.blit(render_text,self.user_text_rect.topleft)

    def update_text(self,text:str): #change to use user_text instead of raw_text. raw_text is actually pretty useless.
        self.user_text = text
        self.user_text_width = max(200*self._SIZE_SF,self.font.size(text)[0])
        self.user_text_rect.w = self.user_text_width



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
                                     [(self.__s[0]/self._SIZE_SF),self.__s[1]/self._SIZE_SF])
        for t_input in range(len(self.text_inputs)):
            self.text_inputs[t_input].pos[1] = self.pos[1] + (self.__GUIobjWinTop_Displacement) + 60*self._SIZE_SF*t_input #adjust distance dependent multiple of font size (figure out later)
            self.text_inputs[t_input].pos[0] = (self.pos[0] + 10*self._SIZE_SF)

            self.text_inputs[t_input].text_rect.y = self.text_inputs[t_input].pos[1]
            self.text_inputs[t_input].text_rect.x = self.text_inputs[t_input].pos[0]
            
            self.text_inputs[t_input].user_text_rect.y = self.text_inputs[t_input].pos[1]
            self.text_inputs[t_input].user_text_rect.x = self.text_inputs[t_input].pos[0] + self.text_inputs[t_input].text_rect.width + 20*self._SIZE_SF
            
            
        
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