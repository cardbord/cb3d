
import pygame
from utils import pgui


pygame.init()
x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])

print(pygame.display.get_desktop_sizes()[0])

menu =  pgui.menu()


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
                    if menu.File.checkcollide(x,y):
                         menu.File.is_dropped = not menu.File.is_dropped
                    if menu.Help.checkcollide(x,y):
                         menu.Help.is_dropped = not menu.Help.is_dropped
                         
                    menu.clickable_cross.on_click(x,y)

               if menu.File.is_dropped:
                    for button in menu.File.buttons:
                         button.on_click(x,y)
               elif menu.Help.is_dropped:
                    for button in menu.Help.buttons:
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