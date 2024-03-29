'''
note for anybody who reads the following test file,

this is NOT a clean and optimised test by any long shot, simply just an attempt at putting things together without writing directly to run_3d.py (that would take way too long to test)
I apologize for the horrid algorithms used here - I promise I'll write a cleaner implementation in run_3d.py

'''

import pygame
from utils import pgui

def create_random_textbox_for_the_funsies():
    tb1 = pgui.TextInput([0,0],"hi")
    tb2 = pgui.TextInput([0,0],"hi2")
    tib1 = pgui.TextInputBox([50,100],[600,500],[tb1,tb2],"this is a demo")
    return tib1

darr = []
pygame.init()
x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])

print(pygame.display.get_desktop_sizes()[0])

wecheck = False
tb1 = pgui.TextInput([0,0],"hi")
tb2 = pgui.TextInput([0,0],"hi2")
tib1 = pgui.TextInputBox([50,100],[600,500],[tb1,tb2],"this is a demo")
darr.append(tib1)
previously_moved = 0


while 1: #main loop
    dis.fill((255,255,255))
    for i in range(len(darr),0,-1):
        darr[i-1].display(dis)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            elif event.key == pygame.K_BACKSPACE:
                if len(darr)>0:
                    for t_input in darr[0].text_inputs:
                        if t_input.to_input:
                            t_input.backspace()
                
            
            
            elif event.key == pygame.K_DELETE: #changed to del because my silly little 75% keyboard doesn't have an insert key!
                darr.append(create_random_textbox_for_the_funsies())
            else:
                if len(darr) > 0:
                    for t_input in darr[0].text_inputs:
                        if t_input.to_input:    
                            t_input.add_char(event.unicode)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            

            if len(darr) > 0 and darr[0].check_closebuttoncollide(x,y):
                darr.pop(0)
            
            else:
                for d in range(len(darr)):
                    if d==0:
                        darr[d].on_collide(x,y)
                    else:
                        for t_input in darr[d].text_inputs:
                            t_input.to_input = False
                wecheck = True #check for collisions in this cycle
        
        elif event.type == pygame.MOUSEBUTTONUP:
            wecheck = False
        
        moved_in_cycle = False
        if len(darr) > 1 and previously_moved != 0:
            darr[0], darr[previously_moved] = darr[previously_moved], darr[0]
            previously_moved = 0
        
        
        for tib in darr:
            if wecheck and tib.check_windowcollide(x,y) and (not darr[0].check_objcollide(x,y) if darr.index(tib) != 0 else True):
                if not moved_in_cycle:
                    
                    newx, newy = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                    tib.move_window([tib.pos[0]+(newx-x),tib.pos[1]+(newy-y)]) #there's a hilarious logic problem here where you can merge windows by dragging them around, so we'll have to track one movement per cycle
                    moved_in_cycle = True
                    previously_moved = darr.index(tib) # this is getting sketchy now, i'm smelling a big rewrite for optimisation in the future!

                
        if len(darr) > 0:    
            if darr[0].check_closebuttoncollide(x,y):
            
                darr[0].clickable_cross.highlighted = True
            else:
                darr[0].clickable_cross.highlighted = False
            
    x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]

    pygame.display.flip()
    
    