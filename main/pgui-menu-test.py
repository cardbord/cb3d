
import pygame
from utils.pgui import menu as m, Dropdown, Button, scale_to_window


pygame.init()
x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])

print(pygame.display.get_desktop_sizes()[0])

File = Dropdown([0,0], Button([0,0],"File",[200,50],(10,10,10)), [ Button([0,0],"demo1",[200,50]),Button([0,0],"demo2",[200,50]),Button([0,0],"demo3",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50],None,lambda: print("works")), ] )#place button list in sq brackets
Help = Dropdown([scale_to_window(200),0], Button([scale_to_window(200),0],"Help",[200,50],(10,10,10)), [ Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]),Button([0,0],"demo",[200,50]), ] ) 

menu = m([File,Help])


while 1: #main loop
     dis.fill((255,255,255))
     
     
     
     for event in pygame.event.get():
          if event.type == pygame.QUIT:
               pygame.quit()
               quit()
          elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
               
                    
          elif event.type == pygame.MOUSEBUTTONDOWN:
               if menu.check_windowcollide(x,y):
                    
                    for dropdown in menu.dropdowns:
                         dropdown.on_click(x,y)
                    
                         
                    menu.clickable_cross.on_click(x,y)
               
               
               for dropdown in menu.dropdowns:
                    if dropdown.is_dropped:
                         for button in dropdown.buttons:
                              button.on_click(x,y)

               
                    
          elif event.type == pygame.MOUSEBUTTONUP:
               pass
          
     menu.display_window(dis)


     if menu.check_closebuttoncollide(x,y):
          menu.clickable_cross.highlighted = True
     else:
          menu.clickable_cross.highlighted = False

     
               

     x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]

     pygame.display.flip()